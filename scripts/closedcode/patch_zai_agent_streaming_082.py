#!/usr/bin/env python3
from pathlib import Path

path = Path("scripts/closedcode/passthrough_server.py")
text = path.read_text(encoding="utf-8")

if 'VERSION = "0.8.1"' not in text:
    raise SystemExit("expected backend version 0.8.1")
text = text.replace('VERSION = "0.8.1"', 'VERSION = "0.8.2"', 1)

anchor = '''def auth_path() -> Path:
'''
if anchor not in text:
    raise SystemExit("auth_path anchor missing")

stream_code = r'''
def agent_provider_stream_completion(provider_id: str, upstream_url: str, key: str, payload: dict, request_id: str) -> dict:
    """Run an OpenAI-compatible streaming completion and rebuild one assistant message.

    Z.AI/GLM's free endpoint has historically accepted streaming requests while
    intermittently rate-limiting the equivalent non-streaming request.  The
    agent still needs a complete assistant message so tool calls can be
    executed round-by-round; this adapter accumulates SSE deltas into that
    normal message shape.
    """
    stream_payload = dict(payload)
    stream_payload["stream"] = True
    encoded = json.dumps(stream_payload, separators=(",", ":")).encode("utf-8")
    last_error = "provider streaming request failed"

    for attempt in range(1, PROVIDER_MAX_ATTEMPTS + 1):
        if active_stream_cancelled(request_id):
            raise RuntimeError("provider request cancelled")

        req = urlrequest.Request(
            upstream_url,
            data=encoded,
            method="POST",
            headers={
                "Authorization": "Bearer " + key,
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "User-Agent": "ClosedCode-Agent/" + VERSION,
            },
        )

        retryable = False
        try:
            upstream = urlrequest.urlopen(req, timeout=180)
            active_stream_set_upstream(request_id, upstream)
            role = "assistant"
            content_parts = []
            reasoning_parts = []
            tool_slots = {}
            finish_reason = None

            with upstream:
                status = getattr(upstream, "status", 200)
                if status < 200 or status >= 300:
                    last_error = "provider HTTP " + str(status)
                    retryable = status in RETRYABLE_PROVIDER_STATUS
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
                                slot = tool_slots.setdefault(
                                    index,
                                    {
                                        "id": "",
                                        "type": "function",
                                        "function": {"name": "", "arguments": ""},
                                    },
                                )
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
                    message = {"role": role}
                    if content_parts:
                        message["content"] = "".join(content_parts)
                    else:
                        message["content"] = None
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
                    return {
                        "choices": [
                            {
                                "index": 0,
                                "message": message,
                                "finish_reason": finish_reason,
                            }
                        ]
                    }
            active_stream_set_upstream(request_id, None)
        except urlerror.HTTPError as exc:
            active_stream_set_upstream(request_id, None)
            status = exc.code
            try:
                exc.read(131072)
            except Exception:
                pass
            last_error = "provider HTTP " + str(status)
            retryable = status in RETRYABLE_PROVIDER_STATUS
        except (urlerror.URLError, TimeoutError, OSError) as exc:
            active_stream_set_upstream(request_id, None)
            last_error = "provider transport error: " + exc.__class__.__name__
            retryable = True

        if not retryable or attempt >= PROVIDER_MAX_ATTEMPTS:
            raise RuntimeError(last_error + " after " + str(attempt) + " attempt(s)")
        if not wait_with_cancel(request_id, 0.75 * attempt):
            raise RuntimeError("provider request cancelled")

    raise RuntimeError(last_error)


'''
text = text.replace(anchor, stream_code + anchor, 1)

old = '''                        response = agent_provider_completion(
                            provider_id,
                            upstream_url,
                            key,
                            upstream_payload,
                            request_id,
                        )
'''
new = '''                        completion = (
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
'''
if old not in text:
    raise SystemExit("agent completion call anchor missing")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("PATCH_ZAI_AGENT_STREAMING_082=APPLIED")
print("VERSION_COUNT", text.count('VERSION = "0.8.2"'))
print("STREAM_FUNCTION_COUNT", text.count("def agent_provider_stream_completion("))
print("ZAI_SELECTION_COUNT", text.count('if provider_id == "zai"'))
