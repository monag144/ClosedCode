#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:4097"
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


def get_json(path: str):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return r.status, json.loads(r.read().decode())


def stream(session_id: str, request_id: str, prompt: str, cancel_after_text: bool):
    body = {
        "providerID": "nvidia",
        "model": MODEL,
        "sessionID": session_id,
        "requestID": request_id,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": 256 if not cancel_after_text else 1024,
        "temperature": 0,
    }
    data = json.dumps(body, separators=(",", ":")).encode()
    req = urllib.request.Request(
        BASE + "/v1/chat/completions",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
    )
    text = []
    terminal = None
    cancel_sent = False
    with urllib.request.urlopen(req, timeout=90) as r:
        if r.status != 200:
            raise RuntimeError(f"stream HTTP {r.status}")
        while True:
            raw = r.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                continue
            event = json.loads(payload)
            cc = event.get("closedcode") if isinstance(event, dict) else None
            if isinstance(cc, dict) and cc.get("complete"):
                terminal = cc
                break
            choices = event.get("choices") if isinstance(event, dict) else None
            choice = choices[0] if isinstance(choices, list) and choices else {}
            delta = choice.get("delta") if isinstance(choice, dict) else {}
            if isinstance(delta, dict):
                piece = delta.get("content") or delta.get("reasoning_content")
                if isinstance(piece, str) and piece:
                    text.append(piece)
                    if cancel_after_text and not cancel_sent:
                        code, result = post_json("/cancel", {"requestID": request_id})
                        print("CANCEL_RESPONSE=" + json.dumps({"code": code, "body": result}, separators=(",", ":")))
                        if code != 200 or not result.get("cancelled"):
                            raise RuntimeError("cancel request was not accepted")
                        cancel_sent = True
    return "".join(text), terminal, cancel_sent


def main() -> int:
    stamp = str(int(time.time() * 1000))
    session = "op233-stream-" + stamp

    text1, terminal1, _ = stream(
        session,
        "op233-complete-" + stamp,
        "Reply with exactly STREAM_OK and nothing else.",
        False,
    )
    print("COMPLETE_TEXT=" + json.dumps(text1))
    print("COMPLETE_TERMINAL=" + json.dumps(terminal1, separators=(",", ":")))
    if terminal1 is None or terminal1.get("cancelled") is not False:
        return 41

    _, history1 = get_json("/history?sessionID=" + urllib.parse.quote(session, safe=""))
    print("HISTORY_AFTER_COMPLETE=" + json.dumps(history1, separators=(",", ":")))
    messages1 = history1.get("messages", [])
    if len(messages1) < 2:
        return 42
    if messages1[-1].get("role") != "assistant":
        return 43

    text2, terminal2, cancel_sent = stream(
        session,
        "op233-cancel-" + stamp,
        "Count upward from 1 to 1000, one number per line, with no commentary.",
        True,
    )
    print("CANCEL_PARTIAL_TEXT_LEN=" + str(len(text2)))
    print("CANCEL_TERMINAL=" + json.dumps(terminal2, separators=(",", ":")))
    if not cancel_sent or terminal2 is None or terminal2.get("cancelled") is not True:
        return 44

    _, history2 = get_json("/history?sessionID=" + urllib.parse.quote(session, safe=""))
    print("HISTORY_AFTER_CANCEL_COUNT=" + str(len(history2.get("messages", []))))
    if len(history2.get("messages", [])) < len(messages1) + 1:
        return 45

    print("PROVIDER_STREAM_COMPLETE=GREEN")
    print("PROVIDER_STREAM_HISTORY=GREEN")
    print("PROVIDER_STREAM_CANCEL=GREEN")
    return 0


if __name__ == "__main__":
    import urllib.parse
    raise SystemExit(main())
