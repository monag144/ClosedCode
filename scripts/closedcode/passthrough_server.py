#!/usr/bin/env python3
"""ClosedCode loopback provider passthrough.

Owns NVIDIA/Z.AI HTTP forwarding outside OpenCode's compiled agent graph.
Provider API keys remain in Termux's OpenCode auth store and are never
returned by this service.
"""
from __future__ import annotations

import argparse
from datetime import timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import os
import stat
import subprocess
import shutil
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import parse_qs, urlparse

VERSION = "0.8.19"
MAX_BODY = 2 * 1024 * 1024
DEFAULT_AUTH_PATH = Path.home() / ".local" / "share" / "opencode" / "auth.json"
DEFAULT_HISTORY_ROOT = Path.home() / ".local" / "share" / "closedcode" / "passthrough-history"
MAX_HISTORY_MESSAGES = 500
MAX_STEERING_CHARS = 12000
PROVIDERS = {
    "nvidia": {
        "env": "CLOSEDCODE_NVIDIA_BASE_URL",
        "default_base": "https://integrate.api.nvidia.com/v1",
    },
    "zai": {
        "env": "CLOSEDCODE_ZAI_BASE_URL",
        "default_base": "https://api.z.ai/api/paas/v4",
    },
}

ACTIVE_STREAMS_LOCK = threading.Lock()
ACTIVE_STREAMS = {}
HISTORY_LOCK = threading.RLock()

ACTIVE_PERMISSIONS_LOCK = threading.Lock()
ACTIVE_PERMISSIONS = {}
AGENT_APPROVAL_TOOLS = {"workspace_write", "workspace_patch", "workspace_mkdir", "workspace_move", "workspace_delete", "shell"}
YOLO_AUTO_APPROVAL_TOOLS = {"workspace_write", "workspace_patch", "workspace_mkdir", "workspace_move", "workspace_delete"}


def validate_request_id(value):
    if not isinstance(value, str) or not value or len(value) > 256:
        raise ValueError("invalid requestID")
    return value


def active_stream_register(request_id: str, upstream, session_id: str | None = None):
    if session_id is not None:
        history_path(session_id)
    with ACTIVE_STREAMS_LOCK:
        if request_id in ACTIVE_STREAMS:
            raise ValueError("requestID already active")
        ACTIVE_STREAMS[request_id] = {"upstream": upstream, "cancelled": False, "steering": [], "sessionID": session_id}


def active_stream_cancel(request_id: str) -> bool:
    validate_request_id(request_id)
    with ACTIVE_STREAMS_LOCK:
        entry = ACTIVE_STREAMS.get(request_id)
        if not entry:
            return False
        entry["cancelled"] = True
        upstream = entry.get("upstream")
    try:
        if upstream is not None:
            upstream.close()
    except Exception:
        pass
    with ACTIVE_PERMISSIONS_LOCK:
        waiting = [
            permission["event"]
            for permission in ACTIVE_PERMISSIONS.values()
            if permission.get("requestID") == request_id
        ]
    for event in waiting:
        event.set()
    return True


def active_stream_cancelled(request_id: str) -> bool:
    with ACTIVE_STREAMS_LOCK:
        entry = ACTIVE_STREAMS.get(request_id)
        return bool(entry and entry.get("cancelled"))


def active_stream_unregister(request_id: str):
    with ACTIVE_STREAMS_LOCK:
        ACTIVE_STREAMS.pop(request_id, None)


def active_stream_set_upstream(request_id: str, upstream):
    with ACTIVE_STREAMS_LOCK:
        entry = ACTIVE_STREAMS.get(request_id)
        if entry is not None:
            entry["upstream"] = upstream


def active_stream_steer(request_id: str, text: str) -> bool:
    validate_request_id(request_id)
    if not isinstance(text, str):
        raise ValueError("steering text must be text")
    text = text.strip()
    if not text:
        raise ValueError("steering text is required")
    if len(text) > MAX_STEERING_CHARS:
        raise ValueError("steering text exceeds length limit")
    with ACTIVE_STREAMS_LOCK:
        entry = ACTIVE_STREAMS.get(request_id)
        if not entry or entry.get("cancelled"):
            return False
        session_id = entry.get("sessionID")
        if not session_id:
            return False
        persist_messages(session_id, [{"role": "user", "content": text}])
        entry.setdefault("steering", []).append(text)
    return True


def active_stream_take_steering(request_id: str) -> list[str]:
    with ACTIVE_STREAMS_LOCK:
        entry = ACTIVE_STREAMS.get(request_id)
        if not entry:
            return []
        steering = list(entry.get("steering") or [])
        entry["steering"] = []
    return steering


def agent_permission_id(request_id: str, call_id: str, round_index: int) -> str:
    raw = f"{request_id}:{call_id}:{round_index}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]


def agent_permission_register(permission_id: str, request_id: str):
    event = threading.Event()
    with ACTIVE_PERMISSIONS_LOCK:
        ACTIVE_PERMISSIONS[permission_id] = {
            "requestID": request_id,
            "event": event,
            "decision": None,
        }
    return event


def agent_permission_resolve(permission_id: str, request_id: str, decision: str) -> bool:
    if decision not in {"allow", "reject"}:
        raise ValueError("decision must be allow or reject")
    with ACTIVE_PERMISSIONS_LOCK:
        entry = ACTIVE_PERMISSIONS.get(permission_id)
        if not entry or entry.get("requestID") != request_id:
            return False
        entry["decision"] = decision
        event = entry["event"]
    event.set()
    return True


def agent_permission_wait(permission_id: str, request_id: str, timeout_seconds: int = 600):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if active_stream_cancelled(request_id):
            return "cancelled"
        with ACTIVE_PERMISSIONS_LOCK:
            entry = ACTIVE_PERMISSIONS.get(permission_id)
            if not entry:
                return "reject"
            decision = entry.get("decision")
            event = entry["event"]
        if decision in {"allow", "reject"}:
            return decision
        event.wait(timeout=min(0.25, max(0.0, deadline - time.monotonic())))
    return "reject"


def agent_permission_unregister(permission_id: str):
    with ACTIVE_PERMISSIONS_LOCK:
        ACTIVE_PERMISSIONS.pop(permission_id, None)


RETRYABLE_PROVIDER_STATUS = {429, 500, 502, 503, 504}
PROVIDER_MAX_ATTEMPTS = 8
PROVIDER_RETRY_AFTER_CAP_SECONDS = 30.0
PROVIDER_RATE_LIMIT_BASE_DELAY_SECONDS = 4.0
ZAI_MIN_AGENT_ROUND_INTERVAL_SECONDS = 20.0
PROVIDER_TRANSIENT_BASE_DELAY_SECONDS = 0.75
PROVIDER_TRANSIENT_DELAY_CAP_SECONDS = 6.0
PROVIDER_TRANSPORT_REASON_MAX_CHARS = 240


def provider_transport_error_message(exc: Exception) -> str:
    reason = getattr(exc, "reason", None)
    detail = str(reason if reason is not None else exc).strip()
    detail = " ".join(detail.split())
    if detail:
        detail = detail[:PROVIDER_TRANSPORT_REASON_MAX_CHARS]
        return "provider transport error: " + exc.__class__.__name__ + ": " + detail
    return "provider transport error: " + exc.__class__.__name__


def provider_retry_after_seconds(headers) -> float | None:
    if headers is None:
        return None
    try:
        value = headers.get("Retry-After")
    except Exception:
        return None
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    try:
        seconds = float(raw)
    except ValueError:
        try:
            when = parsedate_to_datetime(raw)
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            seconds = when.timestamp() - time.time()
        except Exception:
            return None
    return max(0.0, min(PROVIDER_RETRY_AFTER_CAP_SECONDS, seconds))


def provider_retry_delay(status: int | None, attempt: int, headers=None) -> float:
    attempt = max(1, attempt)
    if status == 429:
        retry_after = provider_retry_after_seconds(headers)
        if retry_after is not None:
            return retry_after
        return min(PROVIDER_RETRY_AFTER_CAP_SECONDS, PROVIDER_RATE_LIMIT_BASE_DELAY_SECONDS * (2 ** (attempt - 1)))
    return min(PROVIDER_TRANSIENT_DELAY_CAP_SECONDS, PROVIDER_TRANSIENT_BASE_DELAY_SECONDS * (2 ** (attempt - 1)))


