# Heavy Engineer 10 — ClosedCode Audit Ops376–380

Mission: complete trustworthy long-horizon acceptance, then deep cancellation and ASK/YOLO qualification.
Anchor: Op375, explicitly released by the Director.
Window: Ops376–380 exactly.
Repository: `~/ClosedCode`
Branch: `closedcode/android-cleanroom-opencode-mobile-20260916`
Pre-audit HEAD: `8cab4d404e32f110b5a2a363690c9536a67277c4`
Timestamp UTC: `2026-09-20T01:10:42Z`

## Operation ledger
- **Op376 — GREEN.** Recovered the failed Op375 governance artifacts after explicit Director release and structurally inspected the existing post-0.8.10 request without replacing it. The run was still active at 153 successful tools, 123 unique invocation signatures, 77 compactions, both steering checkpoints applied, zero permissions/errors/guardrails at that capture. Persisted audit/checkpoint/capture evidence in commit `10e61e35f727894d16d6d4e607c3ee3b626f2080`.
- **Op377 — GREEN observation; underlying Op372 qualification classified RED.** Existing request had naturally terminated with `termination=error` after 169 successful tools, 139 unique signatures, 77 compactions, both steering applications, zero permissions/guardrails/cancellation, nine non-terminal workspace tool errors, and fatal `provider transport error: URLError after 4 attempt(s)`. No final report existed, so original eight-area continuity could not be awarded GREEN. No anti-churn steer was sent because the request was already done.
- **Op378 — GREEN.** Diagnosed Op372 as a transient/intermittent provider transport failure: current NVIDIA DNS resolved and unauthenticated HTTPS `/v1/models` returned HTTP 200 in 173 ms; backend remained healthy 0.8.10 with exactly one structural owner. Shut down only the already-finished Op372 status observer. Persisted diagnosis in commit `8cab4d404e32f110b5a2a363690c9536a67277c4`.
- **Op379 — GREEN.** Launched exactly one justified replacement NVIDIA qualification, request `marathon-request-1789866582505`, session `marathon-session-1789866582505`, PID `11247`, using a byte-for-byte copy of the original mission prompt SHA-256 `e8ceeda52864a587e61666384a88b7522d72987d0dc9173ab99066bc88c6c952`. Retained steerings at 50 and 85 and added bounded completion steering at 95. No other replacement request launched.
- **Op380 — GREEN only if this audit operation reaches terminal success.** Mandatory Audit 376–380 plus one read-only snapshot of the existing replacement request. No new provider request, cancellation, backend restart, Android mutation, APK install, Relay mutation, or OpenCode replacement.

## Op380 replacement snapshot
Classification: **RUNNING_UNCLASSIFIED**

