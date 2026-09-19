#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from collections import Counter, defaultdict
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
    parser.add_argument("--steer", action="append", type=parse_steer, default=[])
    parser.add_argument("--cancel-at", type=int)
    parser.add_argument("--permission-policy", choices=("reject", "allow", "error"), default="error")
    parser.add_argument("--max-permissions", type=int, default=0)
    parser.add_argument("--socket-timeout", type=int, default=1800)
    parser.add_argument("--output")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.min_tools < 0:
        parser.error("--min-tools must be >= 0")
    if args.cancel_at is not None and args.cancel_at < 1:
        parser.error("--cancel-at must be >= 1")
    if args.max_permissions < 0:
        parser.error("--max-permissions must be >= 0")

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
    steering_posted = []
    steering_applied = 0
    cancel_posted = False
    errors = []
    terminal = None
    final_parts = []

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
                            for threshold, text in steering:
                                if completed_tools >= threshold and threshold not in steering_posted:
                                    code, body = post_json("/agent/steer", {"requestID": request_id, "text": text})
                                    if code == 200 and body.get("queued"):
                                        steering_posted.append(threshold)
                                    else:
                                        errors.append(f"steering failed at {threshold}")
                            if args.cancel_at is not None and completed_tools >= args.cancel_at and not cancel_posted:
                                code, body = post_json("/cancel", {"requestID": request_id})
                                cancel_posted = bool(code == 200 and body.get("cancelled"))
                                if not cancel_posted:
                                    errors.append("configured cancellation failed")
                        else:
                            tool_errors += 1
                            errors.append("tool error: " + name)
                elif etype == "context_compaction":
                    compactions += 1
                elif etype == "progress_guardrail":
                    guardrails += 1
                elif etype == "steering":
                    steering_applied += int(cc.get("count") or 1)
                elif etype == "error":
                    errors.append(str(cc.get("message") or "agent error"))
                if cc.get("complete"):
                    terminal = cc
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
    normal_acceptance = (
        args.cancel_at is None
        and completed_tools >= args.min_tools
        and termination == "completed"
        and not cancelled
        and steering_applied >= len(steering)
        and permissions <= args.max_permissions
        and not errors
    )
    cancel_acceptance = (
        args.cancel_at is not None
        and cancel_posted
        and completed_tools >= args.cancel_at
        and termination == "cancelled"
        and cancelled
        and permissions <= args.max_permissions
        and not errors
    )
    accepted = cancel_acceptance if args.cancel_at is not None else normal_acceptance
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
        "permissions": permissions,
        "permissionActions": dict(permission_actions),
        "compactions": compactions,
        "guardrails": guardrails,
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
    emit_summary(summary, args.output)
    print("MARATHON_ACCEPTANCE=" + ("GREEN" if accepted else "RED"))
    return 0 if accepted else 50


if __name__ == "__main__":
    raise SystemExit(main())