def wait_with_cancel(request_id: str, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if active_stream_cancelled(request_id):
            return False
        time.sleep(min(0.1, max(0.0, deadline - time.monotonic())))
    return not active_stream_cancelled(request_id)


def agent_provider_token_usage(response: dict):
    if not isinstance(response, dict) or not isinstance(response.get("usage"), dict):
        return None
    usage = response["usage"]
    def read(*keys):
        for key in keys:
            value = usage.get(key)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                return value
        return None
    prompt = read("prompt_tokens", "input_tokens", "promptTokens", "inputTokens")
    completion = read("completion_tokens", "output_tokens", "completionTokens", "outputTokens")
    total = read("total_tokens", "totalTokens")
    if total is None and prompt is not None and completion is not None:
        total = prompt + completion
    if prompt is None and completion is None and total is None:
        return None
    return {"promptTokens": prompt, "completionTokens": completion, "totalTokens": total}

def agent_provider_completion(provider_id: str, upstream_url: str, key: str, payload: dict, request_id: str) -> dict:
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    last_error = "provider request failed"
    for attempt in range(1, PROVIDER_MAX_ATTEMPTS + 1):
        if active_stream_cancelled(request_id):
            raise RuntimeError("provider request cancelled")
        retry_status = None
        retry_headers = None
        retryable = False
        req = urlrequest.Request(upstream_url, data=encoded, method="POST", headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "ClosedCode-Agent/" + VERSION})
        try:
            upstream = urlrequest.urlopen(req, timeout=180)
            active_stream_set_upstream(request_id, upstream)
            with upstream:
                body = upstream.read()
                status = getattr(upstream, "status", 200)
                retry_headers = getattr(upstream, "headers", None)
            active_stream_set_upstream(request_id, None)
            if status < 200 or status >= 300:
                last_error = "provider HTTP " + str(status)
                retryable = status in RETRYABLE_PROVIDER_STATUS
                retry_status = status
            else:
                return json.loads(body.decode("utf-8", errors="replace"))
        except urlerror.HTTPError as exc:
            active_stream_set_upstream(request_id, None)
            status = exc.code
            retry_status = status
            retry_headers = getattr(exc, "headers", None)
            try:
                exc.read(131072)
            except Exception:
                pass
            last_error = "provider HTTP " + str(status)
            retryable = status in RETRYABLE_PROVIDER_STATUS
        except (urlerror.URLError, TimeoutError, OSError) as exc:
            active_stream_set_upstream(request_id, None)
            last_error = provider_transport_error_message(exc)
            retryable = True
        if not retryable or attempt >= PROVIDER_MAX_ATTEMPTS:
            raise RuntimeError(last_error + " after " + str(attempt) + " attempt(s)")
        delay = provider_retry_delay(retry_status, attempt, retry_headers)
        if not wait_with_cancel(request_id, delay):
            raise RuntimeError("provider request cancelled")
    raise RuntimeError(last_error)


