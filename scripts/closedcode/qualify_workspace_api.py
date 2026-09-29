#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SERVER = REPO / "scripts" / "closedcode" / "passthrough_server.py"
PORT = 4098
ROOT = Path.home() / ".cache" / "closedcode-op229-workspace-api"
HISTORY = ROOT / "history"


def request(method: str, path: str, body=None):
    url = f"http://127.0.0.1:{PORT}{path}"
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def main() -> int:
    if ROOT.exists():
        print("QUALIFY_ABORT_TEST_ROOT_EXISTS=YES")
        return 41
    ROOT.mkdir(parents=True, mode=0o700)
    os.chmod(ROOT, 0o700)

    env = os.environ.copy()
    env["CLOSEDCODE_PASSTHROUGH_HISTORY"] = str(HISTORY)
    log = ROOT / "server.log"
    with log.open("wb") as out:
        proc = subprocess.Popen(
            [sys.executable, str(SERVER), "--host", "127.0.0.1", "--port", str(PORT)],
            stdout=out,
            stderr=subprocess.STDOUT,
            env=env,
        )
    try:
        for _ in range(30):
            try:
                code, health = request("GET", "/health")
                if code == 200:
                    break
            except Exception:
                pass
            time.sleep(0.1)
        else:
            print("QUALIFY_SERVER_START=RED")
            return 42

        print("QUALIFY_HEALTH=" + json.dumps(health, separators=(",", ":")))
        if health.get("version") != "0.3.0":
            print("QUALIFY_VERSION=RED")
            return 43

        code, mk = request("POST", "/fs/mkdir", {"root": str(ROOT), "path": "workspace"})
        print("MKDIR=" + json.dumps({"code": code, "body": mk}, separators=(",", ":")))
        if code != 200:
            return 44

        content = "alpha\nbeta needle\ngamma\n"
        code, wr = request("POST", "/fs/write", {"root": str(ROOT), "path": "workspace/example.txt", "content": content})
        print("WRITE=" + json.dumps({"code": code, "body": wr}, separators=(",", ":")))
        if code != 200:
            return 45

        q = urllib.parse.urlencode({"root": str(ROOT), "path": "workspace/example.txt"})
        code, rd = request("GET", "/fs/read?" + q)
        print("READ=" + json.dumps({"code": code, "path": rd.get("path"), "bytes": rd.get("bytes")}, separators=(",", ":")))
        if code != 200 or rd.get("content") != content:
            return 46

        q = urllib.parse.urlencode({"root": str(ROOT), "query": "needle", "limit": "10"})
        code, sr = request("GET", "/fs/search?" + q)
        print("SEARCH=" + json.dumps({"code": code, "results": sr.get("results")}, separators=(",", ":")))
        if code != 200 or not any(x.get("path") == "workspace/example.txt" for x in sr.get("results", [])):
            return 47

        q = urllib.parse.urlencode({"root": str(ROOT), "path": "workspace"})
        code, ls = request("GET", "/fs/list?" + q)
        print("LIST=" + json.dumps({"code": code, "items": ls.get("items")}, separators=(",", ":")))
        if code != 200 or not any(x.get("name") == "example.txt" for x in ls.get("items", [])):
            return 48

        q = urllib.parse.urlencode({"root": str(ROOT), "path": "../escape.txt"})
        code, esc = request("GET", "/fs/read?" + q)
        print("ESCAPE=" + json.dumps({"code": code, "body": esc}, separators=(",", ":")))
        if code != 400 or "escapes workspace" not in esc.get("message", ""):
            return 49

        print("QUALIFY_WORKSPACE_API=GREEN")
        return 0
    finally:
        try:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
