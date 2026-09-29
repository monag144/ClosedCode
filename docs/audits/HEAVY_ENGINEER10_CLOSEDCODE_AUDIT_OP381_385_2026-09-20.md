# Heavy Engineer 10 — ClosedCode Audit Ops381–385

Mission: complete trustworthy long-horizon acceptance, then deep cancellation and ASK/YOLO qualification.
Anchor: Op375, explicitly released by the Director.
Window: Ops381–385 exactly.
Repository: `~/ClosedCode`
Branch: `closedcode/android-cleanroom-opencode-mobile-20260916`
Pre-audit HEAD: `a32353e97f61933780c2441982a3a8595d01e38e`
Timestamp UTC: `2026-09-20T02:22:03Z`

## Operation ledger
- **Op381 — GREEN observation; underlying Op379 qualification classified RED.** The single replacement marathon began healthy but terminated at 44 successful tools, 41 unique signatures, six compactions, zero permissions/guardrails/cancellation, one non-terminal workspace-list error, and fatal `provider transport error: URLError after 4 attempt(s)`. No final assistant report existed and no steering threshold had yet been reached.
- **Op382 — GREEN root-cause proof.** Deterministic local regression proved the 0.8.10 transport policy allowed only four attempts with 0.75, 1.5, and 3.0 second delays, totaling 5.25 seconds. Three transient failures followed by success recovered on attempt four; four transient failures caused fatal termination before a possible fifth success. The fatal error also discarded the underlying `URLError.reason`. No provider request or source mutation occurred.
- **Op383 — GREEN source fix.** ClosedCode passthrough advanced source 0.8.10 → 0.8.11, increasing bounded transport attempts 4 → 8, total transient retry delay 5.25 → 29.25 seconds, and preserving bounded underlying transport-cause text. Deterministic streaming and non-streaming regressions proved recovery after seven failures and bounded failure after eight. Commit `a32353e97f61933780c2441982a3a8595d01e38e`. Deployed backend intentionally remained 0.8.10.
- **Op384 — RED / COMMAND_FAILED with partial runtime mutation.** The operation terminated the sole deployed backend PID `22370` while attempting deployment. Automatic owner recreation did not occur. The manual fallback incorrectly replayed captured `/proc` argv containing both display-name `python` and interpreter path `/data/data/com.termux/files/usr/bin/python`; no valid backend process resulted. The operation exited 79 with `ERROR=BACKEND_DID_NOT_RESTART`. Source/Git state remained at committed 0.8.11. Preserve Op384 permanently as RED.
- **Op385 — GREEN only if this governance operation reaches terminal success.** Mandatory Audit 381–385 plus read-only reconstruction of the partial Op384 runtime state. No backend restart, provider request, product-source mutation, Android mutation, APK installation, Relay mutation, or OpenCode replacement is performed in Op385.

## Op385 reconstructed runtime state
Classification: **BACKEND_DOWN_AFTER_OP384_PARTIAL_RESTART_FAILURE**
Exact backend owner count: **0**
Port 4097: **CLOSED**
Exact marathon observer owner count: **0**
Port 4212: **CLOSED**

```json
{
    "backendOwners": [],
    "health4097": {
        "error": "URLError",
        "message": "<urlopen error [Errno 111] Connection refused>",
        "ok": false
    },
    "marathonOwners": [],
    "port4097Open": false,
    "port4212Open": false,
    "runtimeClassification": "BACKEND_DOWN_AFTER_OP384_PARTIAL_RESTART_FAILURE",
    "status4212": {
        "error": "URLError",
        "message": "<urlopen error [Errno 111] Connection refused>",
        "ok": false
    }
}

```

## Window assessment
Source mutation: Op383 only, committed/pushed 0.8.11 transport-resilience fix.
Runtime mutation: Op384 terminated the previous 0.8.10 backend and failed to restore it; this partial mutation is preserved exactly. Op385 is read-only except governance documentation/Git persistence.
Historical qualification outcomes remain unchanged: Op357 YELLOW; Op372 RED provider-transport failure; Op379 RED provider-transport failure.
Historical REDs preserved at minimum: Op350, Op351, Op363, Op370, Op373, Op375, Op384.
Protected state: GPT-Termux-Relay remains alive and unmodified; no APK installation through Relay/Termux; OpenCode not replaced.
Current blocker: restore the ClosedCode backend correctly from committed 0.8.11 source, prove singular healthy ownership, then resume long-horizon acceptance. Do not launch another marathon while backend deployment is unresolved.
Governance: Audit 381–385 satisfied if this commit/push succeeds. Next audit Op390; twenty-operation review Op395; hard checkpoint Op400.