def agent_provider_stream_completion(provider_id: str, upstream_url: str, key: str, payload: dict, request_id: str) -> dict:
    stream_payload = dict(payload)
    stream_payload["stream"] = True
    encoded = json.dumps(stream_payload, separators=(",", ":")).encode("utf-8")
    last_error = "provider streaming request failed"
    for attempt in range(1, PROVIDER_MAX_ATTEMPTS + 1):
        if active_stream_cancelled(request_id):
            raise RuntimeError("provider request cancelled")
        retry_status = None
        retry_headers = None
        retryable = False
        req = urlrequest.Request(upstream_url, data=encoded, method="POST", headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "Accept": "text/event-stream", "User-Agent": "ClosedCode-Agent/" + VERSION})
        try:
            upstream = urlrequest.urlopen(req, timeout=180)
            active_stream_set_upstream(request_id, upstream)
            role = "assistant"
            content_parts = []
            reasoning_parts = []
            tool_slots = {}
            finish_reason = None
            usage = None
            with upstream:
                status = getattr(upstream, "status", 200)
                retry_headers = getattr(upstream, "headers", None)
                if status < 200 or status >= 300:
                    last_error = "provider HTTP " + str(status)
                    retryable = status in RETRYABLE_PROVIDER_STATUS
                    retry_status = status
                else:
                    while True:
                        if active_stream_cancelled(request_id):
                            raise RuntimeError("provider request cancelled")
                        line = upstream.readline()
                        if not line:
                            break
                        decoded = line.decode("utf-8", errors="replace").strip()
                        if not decoded.startswith("data:"):
                            continue
                        data = decoded[5:].strip()
                        if not data or data == "[DONE]":
                            if data == "[DONE]":
                                break
                            continue
                        event = json.loads(data)
                        if isinstance(event, dict) and isinstance(event.get("usage"), dict):
                            usage = event["usage"]
                        choices = event.get("choices") if isinstance(event, dict) else None
                        choice = choices[0] if isinstance(choices, list) and choices else {}
                        if not isinstance(choice, dict):
                            continue
                        if choice.get("finish_reason") is not None:
                            finish_reason = choice.get("finish_reason")
                        delta = choice.get("delta")
                        if not isinstance(delta, dict):
                            continue
                        if isinstance(delta.get("role"), str) and delta.get("role"):
                            role = delta["role"]
                        piece = delta.get("content")
                        if isinstance(piece, str) and piece:
                            content_parts.append(piece)
                        reasoning = delta.get("reasoning_content")
                        if isinstance(reasoning, str) and reasoning:
                            reasoning_parts.append(reasoning)
                        calls = delta.get("tool_calls")
                        if isinstance(calls, list):
                            for fallback_index, call in enumerate(calls):
                                if not isinstance(call, dict):
                                    continue
                                index = call.get("index")
                                if not isinstance(index, int):
                                    index = fallback_index
                                slot = tool_slots.setdefault(index, {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                                call_id = call.get("id")
                                if isinstance(call_id, str) and call_id:
                                    slot["id"] = call_id
                                call_type = call.get("type")
                                if isinstance(call_type, str) and call_type:
                                    slot["type"] = call_type
                                function = call.get("function")
                                if isinstance(function, dict):
                                    name = function.get("name")
                                    if isinstance(name, str) and name:
                                        slot["function"]["name"] += name
                                    arguments = function.get("arguments")
                                    if isinstance(arguments, str) and arguments:
                                        slot["function"]["arguments"] += arguments
                    active_stream_set_upstream(request_id, None)
                    message = {"role": role, "content": "".join(content_parts) if content_parts else None}
                    if reasoning_parts:
                        message["reasoning_content"] = "".join(reasoning_parts)
                    if tool_slots:
                        tool_calls = []
                        for index in sorted(tool_slots):
                            slot = tool_slots[index]
                            if not slot["id"]:
                                slot["id"] = "closedcode-stream-call-" + str(index)
                            tool_calls.append(slot)
                        message["tool_calls"] = tool_calls
                    result = {"choices": [{"index": 0, "message": message, "finish_reason": finish_reason}]}
                    if usage is not None:
                        result["usage"] = usage
                    return result
            active_stream_set_upstream(request_id, None)
        except urlerror.HTTPError as exc:
            active_stream_set_upstream(request_id, None)
            status = exc.code
            retry_status = status
            retry_headers = getattr(exc, "headers", None)
            try:
                exc.read(131072)
            except Exception:
                pass
            last_error = "provider HTTP " + str(status)
            retryable = status in RETRYABLE_PROVIDER_STATUS
        except (urlerror.URLError, TimeoutError, OSError) as exc:
            active_stream_set_upstream(request_id, None)
            last_error = provider_transport_error_message(exc)
            retryable = True
        if not retryable or attempt >= PROVIDER_MAX_ATTEMPTS:
            raise RuntimeError(last_error + " after " + str(attempt) + " attempt(s)")
        delay = provider_retry_delay(retry_status, attempt, retry_headers)
        if not wait_with_cancel(request_id, delay):
            raise RuntimeError("provider request cancelled")
    raise RuntimeError(last_error)


def auth_path() -> Path:
    return Path(os.environ.get("OPENCODE_AUTH_PATH", str(DEFAULT_AUTH_PATH))).expanduser()


def load_auth() -> dict:
    path = auth_path()
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise RuntimeError(f"auth file permissions are too broad: {oct(mode)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("auth store root is not an object")
    return data


def provider_key(provider_id: str) -> str:
    entry = load_auth().get(provider_id)
    if not isinstance(entry, dict):
        raise RuntimeError(f"provider auth is not configured: {provider_id}")
    if entry.get("type") != "api":
        raise RuntimeError(f"unsupported auth type for passthrough provider: {provider_id}")
    key = entry.get("key")
    if not isinstance(key, str) or not key:
        raise RuntimeError(f"provider API key is missing: {provider_id}")
    return key


def provider_base(provider_id: str) -> str:
    spec = PROVIDERS[provider_id]
    return os.environ.get(spec["env"], spec["default_base"]).rstrip("/")


def history_root() -> Path:
    return Path(
        os.environ.get("CLOSEDCODE_PASSTHROUGH_HISTORY", str(DEFAULT_HISTORY_ROOT))
    ).expanduser()


def history_path(session_id: str) -> Path:
    if not isinstance(session_id, str) or not session_id or len(session_id) > 512:
        raise ValueError("invalid sessionID")
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    return history_root() / f"{digest}.json"


def normalize_history_messages(messages) -> list[dict]:
    if not isinstance(messages, list):
        raise ValueError("messages must be an array")
    result = []
    for item in messages:
        if not isinstance(item, dict):
            raise ValueError("history message must be an object")
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant", "system"}:
            raise ValueError("invalid history role")
        if not isinstance(content, str):
            raise ValueError("history content must be text")
        result.append({"role": role, "content": content})
    return result


def load_history(session_id: str) -> list[dict]:
    path = history_path(session_id)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return normalize_history_messages(data)


def append_history(session_id: str, messages) -> list[dict]:
    incoming = normalize_history_messages(messages)
    history = (load_history(session_id) + incoming)[-MAX_HISTORY_MESSAGES:]
    root = history_root()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(root, 0o700)
    path = history_path(session_id)
    temp = path.with_suffix(".tmp")
    temp.write_text(
        json.dumps(history, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    os.chmod(temp, 0o600)
    os.replace(temp, path)
    return history


def timeline_path(sid):
    p=history_path(sid)
    return p.with_name(p.stem+".timeline.json")

def load_timeline(sid):
    p=timeline_path(sid)
    if not p.is_file(): return []
    v=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v,list): raise ValueError("invalid timeline")
    return v

def append_timeline(sid,items):
    if not isinstance(items,list) or not all(isinstance(q,dict) and q.get("kind") in {"message","tool"} for q in items):
        raise ValueError("invalid timeline")
    v=(load_timeline(sid)+items)[-MAX_HISTORY_MESSAGES*8:]
    root=history_root(); root.mkdir(parents=True,exist_ok=True,mode=0o700); os.chmod(root,0o700)
    p=timeline_path(sid); t=p.with_suffix(".tmp")
    t.write_text(json.dumps(v,ensure_ascii=False,separators=(",",":")),encoding="utf-8"); os.chmod(t,0o600); os.replace(t,p)
    return v

def persist_messages(session_id: str, messages) -> list[dict]:
    incoming = normalize_history_messages(messages)
    timeline = [{"kind": "message", "role": q["role"], "content": q["content"]} for q in incoming]
    with HISTORY_LOCK:
        stored = append_history(session_id, incoming)
        if timeline:
            append_timeline(session_id, timeline)
    return stored

def persist_timeline_items(session_id: str, items) -> list[dict]:
    with HISTORY_LOCK:
        return append_timeline(session_id, items)


MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_COMMAND_CHARS = 16384
MAX_COMMAND_OUTPUT_BYTES = 512 * 1024
MAX_COMMAND_TIMEOUT_SECONDS = 120
MAX_SEARCH_FILE_BYTES = 512 * 1024
SKIP_SEARCH_DIRS = {".git", ".gradle", "build", "node_modules", "__pycache__"}


def workspace_root(value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("root is required")
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("root must be an existing directory")
    return root


def workspace_path(root_value: str, path_value: str, allow_missing: bool = False, full_access: bool = False):
    root = workspace_root(root_value)
    if not isinstance(path_value, str) or not path_value or len(path_value) > 4096:
        raise ValueError("path is required")
    raw = Path(path_value).expanduser()
    target = (raw if raw.is_absolute() else root / raw).resolve(strict=False)
    if not full_access:
        try: target.relative_to(root)
        except ValueError: raise ValueError("path escapes workspace")
    if not allow_missing and not target.exists(): raise FileNotFoundError("path does not exist")
    return root, target


def workspace_rel(root: Path, target: Path) -> str:
    if target == root: return "."
    try: return target.relative_to(root).as_posix()
    except ValueError: return str(target)


AGENT_EMERGENCY_MAX_ROUNDS_DEFAULT = 4096
AGENT_EMERGENCY_MAX_ROUNDS_MIN = 128
AGENT_EMERGENCY_MAX_ROUNDS_MAX = 100000
AGENT_CONTEXT_COMPACT_AFTER_CHARS_DEFAULT = 280000
AGENT_CONTEXT_COMPACT_AFTER_CHARS_MIN = 65536
AGENT_CONTEXT_COMPACT_AFTER_CHARS_MAX = 4000000
AGENT_CONTEXT_KEEP_RECENT_MESSAGES = 48
AGENT_CONTEXT_EVIDENCE_LIMIT = 80
AGENT_CONTEXT_CHECKPOINT_PREFIX = "ClosedCode mission context checkpoint."
AGENT_CONTEXT_INSTRUCTIONS_JSON_HEADER = "Earlier user and steering instructions preserved verbatim JSON:\n"
AGENT_CONTEXT_INSTRUCTIONS_LEGACY_HEADER = "Earlier user and steering instructions preserved verbatim:\n"
AGENT_CONTEXT_EVIDENCE_HEADER = "\n\nEarlier execution evidence summary:"
AGENT_STAGNATION_REPEAT_THRESHOLD = 4
AGENT_STAGNATION_MAX_INTERVENTIONS = 3
AGENT_STAGNATION_RESET_AFTER_PRODUCTIVE_TOOLS = 12
AGENT_FINALIZATION_MAX_RETRIES = 3
AGENT_TOOL_RESULT_LIMIT = 128 * 1024


def agent_emergency_round_limit() -> int:
    raw = os.environ.get("CLOSEDCODE_AGENT_EMERGENCY_MAX_ROUNDS", "").strip()
    try:
        value = int(raw) if raw else AGENT_EMERGENCY_MAX_ROUNDS_DEFAULT
    except ValueError:
        value = AGENT_EMERGENCY_MAX_ROUNDS_DEFAULT
    return max(AGENT_EMERGENCY_MAX_ROUNDS_MIN, min(AGENT_EMERGENCY_MAX_ROUNDS_MAX, value))


def agent_context_compact_limit() -> int:
    raw = os.environ.get("CLOSEDCODE_AGENT_CONTEXT_COMPACT_AFTER_CHARS", "").strip()
    try:
        value = int(raw) if raw else AGENT_CONTEXT_COMPACT_AFTER_CHARS_DEFAULT
    except ValueError:
        value = AGENT_CONTEXT_COMPACT_AFTER_CHARS_DEFAULT
    return max(AGENT_CONTEXT_COMPACT_AFTER_CHARS_MIN, min(AGENT_CONTEXT_COMPACT_AFTER_CHARS_MAX, value))


def agent_context_chars(conversation) -> int:
    return len(json.dumps(conversation, ensure_ascii=False, separators=(",", ":")))


def agent_context_checkpoint_users(content) -> list[str]:
    if not isinstance(content, str) or not content.startswith(AGENT_CONTEXT_CHECKPOINT_PREFIX):
        return []
    if AGENT_CONTEXT_INSTRUCTIONS_JSON_HEADER in content:
        body = content.split(AGENT_CONTEXT_INSTRUCTIONS_JSON_HEADER, 1)[1]
        if AGENT_CONTEXT_EVIDENCE_HEADER in body:
            body = body.split(AGENT_CONTEXT_EVIDENCE_HEADER, 1)[0]
        try:
            values = json.loads(body)
        except json.JSONDecodeError:
            return []
        if not isinstance(values, list):
            return []
        return [value for value in values if isinstance(value, str) and value]
    if AGENT_CONTEXT_INSTRUCTIONS_LEGACY_HEADER in content:
        body = content.split(AGENT_CONTEXT_INSTRUCTIONS_LEGACY_HEADER, 1)[1]
        if AGENT_CONTEXT_EVIDENCE_HEADER in body:
            body = body.split(AGENT_CONTEXT_EVIDENCE_HEADER, 1)[0]
        return [value for value in body.split("\n---\n") if value]
    return []


def agent_compact_conversation(conversation):
    before = agent_context_chars(conversation)
    if before <= agent_context_compact_limit() or len(conversation) <= AGENT_CONTEXT_KEEP_RECENT_MESSAGES + 2:
        return conversation, None
    start = max(1, len(conversation) - AGENT_CONTEXT_KEEP_RECENT_MESSAGES)
    while start > 1 and conversation[start].get("role") == "tool":
        start -= 1
    if start <= 1:
        return conversation, None
    removed = conversation[1:start]
    users, evidence = [], []
    for item in removed:
        role = item.get("role")
        content = item.get("content")
        if role == "system":
            users.extend(agent_context_checkpoint_users(content))
        elif role == "user" and isinstance(content, str):
            users.append(content)
        elif role == "assistant":
            calls = item.get("tool_calls")
            if isinstance(calls, list):
                for call in calls:
                    fn = call.get("function") if isinstance(call, dict) else None
                    name = fn.get("name") if isinstance(fn, dict) else None
                    args = fn.get("arguments") if isinstance(fn, dict) else None
                    if isinstance(name, str) and name:
                        evidence.append("assistant requested " + name + " args=" + str(args)[:400])
            if isinstance(content, str) and content.strip():
                evidence.append("assistant note: " + content.strip()[:500])
        elif role == "tool" and isinstance(content, str):
            evidence.append(str(item.get("name", "tool")) + ": " + content[:700])
    users = list(dict.fromkeys(users))
    evidence = evidence[-AGENT_CONTEXT_EVIDENCE_LIMIT:]
    parts = [
        AGENT_CONTEXT_CHECKPOINT_PREFIX + " Continue the same mission; older tool chatter was compacted, not completed.",
        "Do not broaden scope. Re-inspect live state before relying on summarized execution evidence.",
    ]
    if users:
        parts.append(AGENT_CONTEXT_INSTRUCTIONS_JSON_HEADER + json.dumps(users, ensure_ascii=False, separators=(",", ":")))
    if evidence:
        parts.append("Earlier execution evidence summary:\n- " + "\n- ".join(evidence))
    checkpoint = {"role":"system","content":"\n\n".join(parts)}
    compacted = [conversation[0], checkpoint] + conversation[start:]
    return compacted, {"beforeChars":before,"afterChars":agent_context_chars(compacted),"removedMessages":len(removed),"preservedUserInstructions":len(users)}


def agent_tool_signature(name, arguments, result) -> str:
    raw = json.dumps({"name":name,"arguments":arguments,"result":result}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def agent_stagnation_reason(signatures):
    n = AGENT_STAGNATION_REPEAT_THRESHOLD
    if len(signatures) >= n and len(set(signatures[-n:])) == 1:
        return "repeated identical tool action and result"
    for width in (2, 3, 4):
        span = width * 3
        if len(signatures) >= span:
            tail = signatures[-span:]
            if tail == tail[:width] * 3:
                return f"repeated {width}-step tool cycle without new evidence"
    return None

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "workspace_list",
            "description": "List files and directories inside the selected workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Workspace-relative directory path. Defaults to ."}},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "workspace_read",
            "description": "Read a UTF-8 text file inside the selected workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "workspace_search",
            "description": "Search workspace paths and UTF-8 text contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "workspace_write",
            "description": "Create or replace a UTF-8 text file inside the selected workspace. Parent directory must already exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "workspace_patch",
            "description": "Apply a targeted UTF-8 text replacement inside one workspace file. By default the old text must occur exactly once.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "oldText": {"type": "string"},
                    "newText": {"type": "string"},
                    "replaceAll": {"type": "boolean"},
                },
                "required": ["path", "oldText", "newText"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "workspace_move",
            "description": "Rename or move one file or directory inside the selected workspace. Destination must not already exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "destination": {"type": "string"},
                },
                "required": ["source", "destination"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "workspace_delete",
            "description": "Delete a workspace file, or a directory only when recursive=true. Never use outside the assigned development task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "recursive": {"type": "boolean"},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Inspect Git status for the selected workspace.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Inspect workspace Git changes. Set staged=true for the index.",
            "parameters": {
                "type": "object",
                "properties": {"staged": {"type": "boolean"}},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_log",
            "description": "Inspect recent Git commit history for the selected workspace.",
            "parameters": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 50}},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "workspace_mkdir",
            "description": "Create a directory inside the selected workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "parents": {"type": "boolean"},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "shell",
            "description": "Run a Termux shell command with the selected workspace as its execution root. Use only when needed for coding, builds, tests, git inspection, or project tooling. Avoid destructive commands unless the user explicitly requested them.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "cwd": {"type": "string", "description": "Workspace-relative directory. Defaults to ."},
                    "timeoutSeconds": {"type": "integer", "minimum": 1, "maximum": 120},
                },
                "required": ["command"],
                "additionalProperties": False,
            },
        },
    },
]


