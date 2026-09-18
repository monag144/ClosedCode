#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:4097"
CASES = [
    ("nvidia", "nvidia/nemotron-3-ultra-550b-a55b", "NVIDIA_A"),
    ("nvidia", "nvidia/nemotron-3-ultra-550b-a55b", "NVIDIA_B"),
    ("zai", "glm-4.7-flash", "ZAI"),
]


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


def run_case(provider: str, model: str, label: str, stamp: str):
    root = Path.home() / ".cache" / f"closedcode-op243-continuation-{label.lower()}-{stamp}"
    root.mkdir(parents=True, mode=0o700)
    filename = f"{label.lower()}.txt"
    expected = f"CONTINUE_OK_{label}"
    session_id = f"op243-{label.lower()}-{stamp}"
    request_id = f"op243-{label.lower()}-request-{stamp}"

    payload = {
        "providerID": provider,
        "model": model,
        "sessionID": session_id,
        "requestID": request_id,
        "root": str(root),
        "messages": [{
            "role": "user",
            "content": (
                f"You MUST call workspace_write to create {filename} containing exactly {expected} "
                "with no trailing newline. Then call workspace_read to verify it. "
                f"After verification reply exactly FINAL_{label}."
            ),
        }],
    }
    data = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        BASE + "/agent",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
    )

    permissions = 0
    tools = []
    errors = []
    finals = []
    terminal = None

    with urllib.request.urlopen(req, timeout=180) as r:
        if r.status != 200:
            raise RuntimeError(f"{label} agent HTTP {r.status}")
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
                    permissions += 1
                    code, body = post_json(
                        "/agent/permission",
                        {
                            "requestID": cc["requestID"],
                            "permissionID": cc["permissionID"],
                            "decision": "allow",
                        },
                    )
                    print(label + "_ALLOW=" + json.dumps({"code": code, "body": body}, separators=(",", ":")))
                    if code != 200 or not body.get("resolved"):
                        raise RuntimeError(label + " permission allow failed")
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
                finals.append(piece)

    result = {
        "root": str(root),
        "permissions": permissions,
        "tools": tools,
        "errors": errors,
        "final": "".join(finals),
        "terminal": terminal,
    }
    print(label + "_RESULT=" + json.dumps(result, separators=(",", ":")))

    artifact = root / filename
    if not artifact.is_file():
        raise RuntimeError(label + " artifact missing")
    if artifact.read_text(encoding="utf-8") != expected:
        raise RuntimeError(label + " artifact mismatch")
    if permissions < 1:
        raise RuntimeError(label + " emitted no permission event")
    if ("workspace_write", "completed") not in tools:
        raise RuntimeError(label + " write did not complete")
    if ("workspace_read", "completed") not in tools:
        raise RuntimeError(label + " read did not complete")
    if errors:
        raise RuntimeError(label + " provider continuation emitted error: " + errors[0])
    if terminal is None or terminal.get("cancelled"):
        raise RuntimeError(label + " terminal invalid")
    if "".join(finals).strip() != f"FINAL_{label}":
        raise RuntimeError(label + " final response mismatch")

    print(label + "_APPROVED_CONTINUATION=GREEN")


def main() -> int:
    stamp = str(int(time.time() * 1000))
    for provider, model, label in CASES:
        run_case(provider, model, label, stamp)
    print("APPROVED_AGENT_CONTINUATION_REPEATABILITY=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
