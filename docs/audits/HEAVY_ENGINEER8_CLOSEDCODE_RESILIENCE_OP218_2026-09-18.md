# HE8 Operation Resilience — Op218

Status: GREEN / diagnostic qualification
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP218.classify-nvidia-503-basic-vs-session
Relay status: OK
Exit code: 0

Purpose:
Classify whether Op215's NVIDIA HTTP 503 was caused by the new session-aware passthrough path or was transient upstream/provider behavior.

Repository/state:
- branch: closedcode/android-cleanroom-opencode-mobile-20260916
- docs-only remote reconciliation to a3c44f7544b469fe1957fcc3a97696bba59088f7
- final worktree clean
- no source mutation
- no live OpenCode runtime replacement
- no GPT-Termux-Relay mutation

Sidecar:
- isolated loopback sidecar healthy
- version 0.2.1
- nvidia configured=true
- zai configured=true

A/B result using exact model nvidia/nemotron-3-ultra-550b-a55b:
- basic request: HTTP 200, finishReason=stop, content=PASS
- otherwise identical request with sessionID: HTTP 200, finishReason=stop, content=PASS
- response model matched the exact requested NVIDIA model in both cases

Session persistence proof:
- GET /history returned exactly:
  - user: Reply exactly PASS.
  - assistant: PASS
- history root mode: 0700
- history file count: 1
- history file mode: 0600
- history file bytes: 87

Conclusion:
The Op215 HTTP 503 is not reproduced and is not attributable to sessionID forwarding or ClosedCode history persistence. The same sidecar code path succeeds both with and without session state. Treat Op215 as transient upstream/provider availability unless future evidence establishes a repeatable provider-side condition.

Next bounded target:
Run a real two-turn NVIDIA memory/context qualification using persisted history, then rebuild/hash the Android APK before the Op220 audit/review boundary.
