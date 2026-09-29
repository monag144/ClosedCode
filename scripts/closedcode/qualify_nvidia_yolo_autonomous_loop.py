#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HOME = Path.home()
SCRATCH = HOME / ".cache" / f"closedcode-op263-nvidia-yolo-{time.time_ns()}"
SCRATCH.mkdir(parents=True)

def run(args, *, cwd=SCRATCH, check=True, capture=False):
    kwargs = {"cwd": str(cwd), "check": check}
    if capture:
        kwargs.update({"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT, "text": True})
    return subprocess.run(args, **kwargs)

run(["git", "init", "-q"])
run(["git", "config", "user.name", "ClosedCode Acceptance"])
run(["git", "config", "user.email", "closedcode@localhost"])

(SCRATCH / "calculator.py").write_text("""def add(a, b):
    # Intentional bug for autonomous repair acceptance.
    return a - b
""")
(SCRATCH / "test_calculator.py").write_text("""import unittest
from calculator import add

class CalculatorTests(unittest.TestCase):
    def test_add_positive(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative(self):
        self.assertEqual(add(-4, 7), 3)

if __name__ == "__main__":
    unittest.main()
""")
(SCRATCH / "test.sh").write_text("""#!/data/data/com.termux/files/usr/bin/sh
set -eu
python -m unittest -v
""")
os.chmod(SCRATCH / "test.sh", 0o755)
run(["git", "add", "calculator.py", "test_calculator.py", "test.sh"])
run(["git", "commit", "-qm", "seed failing calculator project"])

baseline = run(["./test.sh"], check=False, capture=True)
(SCRATCH / "baseline-test.txt").write_text(baseline.stdout)
print(f"BASELINE_TEST_RC={baseline.returncode}")
if baseline.returncode == 0 or "FAILED" not in baseline.stdout:
    raise SystemExit("baseline failure was not reproduced")

payload = {
    "providerID": "nvidia",
    "model": "nvidia/nemotron-3-ultra-550b-a55b",
    "sessionID": "op263-nvidia-yolo",
    "requestID": "op263-nvidia-yolo-request",
    "root": str(SCRATCH),
    "autonomy": "yolo",
    "messages": [{
        "role": "user",
        "content": (
            "Fix this project's bug autonomously. Before editing, inspect the project and run ./test.sh "
            "to observe the current failure. Diagnose the cause, make the smallest appropriate code edit, "
            "rerun ./test.sh until it passes, then inspect git status and git diff and report what changed. "
            "Do not ask for routine project-development approval. Do not modify anything outside this workspace."
        ),
    }],
}
req = urllib.request.Request(
    "http://127.0.0.1:4097/agent",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json; charset=utf-8", "Accept": "text/event-stream"},
    method="POST",
)

events = []
raw_path = SCRATCH / "agent-events.jsonl"
with urllib.request.urlopen(req, timeout=170) as response, raw_path.open("w", encoding="utf-8") as out:
    for raw in response:
        line = raw.decode("utf-8", "replace").rstrip("\n")
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if not data or data == "[DONE]":
            continue
        out.write(data + "\n")
        out.flush()
        try:
            events.append(json.loads(data))
        except Exception:
            pass

tool_events = []
permission_events = []
errors = []
final_text = []
complete = False
cancelled = False
for event in events:
    cc = event.get("closedcode") or {}
    typ = cc.get("type")
    if typ == "tool":
        tool_events.append({"name": cc.get("name"), "status": cc.get("status"), "detail": cc.get("detail")})
    elif typ == "permission":
        permission_events.append(cc)
    elif typ == "error":
        errors.append(cc.get("message", ""))
    if cc.get("complete"):
        complete = True
        cancelled = bool(cc.get("cancelled"))
    for choice in event.get("choices") or []:
        delta = choice.get("delta") or {}
        content = delta.get("content")
        if content:
            final_text.append(content)

summary = {
    "tool_events": tool_events,
    "permission_count": len(permission_events),
    "errors": errors,
    "complete": complete,
    "cancelled": cancelled,
    "final_text": "".join(final_text),
}
(SCRATCH / "agent-summary.json").write_text(json.dumps(summary, indent=2))

print("AGENT_COMPLETE=" + str(complete).upper())
print("AGENT_CANCELLED=" + str(cancelled).upper())
print("PERMISSION_EVENTS=" + str(len(permission_events)))
print("AGENT_ERRORS=" + json.dumps(errors))
print("TOOL_EVENT_COUNT=" + str(len(tool_events)))
print("TOOL_NAMES=" + ",".join(str(x.get("name")) for x in tool_events))
print("TOOL_STATUSES=" + ",".join(str(x.get("status")) for x in tool_events))
print("FINAL_TEXT=" + "".join(final_text).replace("\n", "\\n")[:2000])

if not complete or cancelled or permission_events or errors:
    raise SystemExit("agent terminal/autonomy contract failed")
names = [x.get("name") for x in tool_events]
if "shell" not in names:
    raise SystemExit("agent did not run project commands")
if not any(name in names for name in ("workspace_patch", "workspace_write")):
    raise SystemExit("agent did not edit the project")
if "git_status" not in names or "git_diff" not in names:
    raise SystemExit("agent did not inspect final Git state")

final = run(["./test.sh"], check=False, capture=True)
(SCRATCH / "final-test.txt").write_text(final.stdout)
print("FINAL_TEST_OUTPUT_BEGIN")
print(final.stdout, end="")
print("FINAL_TEST_OUTPUT_END")
print(f"FINAL_TEST_RC={final.returncode}")
if final.returncode != 0 or "OK" not in final.stdout:
    raise SystemExit("final tests are not green")

calculator = (SCRATCH / "calculator.py").read_text()
if "return a + b" not in calculator:
    raise SystemExit("expected bug repair not present")

print("FINAL_GIT_STATUS_BEGIN")
print(run(["git", "status", "--short"], capture=True).stdout, end="")
print("FINAL_GIT_STATUS_END")
print("FINAL_GIT_DIFF_BEGIN")
print(run(["git", "diff", "--", "calculator.py", "test_calculator.py", "test.sh"], capture=True).stdout, end="")
print("FINAL_GIT_DIFF_END")
print(f"SCRATCH_ROOT={SCRATCH}")
print("LIVE_NVIDIA_YOLO_AUTONOMOUS_DEVELOPMENT_LOOP=GREEN")