```json
{
    "allRequiredMarkersExactlyOnceAndNonEmpty": false,
    "areaNonEmpty": {
        "ORIGINAL_AREA_1_PROVIDER_REQUEST_LIFECYCLE=": false,
        "ORIGINAL_AREA_2_AUTONOMY_TOOLS_PERMISSIONS=": false,
        "ORIGINAL_AREA_3_CONTEXT_COMPACTION_CONSTRAINTS=": false,
        "ORIGINAL_AREA_4_STEERING_CANCEL_STAGNATION_TERMINAL=": false,
        "ORIGINAL_AREA_5_QUALIFICATION_INFRASTRUCTURE=": false,
        "ORIGINAL_AREA_6_ANDROID_INTEGRATION=": false,
        "ORIGINAL_AREA_7_RELAY_OPENCODE_BOUNDARY=": false,
        "ORIGINAL_AREA_8_DEFECTS_ROADMAP_ALIGNMENT=": false
    },
    "backendOwners": [
        {
            "args": [
                "python",
                "/data/data/com.termux/files/usr/bin/python",
                "/data/data/com.termux/files/home/ClosedCode/scripts/closedcode/passthrough_server.py",
                "--host",
                "127.0.0.1",
                "--port",
                "4097"
            ],
            "pid": 22370
        }
    ],
    "classification": "RUNNING_UNCLASSIFIED",
    "expectedMarathonArgs": [
        "python",
        "/data/data/com.termux/files/usr/bin/python",
        "scripts/closedcode/qualify_agent_marathon.py",
        "--provider",
        "nvidia",
        "--model",
        "nvidia/nemotron-3-ultra-550b-a55b",
        "--root",
        "/data/data/com.termux/files/home/ClosedCode",
        "--autonomy",
        "ask",
        "--prompt-file",
        "/data/data/com.termux/files/usr/tmp/closedcode-op379-1789866582-11192/mission.txt",
        "--min-tools",
        "100",
        "--steer",
        "50:Deep steering checkpoint 50: continue the ORIGINAL eight-area mission unchanged. Do not rename, merge, substitute, or redefine any original area. In the final response also include exact line STEERING_50_SURVIVED=YES.",
        "--steer",
        "85:Deep steering checkpoint 85: preserve the ORIGINAL definition of done through all compactions and finish only after all eight original areas are evidenced. In the final response also include exact line STEERING_85_SURVIVED=YES.",
        "--steer",
        "95:Qualification completion steering: preserve the ORIGINAL eight-area mission exactly. The minimum is 100 meaningful successful tool actions; do not keep doing broad discovery merely to raise the count. If the original eight areas are already evidenced, use the next necessary actions only to close specific evidence gaps, then after the minimum is met synthesize the required ORIGINAL_AREA_1 through ORIGINAL_AREA_8 final report and exact preservation/read-only/definition-of-done/steering lines. Do not rename, merge, substitute, or redefine any original area.",
        "--permission-policy",
        "error",
        "--max-permissions",
        "0",
        "--socket-timeout",
        "3600",
        "--output",
        "/data/data/com.termux/files/usr/tmp/closedcode-op379-1789866582-11192/summary.json",
        "--status-port",
        "4212",
        "--status-token",
        "he10-op379-replacement",
        "--status-ttl",
        "3600"
    ],
    "finalChars": 0,
    "finalSha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "marathonOwners": [
        {
            "args": [
                "python",
                "/data/data/com.termux/files/usr/bin/python",
                "scripts/closedcode/qualify_agent_marathon.py",
                "--provider",
                "nvidia",
                "--model",
                "nvidia/nemotron-3-ultra-550b-a55b",
                "--root",
                "/data/data/com.termux/files/home/ClosedCode",
                "--autonomy",
                "ask",
                "--prompt-file",
                "/data/data/com.termux/files/usr/tmp/closedcode-op379-1789866582-11192/mission.txt",
                "--min-tools",
                "100",
                "--steer",
                "50:Deep steering checkpoint 50: continue the ORIGINAL eight-area mission unchanged. Do not rename, merge, substitute, or redefine any original area. In the final response also include exact line STEERING_50_SURVIVED=YES.",
                "--steer",
                "85:Deep steering checkpoint 85: preserve the ORIGINAL definition of done through all compactions and finish only after all eight original areas are evidenced. In the final response also include exact line STEERING_85_SURVIVED=YES.",
                "--steer",
                "95:Qualification completion steering: preserve the ORIGINAL eight-area mission exactly. The minimum is 100 meaningful successful tool actions; do not keep doing broad discovery merely to raise the count. If the original eight areas are already evidenced, use the next necessary actions only to close specific evidence gaps, then after the minimum is met synthesize the required ORIGINAL_AREA_1 through ORIGINAL_AREA_8 final report and exact preservation/read-only/definition-of-done/steering lines. Do not rename, merge, substitute, or redefine any original area.",
                "--permission-policy",
                "error",
                "--max-permissions",
                "0",
                "--socket-timeout",
                "3600",
                "--output",
                "/data/data/com.termux/files/usr/tmp/closedcode-op379-1789866582-11192/summary.json",
                "--status-port",
                "4212",
                "--status-token",
                "he10-op379-replacement",
                "--status-ttl",
                "3600"
            ],
            "pid": 11247
        }
    ],
    "markerCounts": {
        "DEFINITION_OF_DONE_REACHED=YES": 0,
        "ORIGINAL_AREA_1_PROVIDER_REQUEST_LIFECYCLE=": 0,
        "ORIGINAL_AREA_2_AUTONOMY_TOOLS_PERMISSIONS=": 0,
        "ORIGINAL_AREA_3_CONTEXT_COMPACTION_CONSTRAINTS=": 0,
        "ORIGINAL_AREA_4_STEERING_CANCEL_STAGNATION_TERMINAL=": 0,
        "ORIGINAL_AREA_5_QUALIFICATION_INFRASTRUCTURE=": 0,
        "ORIGINAL_AREA_6_ANDROID_INTEGRATION=": 0,
        "ORIGINAL_AREA_7_RELAY_OPENCODE_BOUNDARY=": 0,
        "ORIGINAL_AREA_8_DEFECTS_ROADMAP_ALIGNMENT=": 0,
        "ORIGINAL_EIGHT_AREAS_PRESERVED=YES": 0,
        "READ_ONLY_MISSION=YES": 0,
        "STEERING_50_SURVIVED=YES": 0,
        "STEERING_85_SURVIVED=YES": 0
    },
    "status": {
        "accepted": null,
        "autonomy": "ask",
        "cancelPosted": false,
        "compactions": 0,
        "completedTools": 11,
        "done": false,
        "errors": [],
        "guardrails": 0,
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "permissions": 0,
        "phase": "running",
        "pid": 11247,
        "provider": "nvidia",
        "requestID": "marathon-request-1789866582505",
        "runner": "closedcode-marathon",
        "sessionID": "marathon-session-1789866582505",
        "steeringApplied": 0,
        "steeringPosted": [],
        "terminal": null,
        "toolCounts": {
            "workspace_list": 7,
            "workspace_read": 4
        },
        "uniqueInvocationSignatures": 11
    },
    "summary": null,
    "summaryExists": false
}

```

## Window assessment
Mutations: documentation-only recovery/diagnosis commits; one authorized replacement provider qualification launch at Op379; shutdown of the already-terminal Op372 status observer. No product-source mutation in this window.
Preserved historical failures: Op350 RED, Op351 RED, Op363 RED, Op370 RED, Op373 RED, Op375 RED; historical Op357 remains YELLOW; Op372 fresh post-fix qualification remains RED because of terminal provider transport failure.
Protected state: GPT-Termux-Relay remains unmodified; exact backend owner count is one; OpenCode was not replaced; no APK installation through Relay/Termux occurred.
Current blocker: formal long-horizon acceptance depends on the single Op379 replacement reaching a trustworthy terminal result with the original eight-area report intact.
Governance: Audit 376–380 satisfied if this operation commits/pushes successfully. Next audit Op385; twenty-operation review Op395; universal hard checkpoint Op400.
