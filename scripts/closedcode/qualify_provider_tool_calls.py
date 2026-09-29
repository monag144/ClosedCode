#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.error
import urllib.request
import time

BASE = "http://127.0.0.1:4097"
CASES = [
    ("nvidia", "nvidia/nemotron-3-ultra-550b-a55b"),
    ("zai", "glm-4.7-flash"),
]
TOOL = {
    "type": "function",
    "function": {
        "name": "closedcode_probe",
        "description": "Compatibility probe. Call this function instead of answering in text.",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {"type": "string"},
            },
            "required": ["value"],
            "additionalProperties": False,
        },
    },
}


def post(payload: dict, accept: str = "application/json"):
    data = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        BASE + "/v1/chat/completions",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": accept},
    )
    try:
        return urllib.request.urlopen(req, timeout=90)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body


def inspect_nonstream(provider: str, model: str):
    payload = {
        "providerID": provider,
        "model": model,
        "messages": [{
            "role": "user",
            "content": "Call closedcode_probe with value PROBE_OK. Do not answer in normal text."
        }],
        "tools": [TOOL],
        "tool_choice": "auto",
        "temperature": 0,
        "max_tokens": 128,
        "stream": False,
    }
    result = post(payload)
    if isinstance(result, tuple):
        code, body = result
        print(f"{provider.upper()}_NONSTREAM_HTTP={code}")
        print(f"{provider.upper()}_NONSTREAM_BODY={body[:1200]}")
        return False, code
    with result:
        body = result.read().decode("utf-8", errors="replace")
        print(f"{provider.upper()}_NONSTREAM_HTTP={result.status}")
        print(f"{provider.upper()}_NONSTREAM_BODY={body[:2000]}")
        data = json.loads(body)
        choices = data.get("choices") if isinstance(data, dict) else None
        message = choices[0].get("message", {}) if isinstance(choices, list) and choices else {}
        calls = message.get("tool_calls") if isinstance(message, dict) else None
        ok = isinstance(calls, list) and bool(calls)
        if ok:
            first = calls[0]
            fn = first.get("function", {}) if isinstance(first, dict) else {}
            print(f"{provider.upper()}_TOOL_CALL_NAME={fn.get('name','')}")
            print(f"{provider.upper()}_TOOL_CALL_ARGS={fn.get('arguments','')}")
        return ok, result.status


def inspect_stream(provider: str, model: str):
    request_id = f"op236-{provider}-{int(time.time()*1000)}"
    payload = {
        "providerID": provider,
        "model": model,
        "requestID": request_id,
        "messages": [{
            "role": "user",
            "content": "Call closedcode_probe with value PROBE_OK. Do not answer in normal text."
        }],
        "tools": [TOOL],
        "tool_choice": "auto",
        "temperature": 0,
        "max_tokens": 128,
        "stream": True,
    }
    result = post(payload, "text/event-stream")
    if isinstance(result, tuple):
        code, body = result
        print(f"{provider.upper()}_STREAM_HTTP={code}")
        print(f"{provider.upper()}_STREAM_BODY={body[:1200]}")
        return False, code
    names = []
    args = []
    with result:
        print(f"{provider.upper()}_STREAM_HTTP={result.status}")
        while True:
            raw = result.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data or data == "[DONE]":
                continue
            event = json.loads(data)
            if isinstance(event, dict) and "closedcode" in event:
                continue
            choices = event.get("choices") if isinstance(event, dict) else None
            choice = choices[0] if isinstance(choices, list) and choices else {}
            delta = choice.get("delta") if isinstance(choice, dict) else {}
            calls = delta.get("tool_calls") if isinstance(delta, dict) else None
            if not isinstance(calls, list):
                continue
            for call in calls:
                fn = call.get("function", {}) if isinstance(call, dict) else {}
                name = fn.get("name")
                argument_piece = fn.get("arguments")
                if isinstance(name, str) and name:
                    names.append(name)
                if isinstance(argument_piece, str) and argument_piece:
                    args.append(argument_piece)
    if names:
        print(f"{provider.upper()}_STREAM_TOOL_CALL_NAME={names[-1]}")
        print(f"{provider.upper()}_STREAM_TOOL_CALL_ARGS={''.join(args)}")
        return True, 200
    return False, 200


def main() -> int:
    overall = True
    for provider, model in CASES:
        ok, code = inspect_nonstream(provider, model)
        if not ok:
            print(f"{provider.upper()}_NONSTREAM_TOOL_CALL=NO")
            stream_ok, stream_code = inspect_stream(provider, model)
            print(f"{provider.upper()}_STREAM_TOOL_CALL={'YES' if stream_ok else 'NO'}")
            ok = stream_ok
            code = stream_code
        else:
            print(f"{provider.upper()}_NONSTREAM_TOOL_CALL=YES")
        if ok:
            print(f"{provider.upper()}_TOOL_CALL_CAPABILITY=GREEN")
        else:
            print(f"{provider.upper()}_TOOL_CALL_CAPABILITY=UNPROVEN")
            overall = False
    print("TOOL_CALL_PROBE_OVERALL=" + ("GREEN" if overall else "PARTIAL"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
