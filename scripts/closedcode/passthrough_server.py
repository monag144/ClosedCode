#!/usr/bin/env python3
"""ClosedCode loopback provider passthrough.

Owns NVIDIA/Z.AI HTTP forwarding outside OpenCode's compiled agent graph.
Provider API keys remain in Termux's OpenCode auth store and are never
returned by this service.
"""
from __future__ import annotations

import argparse
import json
import os
import stat
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest

VERSION = "0.1.0"
MAX_BODY = 2 * 1024 * 1024
DEFAULT_AUTH_PATH = Path.home() / ".local" / "share" / "opencode" / "auth.json"
PROVIDERS = {
    "nvidia": {
        "env": "CLOSEDCODE_NVIDIA_BASE_URL",
        "default_base": "https://integrate.api.nvidia.com/v1",
    },
    "zai": {
        "env": "CLOSEDCODE_ZAI_BASE_URL",
        "default_base": "https://api.z.ai/api/paas/v4",
    },
}


def auth_path() -> Path:
    return Path(os.environ.get("OPENCODE_AUTH_PATH", str(DEFAULT_AUTH_PATH))).expanduser()


def load_auth() -> dict:
    path = auth_path()
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise RuntimeError(f"auth file permissions are too broad: {oct(mode)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("auth store root is not an object")
    return data


def provider_key(provider_id: str) -> str:
    entry = load_auth().get(provider_id)
    if not isinstance(entry, dict):
        raise RuntimeError(f"provider auth is not configured: {provider_id}")
    if entry.get("type") != "api":
        raise RuntimeError(f"unsupported auth type for passthrough provider: {provider_id}")
    key = entry.get("key")
    if not isinstance(key, str) or not key:
        raise RuntimeError(f"provider API key is missing: {provider_id}")
    return key


def provider_base(provider_id: str) -> str:
    spec = PROVIDERS[provider_id]
    return os.environ.get(spec["env"], spec["default_base"]).rstrip("/")


def provider_status() -> dict[str, bool]:
    try:
        data = load_auth()
    except Exception:
        return {provider: False for provider in PROVIDERS}
    result: dict[str, bool] = {}
    for provider in PROVIDERS:
        entry = data.get(provider)
        result[provider] = (
            isinstance(entry, dict)
            and entry.get("type") == "api"
            and isinstance(entry.get("key"), str)
            and bool(entry.get("key"))
        )
    return result


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "ClosedCodePassthrough/" + VERSION

    def log_message(self, fmt, *args):
        # Never log prompts, authorization headers, or provider response bodies.
        return

    def send_json(self, status: int, payload: dict):
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(
                200,
                {
                    "healthy": True,
                    "service": "closedcode-passthrough",
                    "version": VERSION,
                    "bind": "loopback-only",
                    "providers": provider_status(),
                },
            )
            return
        if self.path == "/providers":
            status = provider_status()
            self.send_json(
                200,
                {
                    "providers": [
                        {
                            "id": provider,
                            "connected": connected,
                            "baseUrlSource": "environment"
                            if os.environ.get(PROVIDERS[provider]["env"])
                            else "default",
                        }
                        for provider, connected in status.items()
                    ]
                },
            )
            return
        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_json(404, {"error": "not_found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError("invalid request size")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("request body must be an object")

            provider_id = payload.pop("providerID", None)
            if provider_id is None:
                provider_id = payload.pop("provider", None)
            else:
                payload.pop("provider", None)
            if provider_id not in PROVIDERS:
                raise ValueError("providerID must be nvidia or zai")

            model = payload.get("model")
            if not isinstance(model, str) or not model.strip():
                raise ValueError("model is required")
            messages = payload.get("messages")
            if not isinstance(messages, list) or not messages:
                raise ValueError("messages must be a non-empty array")

            key = provider_key(provider_id)
            upstream_url = provider_base(provider_id) + "/chat/completions"
            stream = bool(payload.get("stream", False))
            encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            req = urlrequest.Request(
                upstream_url,
                data=encoded,
                method="POST",
                headers={
                    "Authorization": "Bearer " + key,
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream" if stream else "application/json",
                    "User-Agent": "ClosedCode-Passthrough/" + VERSION,
                },
            )

            try:
                upstream = urlrequest.urlopen(req, timeout=180)
            except urlerror.HTTPError as exc:
                body = exc.read(131072).decode("utf-8", errors="replace")
                self.send_json(
                    exc.code,
                    {
                        "error": "upstream_http_error",
                        "providerID": provider_id,
                        "status": exc.code,
                        "body": body,
                    },
                )
                return

            with upstream:
                status = getattr(upstream, "status", 200)
                if stream:
                    self.send_response(status)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache, no-store")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    while True:
                        chunk = upstream.read(8192)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
                    self.close_connection = True
                    return

                body = upstream.read()
                self.send_response(status)
                self.send_header(
                    "Content-Type",
                    upstream.headers.get("Content-Type", "application/json"),
                )
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": "invalid_request", "message": str(exc)})
        except (FileNotFoundError, PermissionError, RuntimeError) as exc:
            self.send_json(503, {"error": "provider_unavailable", "message": str(exc)})
        except Exception as exc:
            self.send_json(
                502,
                {"error": "passthrough_failure", "message": exc.__class__.__name__},
            )


def check() -> int:
    path = auth_path()
    payload = {
        "service": "closedcode-passthrough",
        "version": VERSION,
        "authPresent": path.is_file(),
        "providers": provider_status(),
        "nvidiaBaseUrl": provider_base("nvidia"),
        "zaiBaseUrl": provider_base("zai"),
    }
    print(json.dumps(payload, separators=(",", ":")))
    return 0 if path.is_file() else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4097)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        return check()
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("passthrough service must bind to loopback")

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(
        json.dumps(
            {
                "event": "listening",
                "service": "closedcode-passthrough",
                "host": args.host,
                "port": server.server_address[1],
                "version": VERSION,
            },
            separators=(",", ":"),
        ),
        flush=True,
    )
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
