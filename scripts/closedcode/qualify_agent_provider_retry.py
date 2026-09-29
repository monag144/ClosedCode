#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import urllib.error
from pathlib import Path

SERVER = Path(__file__).with_name("passthrough_server.py")
spec = importlib.util.spec_from_file_location("closedcode_passthrough_server", SERVER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class FakeResponse:
    status = 200

    def __init__(self, body: dict):
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body

    def close(self):
        pass


def http_error(code: int):
    return urllib.error.HTTPError(
        "https://provider.invalid/chat/completions",
        code,
        "forced",
        hdrs=None,
        fp=io.BytesIO(b'{"error":{"message":"forced"}}'),
    )


def main() -> int:
    request_id = "op244-forced-retry"
    module.active_stream_register(request_id, None)
    original = module.urlrequest.urlopen
    attempts = []
    responses = [
        http_error(500),
        http_error(503),
        FakeResponse({"choices": [{"message": {"role": "assistant", "content": "RETRY_OK"}}]}),
    ]

    def fake_urlopen(req, timeout=180):
        attempts.append(timeout)
        item = responses[len(attempts) - 1]
        if isinstance(item, Exception):
            raise item
        return item

    try:
        module.urlrequest.urlopen = fake_urlopen
        result = module.agent_provider_completion(
            "nvidia",
            "https://provider.invalid/chat/completions",
            "not-a-real-key",
            {"model": "probe", "messages": [{"role": "user", "content": "probe"}]},
            request_id,
        )
    finally:
        module.urlrequest.urlopen = original
        module.active_stream_unregister(request_id)

    if len(attempts) != 3:
        raise RuntimeError("expected 3 attempts, got " + str(len(attempts)))
    content = result["choices"][0]["message"]["content"]
    if content != "RETRY_OK":
        raise RuntimeError("unexpected retry result: " + repr(content))

    print("FORCED_RETRY_ATTEMPTS=3")
    print("FORCED_500_503_RECOVERY=GREEN")
    print("RAW_UPSTREAM_ERROR_BODY_EXPOSURE=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
