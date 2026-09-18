#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:4097"
STAMP = str(int(time.time() * 1000))
ROOT = Path.home() / ".cache" / ("closedcode-op242-permission-" + STAMP)
MODEL = "nvidia/nemotron-3-ultra-550b-a55b"


def post_json(path: str, payload: dict):
    data = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.loads(r.read().decode())


def run_agent(session_id: str, request_id: str, prompt: str, on_permission):
    payload = {
        "providerID": "nvidia",
        "model": MODEL,
        "sessionID": session_id,
        "requestID": request_id,
        "root": str(ROOT),
        "messages": [{"role": "user", "content": prompt}],
    }
    data = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        BASE + "/agent",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
    )
    permissions = []
    tools = []
    terminal = None
    errors = []
    final = []
    with urllib.request.urlopen(req, timeout=180) as r:
        if r.status != 200:
            raise RuntimeError(f"agent HTTP {r.status}")
        while True:
            raw = r.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            payload_text = line[5:].strip()
            if not payload_text:
                continue
            event = json.loads(payload_text)
            cc = event.get("closedcode") if isinstance(event, dict) else None
            if isinstance(cc, dict):
                etype = cc.get("type")
                if etype == "permission":
                    permissions.append(cc)
                    on_permission(cc)
                elif etype == "tool":
                    tools.append((cc.get("name"), cc.get("status")))
                elif etype == "error":
                    errors.append(cc.get("message", "agent error"))
                elif cc.get("complete"):
                    terminal = cc
                    break
                continue
            choices = event.get("choices") if isinstance(event, dict) else None
            choice = choices[0] if isinstance(choices, list) and choices else {}
            delta = choice.get("delta") if isinstance(choice, dict) else {}
            piece = delta.get("content") if isinstance(delta, dict) else None
            if isinstance(piece, str) and piece:
                final.append(piece)
    return {
        "permissions": permissions,
        "tools": tools,
        "terminal": terminal,
        "errors": errors,
        "final": "".join(final),
    }


def allow_permission(cc: dict):
    code, body = post_json(
        "/agent/permission",
        {
            "requestID": cc["requestID"],
            "permissionID": cc["permissionID"],
            "decision": "allow",
        },
    )
    print("ALLOW_RESPONSE=" + json.dumps({"code": code, "body": body}, separators=(",", ":")))
    if code != 200 or not body.get("resolved"):
        raise RuntimeError("allow permission did not resolve")


def reject_permission(cc: dict):
    code, body = post_json(
        "/agent/permission",
        {
            "requestID": cc["requestID"],
            "permissionID": cc["permissionID"],
            "decision": "reject",
        },
    )
    print("REJECT_RESPONSE=" + json.dumps({"code": code, "body": body}, separators=(",", ":")))
    if code != 200 or not body.get("resolved"):
        raise RuntimeError("reject permission did not resolve")


def cancel_permission(cc: dict):
    code, body = post_json("/cancel", {"requestID": cc["requestID"]})
    print("CANCEL_RESPONSE=" + json.dumps({"code": code, "body": body}, separators=(",", ":")))
    if code != 200 or not body.get("cancelled"):
        raise RuntimeError("cancel did not resolve active request")


def main() -> int:
    ROOT.mkdir(parents=True, mode=0o700)
    print("SCRATCH_ROOT=" + str(ROOT))

    allow_file = ROOT / "allowed.txt"
    allow = run_agent(
        "op242-allow-" + STAMP,
        "op242-allow-request-" + STAMP,
        (
            "You MUST call workspace_write to create allowed.txt containing exactly "
            "PERMISSION_ALLOW_OK with no trailing newline. After success, reply ALLOW_DONE."
        ),
        allow_permission,
    )
    print("ALLOW_RESULT=" + json.dumps(allow, separators=(",", ":")))
    if not allow_file.is_file() or allow_file.read_text(encoding="utf-8") != "PERMISSION_ALLOW_OK":
        print("ALLOW_ARTIFACT=RED")
        return 41
    if not allow["permissions"] or allow["permissions"][0].get("name") != "workspace_write":
        print("ALLOW_PERMISSION_EVENT=RED")
        return 42
    if ("workspace_write", "completed") not in allow["tools"]:
        print("ALLOW_TOOL_COMPLETION=RED")
        return 43

    reject_file = ROOT / "rejected.txt"
    reject = run_agent(
        "op242-reject-" + STAMP,
        "op242-reject-request-" + STAMP,
        (
            "You MUST call workspace_write to create rejected.txt containing REJECT_SHOULD_NOT_EXIST. "
            "If permission is rejected, do not try another write; reply REJECT_DONE."
        ),
        reject_permission,
    )
    print("REJECT_RESULT=" + json.dumps(reject, separators=(",", ":")))
    if reject_file.exists():
        print("REJECT_ARTIFACT=RED_EXISTS")
        return 44
    if not reject["permissions"] or reject["permissions"][0].get("name") != "workspace_write":
        print("REJECT_PERMISSION_EVENT=RED")
        return 45

    cancel_file = ROOT / "cancelled.txt"
    cancelled = run_agent(
        "op242-cancel-" + STAMP,
        "op242-cancel-request-" + STAMP,
        "You MUST call workspace_write to create cancelled.txt containing CANCEL_SHOULD_NOT_EXIST.",
        cancel_permission,
    )
    print("CANCEL_RESULT=" + json.dumps(cancelled, separators=(",", ":")))
    if cancel_file.exists():
        print("CANCEL_ARTIFACT=RED_EXISTS")
        return 46
    if cancelled["terminal"] is None or not cancelled["terminal"].get("cancelled"):
        print("CANCEL_TERMINAL=RED")
        return 47

    print("AGENT_PERMISSION_ALLOW=GREEN")
    print("AGENT_PERMISSION_REJECT=GREEN")
    print("AGENT_PERMISSION_CANCEL_WAKE=GREEN")
    print("AGENT_MUTATION_GUARD=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