def agent_tool_result(root_value: str, name: str, arguments: dict, full_access: bool = False) -> dict:
    if not isinstance(arguments, dict):
        raise ValueError("tool arguments must be an object")

    if name == "workspace_list":
        root, target = workspace_path(root_value, arguments.get("path", "."), full_access=full_access)
        if not target.is_dir():
            raise ValueError("path is not a directory")
        items = []
        for child in sorted(target.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
            entry = {
                "name": child.name,
                "path": workspace_rel(root, child),
                "type": "directory" if child.is_dir() else "file",
            }
            if child.is_file():
                entry["size"] = child.stat().st_size
            items.append(entry)
        return {"ok": True, "path": workspace_rel(root, target), "items": items[:500]}

    if name == "workspace_read":
        root, target = workspace_path(root_value, arguments.get("path"), full_access=full_access)
        if not target.is_file():
            raise ValueError("path is not a file")
        size = target.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ValueError("file exceeds read limit")
        return {
            "ok": True,
            "path": workspace_rel(root, target),
            "bytes": size,
            "content": target.read_text(encoding="utf-8"),
        }

    if name == "workspace_search":
        needle = arguments.get("query")
        if not isinstance(needle, str) or not needle:
            raise ValueError("query is required")
        limit = arguments.get("limit", 50)
        if not isinstance(limit, int):
            raise ValueError("limit must be an integer")
        limit = max(1, min(limit, 100))
        root = workspace_root(root_value)
        folded = needle.casefold()
        results = []
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_SEARCH_DIRS]
            base_path = Path(base)
            for filename in files:
                path = base_path / filename
                try:
                    rel = workspace_rel(root, path)
                    if folded in rel.casefold():
                        results.append({"path": rel, "line": 0, "preview": rel})
                        if len(results) >= limit:
                            break
                    if path.stat().st_size > MAX_SEARCH_FILE_BYTES:
                        continue
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                for number, line in enumerate(text.splitlines(), 1):
                    if folded in line.casefold():
                        results.append({"path": rel, "line": number, "preview": line[:240]})
                        if len(results) >= limit:
                            break
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break
        return {"ok": True, "query": needle, "results": results, "truncated": len(results) >= limit}

    if name == "workspace_write":
        content = arguments.get("content")
        if not isinstance(content, str):
            raise ValueError("content must be text")
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_FILE_BYTES:
            raise ValueError("file exceeds write limit")
        root, target = workspace_path(root_value, arguments.get("path"), allow_missing=True, full_access=full_access)
        if target.exists() and not target.is_file():
            raise ValueError("path is not a file")
        if not target.parent.is_dir():
            raise ValueError("parent directory does not exist")
        temp = target.with_name(target.name + ".closedcode.agent.tmp")
        if temp.exists():
            raise ValueError("temporary write path already exists")
        temp.write_bytes(encoded)
        os.chmod(temp, stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o600)
        os.replace(temp, target)
        return {"ok": True, "path": workspace_rel(root, target), "bytes": len(encoded)}

    if name == "workspace_patch":
        old_text = arguments.get("oldText")
        new_text = arguments.get("newText")
        if not isinstance(old_text, str) or not old_text:
            raise ValueError("oldText must be non-empty text")
        if not isinstance(new_text, str):
            raise ValueError("newText must be text")
        root, target = workspace_path(root_value, arguments.get("path"), full_access=full_access)
        if not target.is_file():
            raise ValueError("path is not a file")
        content = target.read_text(encoding="utf-8")
        occurrences = content.count(old_text)
        replace_all = bool(arguments.get("replaceAll", False))
        if occurrences == 0:
            raise ValueError("oldText not found")
        if not replace_all and occurrences != 1:
            raise ValueError("oldText must occur exactly once unless replaceAll=true")
        updated = content.replace(old_text, new_text, -1 if replace_all else 1)
        encoded = updated.encode("utf-8")
        if len(encoded) > MAX_FILE_BYTES:
            raise ValueError("file exceeds write limit")
        temp = target.with_name(target.name + ".closedcode.agent.tmp")
        if temp.exists():
            raise ValueError("temporary write path already exists")
        temp.write_bytes(encoded)
        os.chmod(temp, stat.S_IMODE(target.stat().st_mode))
        os.replace(temp, target)
        return {"ok": True, "path": workspace_rel(root, target), "replacements": occurrences if replace_all else 1, "bytes": len(encoded)}

    if name == "workspace_move":
        root, source = workspace_path(root_value, arguments.get("source"), full_access=full_access)
        _, destination = workspace_path(root_value, arguments.get("destination"), allow_missing=True, full_access=full_access)
        if source == root:
            raise ValueError("cannot move workspace root")
        if destination.exists():
            raise ValueError("destination already exists")
        if not destination.parent.is_dir():
            raise ValueError("destination parent does not exist")
        source.rename(destination)
        return {"ok": True, "source": workspace_rel(root, source), "destination": workspace_rel(root, destination)}

    if name == "workspace_delete":
        root, target = workspace_path(root_value, arguments.get("path"), full_access=full_access)
        if target == root:
            raise ValueError("cannot delete workspace root")
        recursive = bool(arguments.get("recursive", False))
        rel = workspace_rel(root, target)
        if target.is_dir():
            if not recursive:
                target.rmdir()
            else:
                shutil.rmtree(target)
        else:
            target.unlink()
        return {"ok": True, "path": rel, "deleted": True, "recursive": recursive}

    if name in {"git_status", "git_diff", "git_log"}:
        root = workspace_root(root_value)
        if name == "git_status":
            command = ["git", "-C", str(root), "status", "--short", "--branch"]
        elif name == "git_diff":
            command = ["git", "-C", str(root), "diff", "--no-ext-diff"]
            if bool(arguments.get("staged", False)):
                command.append("--cached")
            command.extend(["--", "."])
        else:
            limit = arguments.get("limit", 10)
            if not isinstance(limit, int):
                raise ValueError("limit must be an integer")
            limit = max(1, min(limit, 50))
            command = ["git", "-C", str(root), "log", f"-{limit}", "--oneline", "--decorate"]
        completed = subprocess.run(
            command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30, check=False,
        )
        output = completed.stdout[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
        error = completed.stderr[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
        if completed.returncode != 0:
            raise ValueError("git command failed: " + (error.strip() or str(completed.returncode)))
        return {"ok": True, "output": output, "truncated": len(completed.stdout) > MAX_COMMAND_OUTPUT_BYTES}

    if name == "workspace_mkdir":
        root, target = workspace_path(root_value, arguments.get("path"), allow_missing=True, full_access=full_access)
        if target.exists():
            raise ValueError("path already exists")
        target.mkdir(parents=bool(arguments.get("parents", False)), mode=0o700)
        return {"ok": True, "path": workspace_rel(root, target), "created": True}

    if name == "shell":
        command = arguments.get("command")
        if not isinstance(command, str) or not command.strip():
            raise ValueError("command is required")
        if len(command) > MAX_COMMAND_CHARS:
            raise ValueError("command exceeds length limit")
        timeout_seconds = arguments.get("timeoutSeconds", 60)
        if not isinstance(timeout_seconds, int):
            raise ValueError("timeoutSeconds must be an integer")
        timeout_seconds = max(1, min(timeout_seconds, MAX_COMMAND_TIMEOUT_SECONDS))
        root, cwd = workspace_path(root_value, arguments.get("cwd", "."), full_access=full_access)
        if not cwd.is_dir():
            raise ValueError("cwd is not a directory")
        started = time.monotonic()
        try:
            completed = subprocess.run(
                ["/data/data/com.termux/files/usr/bin/sh", "-lc", command],
                cwd=str(cwd),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_seconds,
                check=False,
            )
            timed_out = False
            exit_code = completed.returncode
            stdout = completed.stdout[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
            stderr = completed.stderr[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
            stdout_truncated = len(completed.stdout) > MAX_COMMAND_OUTPUT_BYTES
            stderr_truncated = len(completed.stderr) > MAX_COMMAND_OUTPUT_BYTES
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            exit_code = None
            raw_stdout = exc.stdout or b""
            raw_stderr = exc.stderr or b""
            stdout = raw_stdout[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
            stderr = raw_stderr[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
            stdout_truncated = len(raw_stdout) > MAX_COMMAND_OUTPUT_BYTES
            stderr_truncated = len(raw_stderr) > MAX_COMMAND_OUTPUT_BYTES
        return {
            "ok": True,
            "cwd": workspace_rel(root, cwd),
            "exitCode": exit_code,
            "timedOut": timed_out,
            "durationMs": int((time.monotonic() - started) * 1000),
            "stdout": stdout,
            "stderr": stderr,
            "stdoutTruncated": stdout_truncated,
            "stderrTruncated": stderr_truncated,
        }

    raise ValueError("unknown tool: " + str(name))


def provider_status() -> dict[str, bool]:
    try:
        data = load_auth()
    except Exception:
        return {provider: False for provider in PROVIDERS}
    result: dict[str, bool] = {}
    for provider in PROVIDERS:
        entry = data.get(provider)
        result[provider] = (
            isinstance(entry, dict)
            and entry.get("type") == "api"
            and isinstance(entry.get("key"), str)
            and bool(entry.get("key"))
        )
    return result


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "ClosedCodePassthrough/" + VERSION

    def log_message(self, fmt, *args):
        # Never log prompts, authorization headers, or provider response bodies.
        return

    def send_json(self, status: int, payload: dict):
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/history":
            try:
                values = parse_qs(parsed.query).get("sessionID", [])
                session_id = values[0] if values else ""
                self.send_json(
                    200,
                    {"sessionID": session_id, "messages": load_history(session_id), "timeline": load_timeline(session_id)},
                )
            except ValueError as exc:
                self.send_json(400, {"error": "invalid_request", "message": str(exc)})
            except Exception as exc:
                self.send_json(
                    500,
                    {"error": "history_failure", "message": exc.__class__.__name__},
                )
            return
        if parsed.path in {"/fs/list", "/fs/read", "/fs/search", "/fs/diff"}:
            try:
                query = parse_qs(parsed.query)
                root_value = (query.get("root") or [""])[0]
                if parsed.path == "/fs/diff":
                    status_result = agent_tool_result(root_value, "git_status", {})
                    diff_result = agent_tool_result(root_value, "git_diff", {})
                    self.send_json(
                        200,
                        {
                            "root": str(workspace_root(root_value)),
                            "status": status_result.get("output", ""),
                            "diff": diff_result.get("output", ""),
                            "statusTruncated": bool(status_result.get("truncated", False)),
                            "diffTruncated": bool(diff_result.get("truncated", False)),
                        },
                    )
                    return
                if parsed.path == "/fs/list":
                    path_value = (query.get("path") or ["."])[0]
                    root, target = workspace_path(root_value, path_value)
                    if not target.is_dir():
                        raise ValueError("path is not a directory")
                    items = []
                    for child in sorted(target.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
                        try:
                            entry = {
                                "name": child.name,
                                "path": workspace_rel(root, child),
                                "type": "directory" if child.is_dir() else "file",
                            }
                            if child.is_file():
                                entry["size"] = child.stat().st_size
                            items.append(entry)
                        except OSError:
                            continue
                    self.send_json(200, {"path": workspace_rel(root, target), "items": items})
                    return
                if parsed.path == "/fs/read":
                    path_value = (query.get("path") or [""])[0]
                    root, target = workspace_path(root_value, path_value)
                    if not target.is_file():
                        raise ValueError("path is not a file")
                    size = target.stat().st_size
                    if size > MAX_FILE_BYTES:
                        raise ValueError("file exceeds read limit")
                    try:
                        content = target.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        raise ValueError("file is not UTF-8 text")
                    self.send_json(200, {"path": workspace_rel(root, target), "bytes": size, "content": content})
                    return
                needle = (query.get("query") or [""])[0]
                if not needle:
                    raise ValueError("query is required")
                try:
                    limit = max(1, min(int((query.get("limit") or ["100"])[0]), 200))
                except ValueError:
                    raise ValueError("invalid limit")
                root = workspace_root(root_value)
                folded = needle.casefold()
                results = []
                for base, dirs, files in os.walk(root):
                    dirs[:] = [name for name in dirs if name not in SKIP_SEARCH_DIRS]
                    base_path = Path(base)
                    for name in files:
                        path = base_path / name
                        try:
                            rel = workspace_rel(root, path)
                            if folded in rel.casefold():
                                results.append({"path": rel, "line": 0, "preview": rel})
                                if len(results) >= limit:
                                    break
                            if path.stat().st_size > MAX_SEARCH_FILE_BYTES:
                                continue
                            text = path.read_text(encoding="utf-8")
                        except (OSError, UnicodeDecodeError):
                            continue
                        for number, line in enumerate(text.splitlines(), 1):
                            if folded in line.casefold():
                                results.append({"path": rel, "line": number, "preview": line[:240]})
                                if len(results) >= limit:
                                    break
                        if len(results) >= limit:
                            break
                    if len(results) >= limit:
                        break
                self.send_json(200, {"query": needle, "results": results, "truncated": len(results) >= limit})
            except (ValueError, FileNotFoundError) as exc:
                self.send_json(400, {"error": "invalid_request", "message": str(exc)})
            except Exception as exc:
                self.send_json(500, {"error": "filesystem_failure", "message": exc.__class__.__name__})
            return
        if self.path == "/health":
            self.send_json(
                200,
                {
                    "healthy": True,
                    "service": "closedcode-passthrough",
                    "version": VERSION,
                    "bind": "loopback-only",
                    "providers": provider_status(),
                },
            )
            return
        if self.path == "/providers":
            status = provider_status()
            self.send_json(
                200,
                {
                    "providers": [
                        {
                            "id": provider,
                            "connected": connected,
                            "baseUrlSource": "environment"
                            if os.environ.get(PROVIDERS[provider]["env"])
                            else "default",
                        }
                        for provider, connected in status.items()
                    ]
                },
            )
            return
        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path not in {"/v1/chat/completions", "/history", "/fs/write", "/fs/mkdir", "/exec", "/cancel", "/agent", "/agent/permission", "/agent/steer"}:
            self.send_json(404, {"error": "not_found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError("invalid request size")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("request body must be an object")

            if parsed.path == "/cancel":
                request_id = validate_request_id(payload.get("requestID"))
                cancelled = active_stream_cancel(request_id)
                self.send_json(200, {"requestID": request_id, "cancelled": cancelled})
                return

            if parsed.path == "/agent/steer":
                request_id = validate_request_id(payload.get("requestID"))
                text = payload.get("text")
                queued = active_stream_steer(request_id, text)
                if not queued:
                    self.send_json(
                        409,
                        {
                            "requestID": request_id,
                            "queued": False,
                            "error": "request_not_active",
                        },
                    )
                    return
                self.send_json(200, {"requestID": request_id, "queued": True})
                return

            if parsed.path == "/agent/permission":
                request_id = validate_request_id(payload.get("requestID"))
                permission_id = payload.get("permissionID")
                decision = payload.get("decision")
                if not isinstance(permission_id, str) or not permission_id:
                    raise ValueError("permissionID is required")
                resolved = agent_permission_resolve(permission_id, request_id, decision)
                self.send_json(
                    200,
                    {
                        "requestID": request_id,
                        "permissionID": permission_id,
                        "decision": decision,
                        "resolved": resolved,
                    },
                )
                return

            if parsed.path == "/agent":
                provider_id = payload.get("providerID")
                model = payload.get("model")
                session_id = payload.get("sessionID")
                request_id = validate_request_id(payload.get("requestID"))
                root_value = payload.get("root")
                autonomy = payload.get("autonomy", "ask")
                messages = payload.get("messages")
                finalize_after_tools = payload.get("finalizeAfterTools")
                if autonomy not in {"ask", "yolo", "full"}:
                    raise ValueError("autonomy must be ask, yolo, or full")
                if provider_id not in PROVIDERS:
                    raise ValueError("providerID must be nvidia or zai")
                if not isinstance(model, str) or not model.strip():
                    raise ValueError("model is required")
                history_path(session_id)
                workspace_root(root_value)
                prior_history = load_history(session_id)
                current_history_messages = normalize_history_messages(messages)
                if not current_history_messages:
                    raise ValueError("messages must be a non-empty array")
                if finalize_after_tools is not None:
                    if isinstance(finalize_after_tools, bool) or not isinstance(finalize_after_tools, int):
                        raise ValueError("finalizeAfterTools must be an integer")
                    if finalize_after_tools < 1 or finalize_after_tools > 100000:
                        raise ValueError("finalizeAfterTools must be between 1 and 100000")

                active_stream_register(request_id, None, session_id)
                try:
                    persist_messages(session_id, current_history_messages)
                except Exception:
                    active_stream_unregister(request_id)
                    raise
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache, no-store")
                self.send_header("Connection", "close")
                self.end_headers()

                autonomy_note = (
                    "Autonomy mode is FULL ACCESS / DANGER: ClosedCode workspace containment is disabled. Absolute filesystem paths may reach anything Termux can legally access. Filesystem mutation tools and shell run without approval prompts. Android/Linux permissions, SELinux, mounts, and root status remain hard limits. " if autonomy == "full" else
                    "Autonomy mode is YOLO/AUTO-APPROVE: routine workspace-scoped mutation tools run without prompts, but shell commands remain approval-gated. Containment still applies. This is not Full Access. " if autonomy == "yolo" else
                    "Autonomy mode is ASK/GUARDED: filesystem actions remain workspace-contained and mutating tools may require explicit user approval. "
                )
                system = {
                    "role": "system",
                    "content": (
                        "You are ClosedCode, an on-device coding agent. Use the provided tools to inspect, "
                        "modify, build, test, and diagnose the selected workspace. Never claim a file was "
                        "changed or a command was run unless you actually used the corresponding tool. "
                        "Keep actions scoped to the user's assigned development task and selected workspace. "
                        "Prefer inspecting before editing. " + autonomy_note +
                        "Long missions are expected: continue while useful work remains and do not stop merely because many reasoning or tool rounds were needed. Maintain the original definition of done, avoid duplicate work, and stop promptly once the task is actually complete. "
                        "When the task is complete, inspect the resulting changes and answer concisely with what "
                        "changed and meaningful test/build results."
                    ),
                }
                conversation = [system] + prior_history + current_history_messages
                key = provider_key(provider_id)
                upstream_url = provider_base(provider_id) + "/chat/completions"
                final_text = ""
                cancelled = False
                termination_reason = "completed"
                completed_rounds = 0
                last_zai_provider_round_finished_at = None
                recent_tool_signatures = []
                stagnation_interventions = 0
                productive_tools_since_guardrail = 0
                successful_tool_actions = 0
                finalization_mode = False
                finalization_retries = 0
                provider_rounds = 0
                token_reported_rounds = 0
                token_prompt_tokens = 0
                token_completion_tokens = 0
                token_total_tokens = 0
                token_prompt_complete = True
                token_completion_complete = True
                token_total_complete = True

                try:
                    for round_index in range(agent_emergency_round_limit()):
                        completed_rounds = round_index + 1
                        if active_stream_cancelled(request_id):
                            cancelled = True
                            break

                        queued_steering = active_stream_take_steering(request_id)
                        if queued_steering:
                            for steering_text in queued_steering:
                                steering_message = {"role": "user", "content": steering_text}
                                conversation.append(steering_message)

                            steering_event = {
                                "closedcode": {
                                    "type": "steering",
                                    "requestID": request_id,
                                    "status": "applied",
                                    "count": len(queued_steering),
                                }
                            }
                            self.wfile.write(
                                ("data: " + json.dumps(steering_event, separators=(",", ":")) + "\n\n").encode("utf-8")
                            )
                            self.wfile.flush()

                        if provider_id == "zai" and last_zai_provider_round_finished_at is not None:
                            elapsed_since_zai_round = time.monotonic() - last_zai_provider_round_finished_at
                            pacing_delay = max(0.0, ZAI_MIN_AGENT_ROUND_INTERVAL_SECONDS - elapsed_since_zai_round)
                            if pacing_delay > 0 and not wait_with_cancel(request_id, pacing_delay):
                                cancelled = True
                                break

                        compacted, compaction = agent_compact_conversation(conversation)
                        if compaction is not None:
                            conversation = compacted
                            event = {"closedcode":{"type":"context_compaction","requestID":request_id,"status":"completed","round":round_index + 1,**compaction}}
                            self.wfile.write(("data: " + json.dumps(event, separators=(",", ":")) + "\n\n").encode("utf-8"))
                            self.wfile.flush()

                        if finalize_after_tools is not None and successful_tool_actions >= finalize_after_tools and not finalization_mode:
                            finalization_mode = True
                            conversation.append({
                                "role": "system",
                                "content": (
                                    "Explicit finalization boundary reached after the requested successful-tool threshold. "
                                    "Tool use is now disabled for this request. Synthesize the final answer from the evidence already gathered, "
                                    "preserve every user requirement and required output marker, and do not request additional tools."
                                ),
                            })
                            event = {
                                "closedcode": {
                                    "type": "finalization",
                                    "requestID": request_id,
                                    "status": "required",
                                    "successfulTools": successful_tool_actions,
                                    "threshold": finalize_after_tools,
                                }
                            }
                            self.wfile.write(("data: " + json.dumps(event, separators=(",", ":")) + "\n\n").encode("utf-8"))
                            self.wfile.flush()

                        upstream_payload = {
                            "model": model,
                            "messages": conversation,
                            "temperature": 0,
                            "stream": False,
                        }
                        upstream_payload["tools"] = AGENT_TOOLS
                        upstream_payload["tool_choice"] = "none" if finalization_mode else "auto"
                        completion = (
                            agent_provider_stream_completion
                            if provider_id == "zai"
                            else agent_provider_completion
                        )
                        response = completion(
                            provider_id,
                            upstream_url,
                            key,
                            upstream_payload,
                            request_id,
                        )
                        if provider_id == "zai":
                            last_zai_provider_round_finished_at = time.monotonic()
                        provider_rounds += 1
                        round_usage = agent_provider_token_usage(response)
                        if round_usage is None:
                            token_prompt_complete = False
                            token_completion_complete = False
                            token_total_complete = False
                        else:
                            token_reported_rounds += 1
                            value = round_usage.get("promptTokens")
                            if value is None: token_prompt_complete = False
                            else: token_prompt_tokens += value
                            value = round_usage.get("completionTokens")
                            if value is None: token_completion_complete = False
                            else: token_completion_tokens += value
                            value = round_usage.get("totalTokens")
                            if value is None: token_total_complete = False
                            else: token_total_tokens += value

                        if active_stream_cancelled(request_id):
                            cancelled = True
                            break
                        choices = response.get("choices") if isinstance(response, dict) else None
                        choice = choices[0] if isinstance(choices, list) and choices else {}
                        message = choice.get("message") if isinstance(choice, dict) else {}
                        if not isinstance(message, dict):
                            raise RuntimeError("provider response missing message")

                        tool_calls = message.get("tool_calls")
                        if finalization_mode and isinstance(tool_calls, list) and tool_calls:
                            finalization_retries += 1
                            retry_event = {
                                "closedcode": {
                                    "type": "finalization_retry",
                                    "requestID": request_id,
                                    "status": "retry",
                                    "retry": finalization_retries,
                                    "maxRetries": AGENT_FINALIZATION_MAX_RETRIES,
                                    "reason": "provider_returned_tool_calls_while_tool_choice_none",
                                }
                            }
                            self.wfile.write(("data: " + json.dumps(retry_event, separators=(",", ":")) + "\n\n").encode("utf-8"))
                            self.wfile.flush()
                            if finalization_retries > AGENT_FINALIZATION_MAX_RETRIES:
                                raise RuntimeError(
                                    "provider repeatedly returned tool calls during explicit finalization despite tool_choice=none"
                                )
                            conversation.append({
                                "role": "system",
                                "content": (
                                    "Finalization retry: tools are unavailable and no tool call will be executed. "
                                    "Do not request tools. Produce the required final answer now from evidence already gathered, "
                                    "including every required marker and preserved user constraint."
                                ),
                            })
                            continue
                        if not (isinstance(tool_calls, list) and tool_calls):
                            queued_steering = active_stream_take_steering(request_id)
                            if queued_steering:
                                conversation.append(message)
                                for steering_text in queued_steering:
                                    steering_message = {"role": "user", "content": steering_text}
                                    conversation.append(steering_message)

                                steering_event = {
                                    "closedcode": {
                                        "type": "steering",
                                        "requestID": request_id,
                                        "status": "applied",
                                        "count": len(queued_steering),
                                    }
                                }
                                self.wfile.write(
                                    ("data: " + json.dumps(steering_event, separators=(",", ":")) + "\n\n").encode("utf-8")
                                )
                                self.wfile.flush()
                                continue

                        if isinstance(tool_calls, list) and tool_calls:
                            conversation.append(message)
                            for call in tool_calls:
                                if active_stream_cancelled(request_id):
                                    cancelled = True
                                    break
                                call_id = call.get("id") if isinstance(call, dict) else None
                                function = call.get("function") if isinstance(call, dict) else None
                                name = function.get("name") if isinstance(function, dict) else None
                                raw_args = function.get("arguments", "{}") if isinstance(function, dict) else "{}"
                                arguments = {}
                                if not isinstance(call_id, str) or not call_id:
                                    call_id = "closedcode-call-" + str(round_index)
                                if not isinstance(name, str) or not name:
                                    name = "unknown"
                                try:
                                    arguments = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                                    if name in AGENT_APPROVAL_TOOLS and not (autonomy == "full" or (autonomy == "yolo" and name in YOLO_AUTO_APPROVAL_TOOLS)):
                                        permission_id = agent_permission_id(request_id, call_id, round_index)
                                        agent_permission_register(permission_id, request_id)
                                        try:
                                            permission_event = {
                                                "closedcode": {
                                                    "type": "permission",
                                                    "requestID": request_id,
                                                    "permissionID": permission_id,
                                                    "name": name,
                                                    "arguments": arguments,
                                                }
                                            }
                                            self.wfile.write(
                                                ("data: " + json.dumps(permission_event, separators=(",", ":")) + "\n\n").encode("utf-8")
                                            )
                                            self.wfile.flush()
                                            decision = agent_permission_wait(permission_id, request_id)
                                        finally:
                                            agent_permission_unregister(permission_id)
                                        if decision == "cancelled":
                                            cancelled = True
                                            break
                                        if decision != "allow":
                                            result = {"ok": False, "error": "tool permission rejected"}
                                        else:
                                            tool_event = {
                                                "closedcode": {
                                                    "type": "tool",
                                                    "requestID": request_id,
                                                    "name": name,
                                                    "status": "running",
                                                    "arguments": arguments,
                                                }
                                            }
                                            self.wfile.write(
                                                ("data: " + json.dumps(tool_event, separators=(",", ":")) + "\n\n").encode("utf-8")
                                            )
                                            self.wfile.flush()
                                            result = agent_tool_result(root_value, name, arguments, full_access=autonomy == "full")
                                    else:
                                        tool_event = {
                                            "closedcode": {
                                                "type": "tool",
                                                "requestID": request_id,
                                                "name": name,
                                                "status": "running",
                                                "arguments": arguments,
                                            }
                                        }
                                        self.wfile.write(
                                            ("data: " + json.dumps(tool_event, separators=(",", ":")) + "\n\n").encode("utf-8")
                                        )
                                        self.wfile.flush()
                                        result = agent_tool_result(root_value, name, arguments, full_access=autonomy == "full")
                                except Exception as exc:
                                    result = {"ok": False, "error": str(exc)}
                                if result.get("ok"):
                                    successful_tool_actions += 1
                                result_text = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
                                if len(result_text.encode("utf-8")) > AGENT_TOOL_RESULT_LIMIT:
                                    result_text = json.dumps({
                                        "ok": False,
                                        "error": "tool result exceeded limit",
                                    }, separators=(",", ":"))
                                conversation.append({
                                    "role": "tool",
                                    "tool_call_id": call_id,
                                    "name": name,
                                    "content": result_text,
                                })
                                result_event = {
                                    "closedcode": {
                                        "type": "tool",
                                        "requestID": request_id,
                                        "name": name,
                                        "status": "completed" if result.get("ok") else "error",
                                        "detail": result_text[:1000],
                                    }
                                }
                                persist_timeline_items(session_id, [{"kind":"tool","name":name,"status":"completed" if result.get("ok") else "error","detail":result_text[:1000]}])
                                self.wfile.write(("data: " + json.dumps(result_event, separators=(",", ":")) + "\n\n").encode("utf-8"))
                                self.wfile.flush()
                                recent_tool_signatures.append(agent_tool_signature(name, arguments, result))
                                recent_tool_signatures = recent_tool_signatures[-24:]
                            if cancelled:
                                break
                            reason = agent_stagnation_reason(recent_tool_signatures)
                            if reason:
                                if stagnation_interventions >= AGENT_STAGNATION_MAX_INTERVENTIONS:
                                    termination_reason = "blocked_stagnation"
                                    raise RuntimeError("agent blocked after repeated no-progress behavior: " + reason)
                                stagnation_interventions += 1
                                productive_tools_since_guardrail = 0
                                recent_tool_signatures = []
                                conversation.append({"role":"system","content":"Progress guardrail: " + reason + ". Reassess the original mission now. Use a materially different authorized approach, preserve all user constraints, and do not repeat the same tool pattern unless new evidence justifies it."})
                                event = {"closedcode":{"type":"progress_guardrail","requestID":request_id,"status":"reassess","reason":reason,"intervention":stagnation_interventions,"round":round_index + 1}}
                                self.wfile.write(("data: " + json.dumps(event, separators=(",", ":")) + "\n\n").encode("utf-8"))
                                self.wfile.flush()
                            else:
                                productive_tools_since_guardrail += len(tool_calls)
                                if productive_tools_since_guardrail >= AGENT_STAGNATION_RESET_AFTER_PRODUCTIVE_TOOLS:
                                    stagnation_interventions = 0
                            continue

                        content = message.get("content")
                        if not isinstance(content, str) or not content:
                            content = message.get("reasoning_content")
                        final_text = content if isinstance(content, str) else ""
                        if final_text:
                            delta_event = {
                                "choices": [{"index": 0, "delta": {"content": final_text}, "finish_reason": None}]
                            }
                            self.wfile.write(("data: " + json.dumps(delta_event, separators=(",", ":")) + "\n\n").encode("utf-8"))
                            self.wfile.flush()
                        break
                    else:
                        termination_reason = "resource_limit"
                        raise RuntimeError("agent reached configurable emergency round failsafe")
                except Exception as exc:
                    if termination_reason == "completed":
                        termination_reason = "error"
                    error_event = {
                        "closedcode": {
                            "type": "error",
                            "requestID": request_id,
                            "termination": termination_reason,
                            "message": str(exc)[:1500],
                        }
                    }
                    try:
                        self.wfile.write(("data: " + json.dumps(error_event, separators=(",", ":")) + "\n\n").encode("utf-8"))
                        self.wfile.flush()
                    except Exception:
                        pass
                finally:
                    cancelled = cancelled or active_stream_cancelled(request_id)
                    if cancelled:
                        termination_reason = "cancelled"
                    active_stream_unregister(request_id)
                    try:
                        if final_text:
                            persist_messages(session_id, [{"role": "assistant", "content": final_text}])
                    except Exception:
                        pass
                    try:
                        marker = {
                            "closedcode": {
                                "type": "complete",
                                "requestID": request_id,
                                "cancelled": cancelled,
                                "complete": True,
                                "termination": termination_reason,
                                "rounds": completed_rounds,
                                "tokenUsage": {
                                    "promptTokens": token_prompt_tokens if token_prompt_complete and provider_rounds else None,
                                    "completionTokens": token_completion_tokens if token_completion_complete and provider_rounds else None,
                                    "totalTokens": token_total_tokens if token_total_complete and provider_rounds else None,
                                    "providerRounds": provider_rounds,
                                    "reportedRounds": token_reported_rounds,
                                    "unreportedRounds": provider_rounds - token_reported_rounds,
                                    "exact": bool(provider_rounds and token_total_complete),
                                },
                            }
                        }
                        self.wfile.write(("data: " + json.dumps(marker, separators=(",", ":")) + "\n\n").encode("utf-8"))
                        self.wfile.flush()
                    except Exception:
                        pass
                    self.close_connection = True
                return

            if parsed.path == "/exec":
                root_value = payload.get("root")
                cwd_value = payload.get("cwd", ".")
                command = payload.get("command")
                if not isinstance(command, str) or not command.strip():
                    raise ValueError("command is required")
                if len(command) > MAX_COMMAND_CHARS:
                    raise ValueError("command exceeds length limit")
                timeout_raw = payload.get("timeoutSeconds", 60)
                if not isinstance(timeout_raw, int):
                    raise ValueError("timeoutSeconds must be an integer")
                timeout_seconds = max(1, min(timeout_raw, MAX_COMMAND_TIMEOUT_SECONDS))
                root, cwd = workspace_path(root_value, cwd_value)
                if not cwd.is_dir():
                    raise ValueError("cwd is not a directory")
                started = time.monotonic()
                try:
                    completed = subprocess.run(
                        ["/data/data/com.termux/files/usr/bin/sh", "-lc", command],
                        cwd=str(cwd),
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=timeout_seconds,
                        check=False,
                    )
                    timed_out = False
                    exit_code = completed.returncode
                    stdout = completed.stdout[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
                    stderr = completed.stderr[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
                    stdout_truncated = len(completed.stdout) > MAX_COMMAND_OUTPUT_BYTES
                    stderr_truncated = len(completed.stderr) > MAX_COMMAND_OUTPUT_BYTES
                except subprocess.TimeoutExpired as exc:
                    timed_out = True
                    exit_code = None
                    raw_stdout = exc.stdout or b""
                    raw_stderr = exc.stderr or b""
                    stdout = raw_stdout[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
                    stderr = raw_stderr[:MAX_COMMAND_OUTPUT_BYTES].decode("utf-8", errors="replace")
                    stdout_truncated = len(raw_stdout) > MAX_COMMAND_OUTPUT_BYTES
                    stderr_truncated = len(raw_stderr) > MAX_COMMAND_OUTPUT_BYTES
                self.send_json(
                    200,
                    {
                        "cwd": workspace_rel(root, cwd),
                        "exitCode": exit_code,
                        "timedOut": timed_out,
                        "durationMs": int((time.monotonic() - started) * 1000),
                        "stdout": stdout,
                        "stderr": stderr,
                        "stdoutTruncated": stdout_truncated,
                        "stderrTruncated": stderr_truncated,
                    },
                )
                return

            if parsed.path == "/fs/write":
                root_value = payload.get("root")
                path_value = payload.get("path")
                content = payload.get("content")
                if not isinstance(content, str):
                    raise ValueError("content must be text")
                encoded_content = content.encode("utf-8")
                if len(encoded_content) > MAX_FILE_BYTES:
                    raise ValueError("file exceeds write limit")
                root, target = workspace_path(root_value, path_value, allow_missing=True)
                if target.exists() and not target.is_file():
                    raise ValueError("path is not a file")
                if not target.parent.is_dir():
                    raise ValueError("parent directory does not exist")
                temp = target.with_name(target.name + ".closedcode.tmp")
                if temp.exists():
                    raise ValueError("temporary write path already exists")
                temp.write_bytes(encoded_content)
                os.chmod(temp, stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o600)
                os.replace(temp, target)
                self.send_json(200, {"path": workspace_rel(root, target), "bytes": len(encoded_content)})
                return

            if parsed.path == "/fs/mkdir":
                root_value = payload.get("root")
                path_value = payload.get("path")
                parents = bool(payload.get("parents", False))
                root, target = workspace_path(root_value, path_value, allow_missing=True)
                if target.exists():
                    raise ValueError("path already exists")
                target.mkdir(parents=parents, mode=0o700)
                self.send_json(200, {"path": workspace_rel(root, target), "created": True})
                return

            if parsed.path == "/history":
                session_id = payload.get("sessionID")
                messages = payload.get("messages")
                stored = append_history(session_id, messages)
                self.send_json(
                    200,
                    {
                        "sessionID": session_id,
                        "stored": len(normalize_history_messages(messages)),
                        "total": len(stored),
                    },
                )
                return

            provider_id = payload.pop("providerID", None)
            if provider_id is None:
                provider_id = payload.pop("provider", None)
            else:
                payload.pop("provider", None)
            if provider_id not in PROVIDERS:
                raise ValueError("providerID must be nvidia or zai")

            session_id = payload.pop("sessionID", None)
            if session_id is not None:
                history_path(session_id)

            request_id = payload.pop("requestID", None)
            if request_id is not None:
                validate_request_id(request_id)

            model = payload.get("model")
            if not isinstance(model, str) or not model.strip():
                raise ValueError("model is required")
            messages = payload.get("messages")
            if not isinstance(messages, list) or not messages:
                raise ValueError("messages must be a non-empty array")
            current_history_messages = []
            if session_id:
                current_history_messages = normalize_history_messages(messages)
                payload["messages"] = load_history(session_id) + current_history_messages

            key = provider_key(provider_id)
            upstream_url = provider_base(provider_id) + "/chat/completions"
            stream = bool(payload.get("stream", False))
            encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            req = urlrequest.Request(
                upstream_url,
                data=encoded,
                method="POST",
                headers={
                    "Authorization": "Bearer " + key,
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream" if stream else "application/json",
                    "User-Agent": "ClosedCode-Passthrough/" + VERSION,
                },
            )

            try:
                upstream = urlrequest.urlopen(req, timeout=180)
            except urlerror.HTTPError as exc:
                body = exc.read(131072).decode("utf-8", errors="replace")
                self.send_json(
                    exc.code,
                    {
                        "error": "upstream_http_error",
                        "providerID": provider_id,
                        "status": exc.code,
                        "body": body,
                    },
                )
                return

            with upstream:
                status = getattr(upstream, "status", 200)
                if stream:
                    if not request_id:
                        raise ValueError("requestID is required for streaming")
                    active_stream_register(request_id, upstream)
                    self.send_response(status)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache, no-store")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    assistant_parts = []
                    try:
                        while True:
                            if active_stream_cancelled(request_id):
                                break
                            try:
                                line = upstream.readline()
                            except Exception:
                                break
                            if not line:
                                break
                            try:
                                self.wfile.write(line)
                                self.wfile.flush()
                            except Exception:
                                break
                            try:
                                decoded = line.decode("utf-8", errors="replace").strip()
                                if decoded.startswith("data:"):
                                    data = decoded[5:].strip()
                                    if data and data != "[DONE]":
                                        event = json.loads(data)
                                        choices = event.get("choices") if isinstance(event, dict) else None
                                        choice = choices[0] if isinstance(choices, list) and choices else {}
                                        delta = choice.get("delta") if isinstance(choice, dict) else {}
                                        if isinstance(delta, dict):
                                            piece = delta.get("content")
                                            if not isinstance(piece, str) or not piece:
                                                piece = delta.get("reasoning_content")
                                            if isinstance(piece, str) and piece:
                                                assistant_parts.append(piece)
                            except Exception:
                                pass
                    finally:
                        cancelled = active_stream_cancelled(request_id)
                        active_stream_unregister(request_id)
                        if session_id:
                            try:
                                additions = list(current_history_messages)
                                assistant_text = "".join(assistant_parts)
                                if assistant_text:
                                    additions.append({"role": "assistant", "content": assistant_text})
                                if additions:
                                    append_history(session_id, additions)
                            except Exception:
                                pass
                        try:
                            marker = {
                                "closedcode": {
                                    "requestID": request_id,
                                    "cancelled": cancelled,
                                    "complete": True,
                                }
                            }
                            self.wfile.write(
                                ("data: " + json.dumps(marker, separators=(",", ":")) + "\n\n").encode("utf-8")
                            )
                            self.wfile.flush()
                        except Exception:
                            pass
                        self.close_connection = True
                    return

                body = upstream.read()
                if session_id and 200 <= status < 300:
                    try:
                        response = json.loads(body.decode("utf-8", errors="replace"))
                        choices = response.get("choices") if isinstance(response, dict) else None
                        choice = choices[0] if isinstance(choices, list) and choices else {}
                        message = choice.get("message") if isinstance(choice, dict) else {}
                        if not isinstance(message, dict):
                            message = {}
                        content = message.get("content")
                        if not isinstance(content, str) or not content:
                            content = message.get("reasoning_content")
                        additions = list(current_history_messages)
                        if isinstance(content, str) and content:
                            additions.append({"role": "assistant", "content": content})
                        if additions:
                            append_history(session_id, additions)
                    except Exception:
                        pass
                self.send_response(status)
                self.send_header(
                    "Content-Type",
                    upstream.headers.get("Content-Type", "application/json"),
                )
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": "invalid_request", "message": str(exc)})
        except (FileNotFoundError, PermissionError, RuntimeError) as exc:
            self.send_json(503, {"error": "provider_unavailable", "message": str(exc)})
        except Exception as exc:
            self.send_json(
                502,
                {"error": "passthrough_failure", "message": exc.__class__.__name__},
            )


def check() -> int:
    path = auth_path()
    payload = {
        "service": "closedcode-passthrough",
        "version": VERSION,
        "authPresent": path.is_file(),
        "providers": provider_status(),
        "nvidiaBaseUrl": provider_base("nvidia"),
        "zaiBaseUrl": provider_base("zai"),
    }
    print(json.dumps(payload, separators=(",", ":")))
    return 0 if path.is_file() else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4097)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        return check()
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("passthrough service must bind to loopback")

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(
        json.dumps(
            {
                "event": "listening",
                "service": "closedcode-passthrough",
                "host": args.host,
                "port": server.server_address[1],
                "version": VERSION,
            },
            separators=(",", ":"),
        ),
        flush=True,
    )
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
