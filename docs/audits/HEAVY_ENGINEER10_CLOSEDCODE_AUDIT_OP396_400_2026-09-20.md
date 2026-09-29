# Heavy Engineer 10 — ClosedCode Audit Ops396–400

Anchor: Op375, explicitly released by the Director.
Window: Ops396–400 exactly.
Timestamp UTC: `2026-09-20T03:25:50Z`
Pre-audit HEAD: `6b76d3d14ae8e15b297fb98786d97addf3d316f0`

## Operation ledger
- **Op396 — GREEN bounded check and targeted diagnosis.** The 0.8.11 qualification remained non-terminal at 273 completed tools, made zero tool progress during the bounded 30-second check, had all steering applied, zero errors and zero progress guardrails. Read-only control-flow proof established that `min-tools` was only post-hoc acceptance, steering 95 was advisory, provider tool calls continued the loop, varied tool activity could evade exact-cycle stagnation detection, and normal finalization depended on the provider eventually returning no tool calls.
- **Op397 — GREEN source fix.** Added opt-in explicit finalization control and advanced ClosedCode source to 0.8.12. Caller may specify `finalizeAfterTools`; after that many successful tools the backend emits a finalization event, removes tools from the provider request and requires synthesis from gathered evidence. Normal agent requests without the option remain unchanged. Harness gained `--finalize-after-tools` and finalization evidence tracking. Commit `6b76d3d14ae8e15b297fb98786d97addf3d316f0`.
- **Op398 — GREEN retirement/deployment.** The superseded 0.8.11 qualification already had a terminal cancelled summary when inspected, so Op398 sent no new cancellation and awarded no deep-cancellation credit. Historical summary: 279 completed tools, 208 unique signatures, 114 compactions, five late tool errors, zero final chars, terminal cancelled after 285 rounds. That pre-existing cancellation is consistent with the configured status-TTL path but its origin was not independently proven. Op398 then deployed 0.8.12 with exactly one healthy backend owner and verified the new harness configuration by dry run.
- **Op399 — GREEN launch.** Launched one fresh post-0.8.12 qualification using the exact original mission prompt SHA-256 `e8ceeda52864a587e61666384a88b7522d72987d0dc9173ab99066bc88c6c952`, `min-tools=100`, `finalize-after-tools=120`, steering thresholds 50/85/95, ASK mode, permission policy error/max zero, request `marathon-request-1789874680579`, session `marathon-session-1789874680579`.
- **Op400 — GREEN only if this audit/checkpoint operation commits and pushes successfully.** Mandatory Audit 396–400 and universal hard checkpoint. Snapshot only; no provider steering, cancellation, backend restart, product-source mutation, Android work, APK install, Relay mutation or new qualification is performed.

## Op400 live post-0.8.12 qualification snapshot
Classification: **RUNNING_POST_0_8_12_BOUNDED_FINALIZATION_QUALIFICATION**
Completed tools: **21**
Unique invocation signatures: **21**
Compactions: **0**
Errors: **0**
Steering posted: ****
Steering applied: **0**
Finalization triggered: **NO**
Final assistant chars: **0**
Exact backend owner count: **1**
Exact marathon owner count: **1**
Expected marathon PID present: **YES**

```json
{
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
            "pgid": 17138,
            "pid": 27380,
            "ppid": 1,
            "sid": 17138
        }
    ],
    "classification": "RUNNING_POST_0_8_12_BOUNDED_FINALIZATION_QUALIFICATION",
    "expectedMarathonPidPresent": true,
    "finalChars": 0,
    "finalSha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "marathonOwners": [
        {
            "args": [
                "python",
                "/data/data/com.termux/files/usr/bin/python",
                "/data/data/com.termux/files/home/ClosedCode/scripts/closedcode/qualify_agent_marathon.py",
                "--provider",
                "nvidia",
                "--model",
                "nvidia/nemotron-3-ultra-550b-a55b",
                "--root",
                "/data/data/com.termux/files/home/ClosedCode",
                "--autonomy",
                "ask",
                "--prompt-file",
                "/data/data/com.termux/files/usr/tmp/closedcode-op399-1789874679-27608/mission.txt",
                "--min-tools",
                "100",
                "--finalize-after-tools",
                "120",
                "--steer",
                "50:Deep steering checkpoint 50: continue the ORIGINAL eight-area mission unchanged. Do not rename, merge, substitute, or redefine any original area. In the final response also include exact line STEERING_50_SURVIVED=YES.",
                "--steer",
                "85:Deep steering checkpoint 85: preserve the ORIGINAL definition of done through all compactions and finish only after all eight original areas are evidenced. In the final response also include exact line STEERING_85_SURVIVED=YES.",
                "--steer",
                "95:Qualification completion steering: preserve the ORIGINAL eight-area mission exactly. The minimum is 100 meaningful successful tool actions. Close any specific remaining evidence gaps before the explicit finalization boundary. In the final response synthesize ORIGINAL_AREA_1 through ORIGINAL_AREA_8 and the exact preservation/read-only/definition-of-done/steering lines. Do not rename, merge, substitute, or redefine any original area.",
                "--permission-policy",
                "error",
                "--max-permissions",
                "0",
                "--socket-timeout",
                "3600",
                "--output",
                "/data/data/com.termux/files/usr/tmp/closedcode-op399-1789874679-27608/summary.json",
                "--status-port",
                "4214",
                "--status-token",
                "he10-op399-post-0812",
                "--status-ttl",
                "3600"
            ],
            "pgid": 17138,
            "pid": 27677,
            "ppid": 1,
            "sid": 17138
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
    "markersOkay": false,
    "runtimeAcceptanceGreen": false,
    "status": {
        "accepted": null,
        "autonomy": "ask",
        "cancelPosted": false,
        "compactions": 0,
        "completedTools": 21,
        "done": false,
        "errors": [],
        "finalizationTriggered": false,
        "guardrails": 0,
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "permissions": 0,
        "phase": "running",
        "pid": 27677,
        "provider": "nvidia",
        "requestID": "marathon-request-1789874680579",
        "runner": "closedcode-marathon",
        "sessionID": "marathon-session-1789874680579",
        "steeringApplied": 0,
        "steeringPosted": [],
        "terminal": null,
        "toolCounts": {
            "workspace_list": 9,
            "workspace_read": 12
        },
        "uniqueInvocationSignatures": 21
    },
    "summary": null,
    "summaryExists": false
}

```

## Audit assessment
The active acceptance experiment is now testing the repaired 0.8.12 completion contract rather than the superseded unbounded 0.8.11 behavior. Formal long-horizon acceptance remains unsettled until the new run reaches a trustworthy terminal state and the exact eight-area final-report contract is verified.

Transport reliability fix 0.8.11 remains incorporated. The 0.8.12 change is intentionally opt-in so ordinary ClosedCode agent behavior is not shortened merely because a tool count is reached.

Historical failures and superseded evidence remain preserved. No deep-cancellation qualification has yet been credited. Deep cancellation remains after long-horizon acceptance, followed by ASK/YOLO and then Android reassessment.
