# Heavy Engineer 10 — ClosedCode Audit Ops386–390

Mission: complete trustworthy long-horizon acceptance, then deep cancellation and ASK/YOLO qualification.
Anchor: Op375, explicitly released by the Director.
Window: Ops386–390 exactly.
Repository: `~/ClosedCode`
Branch: `closedcode/android-cleanroom-opencode-mobile-20260916`
Pre-audit HEAD: `f21460a395ea1e2f027d75e5d08b105549c367ba`
Timestamp UTC: `2026-09-20T02:34:45Z`

## Operation ledger
- **Op386 — GREEN runtime recovery.** Recovered the ClosedCode backend after Op384's failed restart using committed 0.8.11 source. Exact backend owner count returned to one, health reported 0.8.11 loopback-only with NVIDIA/Z.AI available, and deterministic deployed-source regressions proved bounded eight-attempt streaming/non-streaming transport recovery. Op384 remains permanently RED.
- **Op387 — GREEN launch.** Launched one fresh post-0.8.11 long-horizon NVIDIA qualification using the exact original mission prompt SHA-256 `e8ceeda52864a587e61666384a88b7522d72987d0dc9173ab99066bc88c6c952`, request `marathon-request-1789871015334`, session `marathon-session-1789871015334`. Scheduled original steering gates at 50 and 85 plus bounded completion steering at 95. No parallel marathon existed.
- **Op388 — GREEN observation.** Post-0.8.11 run progressed from five to 39 successful tools, 38 unique signatures and four compactions with zero permissions, guardrails or errors; still running and no final report yet.
- **Op389 — GREEN observation.** Same run progressed to 55 successful tools, 54 unique signatures and 18 compactions. Steering 50 was posted and applied exactly once; zero errors, permissions, guardrails or cancellation; run remained active.
- **Op390 — GREEN only if this audit operation reaches terminal success.** Mandatory Audit 386–390 plus one read-only current snapshot of the same qualification. No new request, steering, cancellation, backend restart, source mutation, Android mutation, APK installation, Relay mutation or OpenCode replacement.

## Op390 live qualification snapshot
Classification: **RUNNING_UNCLASSIFIED**
Exact backend owner count: **1**
Exact marathon owner count: **1**

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
                "/data/data/com.termux/files/usr/bin/python",
                "/data/data/com.termux/files/usr/bin/python",
                "/data/data/com.termux/files/home/ClosedCode/scripts/closedcode/passthrough_server.py",
                "--host",
                "127.0.0.1",
                "--port",
                "4097"
            ],
            "pid": 11366
        }
    ],
    "classification": "RUNNING_UNCLASSIFIED",
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
                "/data/data/com.termux/files/usr/tmp/closedcode-op387-1789871014-11776/mission.txt",
                "--min-tools",
                "100",
                "--steer",
                "50:Deep steering checkpoint 50: continue the ORIGINAL eight-area mission unchanged. Do not rename, merge, substitute, or redefine any original area. In the final response also include exact line STEERING_50_SURVIVED=YES.",
                "--steer",
                "85:Deep steering checkpoint 85: preserve the ORIGINAL definition of done through all compactions and finish only after all eight original areas are evidenced. In the final response also include exact line STEERING_85_SURVIVED=YES.",
                "--steer",
                "95:Qualification completion steering: preserve the ORIGINAL eight-area mission exactly. The minimum is 100 meaningful successful tool actions; do not keep doing broad discovery merely to raise the count. If the original eight areas are already evidenced, use only the next necessary actions to close specific evidence gaps, then after the minimum is met synthesize the required ORIGINAL_AREA_1 through ORIGINAL_AREA_8 final report and exact preservation/read-only/definition-of-done/steering lines. Do not rename, merge, substitute, or redefine any original area.",
                "--permission-policy",
                "error",
                "--max-permissions",
                "0",
                "--socket-timeout",
                "3600",
                "--output",
                "/data/data/com.termux/files/usr/tmp/closedcode-op387-1789871014-11776/summary.json",
                "--status-port",
                "4213",
                "--status-token",
                "he10-op387-post-0811",
                "--status-ttl",
                "3600"
            ],
            "pid": 11845
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
        "compactions": 19,
        "completedTools": 56,
        "done": false,
        "errors": [],
        "guardrails": 0,
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "permissions": 0,
        "phase": "running",
        "pid": 11845,
        "provider": "nvidia",
        "requestID": "marathon-request-1789871015334",
        "runner": "closedcode-marathon",
        "sessionID": "marathon-session-1789871015334",
        "steeringApplied": 1,
        "steeringPosted": [
            50
        ],
        "terminal": null,
        "toolCounts": {
            "workspace_list": 26,
            "workspace_read": 29,
            "workspace_search": 1
        },
        "uniqueInvocationSignatures": 55
    },
    "summary": null,
    "summaryExists": false
}

```

## Window assessment
Source mutation: none in Ops386–390. The 0.8.11 source fix was committed in Op383 and deployed/recovered in Op386.
Git mutation: Op390 governance documentation commit only, if successful.
Runtime/process mutation: Op386 restored one backend owner; Op387 launched one qualification observer/request. Ops388–390 are read-only observations except audit persistence.
Package/APK state: unchanged; no installation attempted. Shared storage: unchanged.
Historical qualification outcomes preserved: Op357 YELLOW; Op372 RED provider transport; Op379 RED provider transport. Historical REDs preserved at minimum: Op350, Op351, Op363, Op370, Op373, Op375, Op384.
Protected state: GPT-Termux-Relay remains alive/unmodified; ClosedCode remains the compatibility boundary; OpenCode is not required transit and was not replaced.
Current blocker: post-0.8.11 long-horizon qualification must reach a trustworthy terminal result and preserve all eight original areas before formal acceptance can be GREEN.
Governance: Audit 386–390 satisfied if this operation commits/pushes successfully. Next audit and twenty-operation review boundary: Op395. Universal hard checkpoint: Op400.
