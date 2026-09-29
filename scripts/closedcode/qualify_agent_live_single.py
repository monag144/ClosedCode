#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:4097"
MODELS = {
    "nvidia": "nvidia/nemotron-3-ultra-550b-a55b",
    "zai": "glm-4.7-flash",
}


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=sorted(MODELS), required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    stamp = str(int(time.time() * 1000))
    provider = args.provider
    model = MODELS[provider]
    label = args.label.upper()
    root = Path.home() / ".cache" / f"closedcode-live-{provider}-{args.label.lower()}-{stamp}"
    root.mkdir(parents=True, mode=0o700)

    filename = f"{provider}_{args.label.lower()}.txt"
    expected = f"LIVE_OK_{label}"
    session_id = f"live-{provider}-{args.label.lower()}-{stamp}"
    request_id = f"live-{provider}-{args.label.lower()}-request-{stamp}"

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
    final_parts = []
    terminal = None

    print("PROVIDER=" + provider)
    print("MODEL=" + model)
    print("SCRATCH_ROOT=" + str(root))

    with urllib.request.urlopen(req, timeout=240) as r:
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
                    permissions += 1
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
                        raise RuntimeError("permission allow failed")
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
                final_parts.append(piece)

    final = "".join(final_parts)
    print("TOOLS=" + json.dumps(tools, separators=(",", ":")))
    print("ERRORS=" + json.dumps(errors, separators=(",", ":")))
    print("FINAL=" + json.dumps(final))
    print("TERMINAL=" + json.dumps(terminal, separators=(",", ":")))

    artifact = root / filename
    if not artifact.is_file():
        raise RuntimeError("artifact missing")
    if artifact.read_text(encoding="utf-8") != expected:
        raise RuntimeError("artifact mismatch")
    if permissions < 1:
        raise RuntimeError("permission event missing")
    if ("workspace_write", "completed") not in tools:
        raise RuntimeError("write completion missing")
    if ("workspace_read", "completed") not in tools:
        raise RuntimeError("read completion missing")
    if errors:
        raise RuntimeError("agent error: " + errors[0])
    if terminal is None or terminal.get("cancelled"):
        raise RuntimeError("invalid terminal")
    if final.strip() != f"FINAL_{label}":
        raise RuntimeError("final mismatch: " + repr(final))

    print("LIVE_PROVIDER_AGENT_CONTINUATION=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
