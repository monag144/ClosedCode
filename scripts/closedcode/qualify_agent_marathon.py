#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import time
import threading
import urllib.request
from collections import Counter, defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = "http://127.0.0.1:4097"
MODELS = {
    "nvidia": "nvidia/nemotron-3-ultra-550b-a55b",
    "zai": "glm-4.7-flash",
}


def post_json(path: str, payload: dict, timeout: int = 30):
    data = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode())


def parse_steer(value: str):
    left, sep, text = value.partition(":")
    if not sep or not text.strip():
        raise argparse.ArgumentTypeError("steer must be TOOL_COUNT:TEXT")
    try:
        count = int(left)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("steer tool count must be an integer") from exc
    if count < 1:
        raise argparse.ArgumentTypeError("steer tool count must be >= 1")
    return count, text.strip()


def emit_summary(summary: dict, output: str | None):
    encoded = json.dumps(summary, indent=2, sort_keys=True)
    print("MARATHON_SUMMARY_BEGIN")
    print(encoded)
    print("MARATHON_SUMMARY_END")
    if output:
        Path(output).write_text(encoded + "\n", encoding="utf-8")
        print("SUMMARY_OUTPUT=" + output)


def marathon_acceptance(
    *,
    cancel_at: int | None,
    cancel_posted: bool,
    completed_tools: int,
    min_tools: int,
    termination: str | None,
    cancelled: bool,
    steering_required: int,
    steering_applied: int,
    permissions: int,
    max_permissions: int,
) -> bool:
    if cancel_at is None:
        return (
            completed_tools >= min_tools
            and termination == "completed"
            and not cancelled
            and steering_applied >= steering_required
            and permissions <= max_permissions
        )
    return (
        cancel_posted
        and completed_tools >= cancel_at
        and termination == "cancelled"
        and cancelled
        and permissions <= max_permissions
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run exactly one real ClosedCode /agent mission and collect long-horizon qualification evidence."
    )
    parser.add_argument("--provider", choices=sorted(MODELS), required=True)
    parser.add_argument("--model")
    parser.add_argument("--root", required=True)
    parser.add_argument("--autonomy", choices=("ask", "yolo"), default="ask")
    prompts = parser.add_mutually_exclusive_group(required=True)
    prompts.add_argument("--prompt")
    prompts.add_argument("--prompt-file")
    parser.add_argument("--min-tools", type=int, default=100)
    parser.add_argument("--finalize-after-tools", type=int)
    parser.add_argument("--steer", action="append", type=parse_steer, default=[])
    parser.add_argument("--cancel-at", type=int)
    parser.add_argument("--permission-policy", choices=("reject", "allow", "error"), default="error")
    parser.add_argument("--max-permissions", type=int, default=0)
    parser.add_argument("--socket-timeout", type=int, default=1800)
    parser.add_argument("--output")
    parser.add_argument("--status-port", type=int)
    parser.add_argument("--status-token")
    parser.add_argument("--status-ttl", type=int, default=1800)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.min_tools < 0:
        parser.error("--min-tools must be >= 0")
    if args.cancel_at is not None and args.cancel_at < 1:
        parser.error("--cancel-at must be >= 1")
    if args.finalize_after_tools is not None:
        if args.finalize_after_tools < 1:
            parser.error("--finalize-after-tools must be >= 1")
        if args.finalize_after_tools < args.min_tools:
            parser.error("--finalize-after-tools must be >= --min-tools")
    if args.max_permissions < 0:
        parser.error("--max-permissions must be >= 0")
    if args.status_port is not None and not (1 <= args.status_port <= 65535):
        parser.error("--status-port must be between 1 and 65535")
    if args.status_port is not None and not args.status_token:
        parser.error("--status-token is required with --status-port")
    if args.status_ttl < 30:
        parser.error("--status-ttl must be >= 30")

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error("--root must be an existing directory")
    prompt = args.prompt if args.prompt is not None else Path(args.prompt_file).read_text(encoding="utf-8")
    model = args.model or MODELS[args.provider]
    steering = sorted(args.steer, key=lambda item: item[0])
    prompt_sha = hashlib.sha256(prompt.encode()).hexdigest()

    config = {
        "provider": args.provider,
        "model": model,
        "root": str(root),
        "autonomy": args.autonomy,
        "minTools": args.min_tools,
        "finalizeAfterTools": args.finalize_after_tools,
        "steeringThresholds": [count for count, _ in steering],
        "cancelAt": args.cancel_at,
        "permissionPolicy": args.permission_policy,
        "maxPermissions": args.max_permissions,
        "promptSha256": prompt_sha,
    }
    print("MARATHON_CONFIG=" + json.dumps(config, separators=(",", ":")))
    if args.dry_run:
        print("MARATHON_DRY_RUN=GREEN_NO_PROVIDER_REQUEST")
        return 0

    stamp = str(int(time.time() * 1000))
    request_id = "marathon-request-" + stamp
    session_id = "marathon-session-" + stamp
    payload = {
        "providerID": args.provider,
        "model": model,
        "sessionID": session_id,
        "requestID": request_id,
        "root": str(root),
        "autonomy": args.autonomy,
        "messages": [{"role": "user", "content": prompt}],
    }
    if args.finalize_after_tools is not None:
        payload["finalizeAfterTools"] = args.finalize_after_tools
    request = urllib.request.Request(
        BASE + "/agent",
        data=json.dumps(payload, separators=(",", ":")).encode(),
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
    )

    started = time.time()
    pending = defaultdict(list)
    tool_counts = Counter()
    unique_signatures = set()
    completed_tools = 0
    tool_errors = 0
    permissions = 0
    permission_actions = Counter()
    compactions = 0
    guardrails = 0
    finalization_triggered = False
    finalization_retries = 0
    steering_posted = []
    steering_applied = 0
    cancel_posted = False
    errors = []
    terminal = None
    final_parts = []

    status_lock = threading.Lock()
    status_done = threading.Event()
    status_server = None
    status_state = {
        "runner": "closedcode-marathon",
        "pid": __import__("os").getpid(),
        "phase": "starting",
        "done": False,
        "accepted": None,
        "requestID": request_id,
        "sessionID": session_id,
        "provider": args.provider,
        "model": model,
        "autonomy": args.autonomy,
        "completedTools": 0,
        "toolCounts": {},
        "uniqueInvocationSignatures": 0,
        "permissions": 0,
        "compactions": 0,
        "guardrails": 0,
        "finalizationTriggered": False,
        "finalizationRetries": 0,
        "steeringPosted": [],
        "steeringApplied": 0,
        "cancelPosted": False,
        "errors": [],
        "terminal": None,
    }

    def status_patch(**values):
        with status_lock:
            status_state.update(values)

    def status_snapshot():
        with status_lock:
            return json.loads(json.dumps(status_state))

    if args.status_port is not None:
        class StatusHandler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                return

            def send_json(self, code, value):
                body = json.dumps(value, separators=(",", ":")).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path == "/status":
                    self.send_json(200, status_snapshot())
                    return
                if self.path == "/cancel/" + args.status_token:
                    try:
                        code, body = post_json("/cancel", {"requestID": request_id})
                        status_patch(cancelPosted=bool(code == 200 and body.get("cancelled")))
                        self.send_json(code, body)
                    except Exception as exc:
                        self.send_json(500, {"error": str(exc)[:300]})
                    return
                if self.path == "/shutdown/" + args.status_token:
                    if not status_snapshot().get("done"):
                        self.send_json(409, {"error": "not_done"})
                        return
                    self.send_json(200, {"shutdown": True})
                    status_done.set()
                    threading.Thread(target=status_server.shutdown, daemon=True).start()
                    return
                self.send_json(404, {"error": "not_found"})

        status_server = ThreadingHTTPServer(("127.0.0.1", args.status_port), StatusHandler)
        threading.Thread(target=status_server.serve_forever, daemon=True).start()

        def expire_status_server():
            time.sleep(args.status_ttl)
            if not status_snapshot().get("done"):
                try:
                    post_json("/cancel", {"requestID": request_id})
                    status_patch(cancelPosted=True, expiryCancel=True)
                except Exception as exc:
                    status_patch(expiryCancelError=str(exc)[:300])
                time.sleep(5)
            status_done.set()
            status_server.shutdown()

        threading.Thread(target=expire_status_server, daemon=True).start()
        print(f"STATUS_ENDPOINT=http://127.0.0.1:{args.status_port}/status")

    status_patch(phase="running")
    with urllib.request.urlopen(request, timeout=args.socket_timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"agent HTTP {response.status}")
        while True:
            raw = response.readline()
            if not raw:
                break
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data:
                continue
            event = json.loads(data)
            cc = event.get("closedcode") if isinstance(event, dict) else None
            if isinstance(cc, dict):
                etype = cc.get("type")
                if etype == "permission":
                    permissions += 1
                    status_patch(permissions=permissions)
                    policy = args.permission_policy
                    decision = "reject" if policy == "error" else policy
                    code, body = post_json(
                        "/agent/permission",
                        {"requestID": cc["requestID"], "permissionID": cc["permissionID"], "decision": decision},
                    )
                    permission_actions[decision] += 1
                    if code != 200 or not body.get("resolved"):
                        errors.append("permission resolution failed")
                    if policy == "error":
                        errors.append("unexpected permission event")
                elif etype == "tool":
                    name = str(cc.get("name"))
                    status = cc.get("status")
                    if status == "running":
                        pending[name].append(cc.get("arguments") or {})
                    elif status in ("completed", "error"):
                        arguments = pending[name].pop(0) if pending[name] else {}
                        if status == "completed":
                            completed_tools += 1
                            tool_counts[name] += 1
                            sig = json.dumps([name, arguments], sort_keys=True, separators=(",", ":"))
                            unique_signatures.add(hashlib.sha256(sig.encode()).hexdigest())
                            status_patch(completedTools=completed_tools, toolCounts=dict(tool_counts), uniqueInvocationSignatures=len(unique_signatures))
                            for threshold, text in steering:
                                if completed_tools >= threshold and threshold not in steering_posted:
                                    code, body = post_json("/agent/steer", {"requestID": request_id, "text": text})
                                    if code == 200 and body.get("queued"):
                                        steering_posted.append(threshold)
                                        status_patch(steeringPosted=list(steering_posted))
                                    else:
                                        errors.append(f"steering failed at {threshold}")
                            if args.cancel_at is not None and completed_tools >= args.cancel_at and not cancel_posted:
                                code, body = post_json("/cancel", {"requestID": request_id})
                                cancel_posted = bool(code == 200 and body.get("cancelled"))
                                status_patch(cancelPosted=cancel_posted)
                                if not cancel_posted:
                                    errors.append("configured cancellation failed")
                        else:
                            tool_errors += 1
                            errors.append("tool error: " + name)
                elif etype == "context_compaction":
                    compactions += 1
                    status_patch(compactions=compactions)
                elif etype == "progress_guardrail":
                    guardrails += 1
                    status_patch(guardrails=guardrails)
                elif etype == "finalization":
                    finalization_triggered = True
                    status_patch(finalizationTriggered=True)
                elif etype == "finalization_retry":
                    finalization_retries += 1
                    status_patch(finalizationRetries=finalization_retries)
                elif etype == "steering":
                    steering_applied += int(cc.get("count") or 1)
                    status_patch(steeringApplied=steering_applied)
                elif etype == "error":
                    errors.append(str(cc.get("message") or "agent error"))
                    status_patch(errors=list(errors))
                if cc.get("complete"):
                    terminal = cc
                    status_patch(terminal=terminal)
                    break
                continue

            choices = event.get("choices") if isinstance(event, dict) else None
            choice = choices[0] if isinstance(choices, list) and choices else {}
            delta = choice.get("delta") if isinstance(choice, dict) else {}
            content = delta.get("content") if isinstance(delta, dict) else None
            if isinstance(content, str) and content:
                final_parts.append(content)

    final_text = "".join(final_parts)
    termination = terminal.get("termination") if isinstance(terminal, dict) else None
    cancelled = bool(terminal.get("cancelled")) if isinstance(terminal, dict) else False
    accepted = marathon_acceptance(
        cancel_at=args.cancel_at,
        cancel_posted=cancel_posted,
        completed_tools=completed_tools,
        min_tools=args.min_tools,
        termination=termination,
        cancelled=cancelled,
        steering_required=len(steering),
        steering_applied=steering_applied,
        permissions=permissions,
        max_permissions=args.max_permissions,
    )
    summary = {
        "accepted": accepted,
        "requestID": request_id,
        "sessionID": session_id,
        "provider": args.provider,
        "model": model,
        "autonomy": args.autonomy,
        "promptSha256": prompt_sha,
        "elapsedSeconds": round(time.time() - started, 3),
        "completedTools": completed_tools,
        "toolCounts": dict(tool_counts),
        "uniqueInvocationSignatures": len(unique_signatures),
        "toolErrors": tool_errors,
        "errorPolicy": "observe-and-report; terminal outcome and mission criteria determine acceptance",
        "permissions": permissions,
        "permissionActions": dict(permission_actions),
        "compactions": compactions,
        "guardrails": guardrails,
        "finalizeAfterTools": args.finalize_after_tools,
        "finalizationTriggered": finalization_triggered,
        "finalizationRetries": finalization_retries,
        "steeringScheduled": [count for count, _ in steering],
        "steeringPosted": steering_posted,
        "steeringApplied": steering_applied,
        "cancelAt": args.cancel_at,
        "cancelPosted": cancel_posted,
        "terminal": terminal,
        "errors": errors,
        "finalChars": len(final_text),
        "finalSha256": hashlib.sha256(final_text.encode()).hexdigest(),
    }
    status_patch(
        phase="done",
        done=True,
        accepted=accepted,
        completedTools=completed_tools,
        toolCounts=dict(tool_counts),
        uniqueInvocationSignatures=len(unique_signatures),
        permissions=permissions,
        compactions=compactions,
        guardrails=guardrails,
        finalizationTriggered=finalization_triggered,
        finalizationRetries=finalization_retries,
        steeringPosted=list(steering_posted),
        steeringApplied=steering_applied,
        cancelPosted=cancel_posted,
        errors=list(errors),
        terminal=terminal,
        finalChars=len(final_text),
        finalSha256=hashlib.sha256(final_text.encode()).hexdigest(),
    )
    emit_summary(summary, args.output)
    print("MARATHON_ACCEPTANCE=" + ("GREEN" if accepted else "RED"))
    if status_server is not None:
        status_done.wait()
    return 0 if accepted else 50


if __name__ == "__main__":
    raise SystemExit(main())
