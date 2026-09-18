#!/usr/bin/env python3
"""ClosedCode loopback provider passthrough.

Owns NVIDIA/Z.AI HTTP forwarding outside OpenCode's compiled agent graph.
Provider API keys remain in Termux's OpenCode auth store and are never
returned by this service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import parse_qs, urlparse

VERSION = "0.2.1"
MAX_BODY = 2 * 1024 * 1024
DEFAULT_AUTH_PATH = Path.home() / ".local" / "share" / "opencode" / "auth.json"
DEFAULT_HISTORY_ROOT = Path.home() / ".local" / "share" / "closedcode" / "passthrough-history"
MAX_HISTORY_MESSAGES = 500
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
                    {"sessionID": session_id, "messages": load_history(session_id)},
                )
            except ValueError as exc:
                self.send_json(400, {"error": "invalid_request", "message": str(exc)})
            except Exception as exc:
                self.send_json(
                    500,
                    {"error": "history_failure", "message": exc.__class__.__name__},
                )
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
        if parsed.path not in {"/v1/chat/completions", "/history"}:
            self.send_json(404, {"error": "not_found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError("invalid request size")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("request body must be an object")

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
                    self.send_response(status)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache, no-store")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    while True:
                        chunk = upstream.read(8192)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
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
