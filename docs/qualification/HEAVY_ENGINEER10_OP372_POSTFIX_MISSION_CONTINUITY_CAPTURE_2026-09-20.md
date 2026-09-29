# Heavy Engineer 10 — Existing Post-0.8.10 Mission-Continuity Capture

Captured during authorized Op376 after Op375 release.
Request: `marathon-request-1789864227137`
Session: `marathon-session-1789864227137`
Timestamp UTC: `2026-09-20T00:58:59Z`
Formal classification at capture: **RUNNING_UNCLASSIFIED**
Summary file present: **NO**
Expected marathon PID still exact/alive: **YES**

## Structural evidence

```json
{
    "allOriginalMissionMarkersExactlyOnce": false,
    "areaValuesNonEmpty": {
        "ORIGINAL_AREA_1_PROVIDER_REQUEST_LIFECYCLE=": false,
        "ORIGINAL_AREA_2_AUTONOMY_TOOLS_PERMISSIONS=": false,
        "ORIGINAL_AREA_3_CONTEXT_COMPACTION_CONSTRAINTS=": false,
        "ORIGINAL_AREA_4_STEERING_CANCEL_STAGNATION_TERMINAL=": false,
        "ORIGINAL_AREA_5_QUALIFICATION_INFRASTRUCTURE=": false,
        "ORIGINAL_AREA_6_ANDROID_INTEGRATION=": false,
        "ORIGINAL_AREA_7_RELAY_OPENCODE_BOUNDARY=": false,
        "ORIGINAL_AREA_8_DEFECTS_ROADMAP_ALIGNMENT=": false
    },
    "assistantMessageCount": 0,
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
    "expectedMarathonAliveAndExact": true,
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
        "/data/data/com.termux/files/usr/tmp/closedcode-op372-1789864226-10054/mission.txt",
        "--min-tools",
        "100",
        "--steer",
        "50:Deep steering checkpoint 50: continue the ORIGINAL eight-area mission unchanged. Do not rename, merge, substitute, or redefine any original area. In the final response also include exact line STEERING_50_SURVIVED=YES.",
        "--steer",
        "85:Deep steering checkpoint 85: preserve the ORIGINAL definition of done through all compactions and finish only after all eight original areas are evidenced. In the final response also include exact line STEERING_85_SURVIVED=YES.",
        "--permission-policy",
        "error",
        "--max-permissions",
        "0",
        "--socket-timeout",
        "3600",
        "--output",
        "/data/data/com.termux/files/usr/tmp/closedcode-op372-1789864226-10054/summary.json",
        "--status-port",
        "4211",
        "--status-token",
        "he10-op372-mission-continuity",
        "--status-ttl",
        "3600"
    ],
    "expectedMarathonPid": 10132,
    "fatalErrors": [],
    "finalChars": 0,
    "finalSha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "historyMessageCount": 0,
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
                "/data/data/com.termux/files/usr/tmp/closedcode-op372-1789864226-10054/mission.txt",
                "--min-tools",
                "100",
                "--steer",
                "50:Deep steering checkpoint 50: continue the ORIGINAL eight-area mission unchanged. Do not rename, merge, substitute, or redefine any original area. In the final response also include exact line STEERING_50_SURVIVED=YES.",
                "--steer",
                "85:Deep steering checkpoint 85: preserve the ORIGINAL definition of done through all compactions and finish only after all eight original areas are evidenced. In the final response also include exact line STEERING_85_SURVIVED=YES.",
                "--permission-policy",
                "error",
                "--max-permissions",
                "0",
                "--socket-timeout",
                "3600",
                "--output",
                "/data/data/com.termux/files/usr/tmp/closedcode-op372-1789864226-10054/summary.json",
                "--status-port",
                "4211",
                "--status-token",
                "he10-op372-mission-continuity",
                "--status-ttl",
                "3600"
            ],
            "pid": 10132
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
    "recoverableToolErrors": [],
    "requestID": "marathon-request-1789864227137",
    "runtimeAcceptanceGates": false,
    "sessionID": "marathon-session-1789864227137",
    "status": {
        "accepted": null,
        "autonomy": "ask",
        "cancelPosted": false,
        "compactions": 77,
        "completedTools": 153,
        "done": false,
        "errors": [],
        "guardrails": 0,
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "permissions": 0,
        "phase": "running",
        "pid": 10132,
        "provider": "nvidia",
        "requestID": "marathon-request-1789864227137",
        "runner": "closedcode-marathon",
        "sessionID": "marathon-session-1789864227137",
        "steeringApplied": 2,
        "steeringPosted": [
            50,
            85
        ],
        "terminal": null,
        "toolCounts": {
            "workspace_list": 27,
            "workspace_read": 93,
            "workspace_search": 33
        },
        "uniqueInvocationSignatures": 123
    },
    "summary": null,
    "summaryExists": false
}

```

## Final assistant report

No terminal final assistant report was present in durable session history at this capture point.

## Acceptance rule applied
GREEN requires more than 100 calls or `termination=completed`: the corrected harness runtime gates must pass, repeated compaction must be demonstrated, both steering checkpoints must survive, permissions must remain within policy, and all eight immutable original mission markers plus original definition-of-done/steering/read-only markers must survive exactly once with non-empty area findings in the actual final report.
