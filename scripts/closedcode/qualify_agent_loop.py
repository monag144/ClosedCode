#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:4097"
ROOT = Path.home() / ".cache" / "closedcode-op237-agent-loop"
CASES = [
    ("nvidia", "nvidia/nemotron-3-ultra-550b-a55b"),
    ("zai", "glm-4.7-flash"),
]


def get_json(path: str):
    with urllib.request.urlopen(BASE + path, timeout=20) as r:
        return r.status, json.loads(r.read().decode())


def run_agent(provider: str, model: str, session_id: str, request_id: str, prompt: str):
    payload = {
        "providerID": provider,
        "model": model,
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
    tools = []
    final_text = []
    terminal = None
    errors = []
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
            data_text = line[5:].strip()
            if not data_text:
                continue
            event = json.loads(data_text)
            cc = event.get("closedcode") if isinstance(event, dict) else None
            if isinstance(cc, dict):
                etype = cc.get("type")
                if etype == "tool":
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
                final_text.append(piece)
    return {
        "tools": tools,
        "final": "".join(final_text),
        "terminal": terminal,
        "errors": errors,
    }


def main() -> int:
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True, mode=0o700)

    stamp = str(int(time.time() * 1000))
    for provider, model in CASES:
        filename = f"{provider}_agent.txt"
        expected = f"TOOL_LOOP_OK_{provider.upper()}\n"
        result = run_agent(
            provider,
            model,
            f"op237-{provider}-{stamp}",
            f"op237-{provider}-write-{stamp}",
            (
                f"You are qualifying the ClosedCode agent loop. You MUST call workspace_write "
                f"to create {filename} with exactly this content including the newline: "
                f"{expected!r} with no trailing newline. Then call workspace_read on that file to verify it. "
                "After the tool work succeeds, reply with exactly AGENT_DONE."
            ),
        )
        print(provider.upper() + "_AGENT_RESULT=" + json.dumps(result, separators=(",", ":")))
        path = ROOT / filename
        if not path.is_file():
            print(provider.upper() + "_ARTIFACT=RED_MISSING")
            return 41
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            print(provider.upper() + "_ARTIFACT=RED_CONTENT")
            print(repr(actual))
            return 42
        names = [name for name, status in result["tools"] if status == "running"]
        if "workspace_write" not in names:
            print(provider.upper() + "_WRITE_TOOL=RED")
            return 43
        if result["terminal"] is None or result["terminal"].get("cancelled"):
            print(provider.upper() + "_TERMINAL=RED")
            return 44
        if result["errors"]:
            print(provider.upper() + "_ERRORS=RED")
            return 45

        session = f"op237-{provider}-{stamp}"
        _, history = get_json("/history?sessionID=" + urllib.parse.quote(session, safe=""))
        messages = history.get("messages", [])
        print(provider.upper() + "_HISTORY_COUNT=" + str(len(messages)))
        if len(messages) < 2 or messages[-1].get("role") != "assistant":
            print(provider.upper() + "_HISTORY=RED")
            return 46
        print(provider.upper() + "_AGENT_LOOP=GREEN")

    shell_result = run_agent(
        "nvidia",
        "nvidia/nemotron-3-ultra-550b-a55b",
        f"op237-shell-{stamp}",
        f"op237-shell-request-{stamp}",
        (
            "You MUST use the shell tool to run exactly this command in the workspace root: "
            "printf 'SHELL_LOOP_OK\\n' > shell_probe.txt ; cat shell_probe.txt . "
            "Do not use workspace_write for this task. After the command succeeds, reply exactly SHELL_DONE."
        ),
    )
    print("NVIDIA_SHELL_AGENT_RESULT=" + json.dumps(shell_result, separators=(",", ":")))
    shell_file = ROOT / "shell_probe.txt"
    if not shell_file.is_file() or shell_file.read_text(encoding="utf-8") != "SHELL_LOOP_OK\n":
        print("NVIDIA_SHELL_ARTIFACT=RED")
        return 47
    shell_names = [name for name, status in shell_result["tools"] if status == "running"]
    if "shell" not in shell_names:
        print("NVIDIA_SHELL_TOOL=RED")
        return 48

    print("NVIDIA_AGENT_LOOP=GREEN")
    print("ZAI_AGENT_LOOP=GREEN")
    print("NVIDIA_AGENT_SHELL=GREEN")
    print("CLOSEDCODE_NATIVE_AGENT_LOOP=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
