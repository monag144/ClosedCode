# Heavy Engineer 10 — ClosedCode Audit Ops391–395

Anchor: Op375, explicitly released by the Director.
Window: Ops391–395 exactly.
Timestamp UTC: `2026-09-20T03:18:47Z`
Pre-audit HEAD: `24bb3d739d7f936d4c981be449d76570e6d25853`

## Operation ledger
- **Op391 — GREEN observation.** Same post-0.8.11 run advanced from 57 to 77 successful tools, 74 unique signatures and 39 compactions, with steering 50 applied once and zero errors.
- **Op392 — GREEN observation.** Run reached 96 successful tools, 86 unique signatures and 58 compactions. Steering 50, 85 and 95 were all posted/applied; zero errors, permissions and guardrails.
- **Op393 — GREEN capture operation; qualification still non-terminal.** Run advanced to 191 successful tools, 159 unique signatures and 91 compactions with all three steerings applied and zero errors. No summary or final assistant response existed.
- **Op394 — GREEN observation/capture; qualification still non-terminal.** Run advanced to 263 successful tools, 192 unique signatures and 114 compactions, still zero errors and no final response/terminal record.
- **Op395 — GREEN only if this audit/review operation commits and pushes successfully.** Read-only live snapshot plus governance persistence only.

## Op395 live snapshot
Classification: **RUNNING_UNCLASSIFIED**
Successful tools: **270**
Unique invocation signatures: **199**
Compactions: **114**
Errors: **0**
Steerings posted: **50,85,95**
Steerings applied: **3**
Final assistant chars: **0**
Exact backend owner count: **1**
Exact marathon owner count: **1**

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
    "markersOkay": false,
    "status": {
        "accepted": null,
        "autonomy": "ask",
        "cancelPosted": false,
        "compactions": 114,
        "completedTools": 270,
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
        "steeringApplied": 3,
        "steeringPosted": [
            50,
            85,
            95
        ],
        "terminal": null,
        "toolCounts": {
            "git_diff": 1,
            "git_log": 1,
            "git_status": 1,
            "workspace_list": 82,
            "workspace_read": 164,
            "workspace_search": 21
        },
        "uniqueInvocationSignatures": 199
    },
    "summary": null,
    "summaryExists": false
}

```

## Audit assessment
The 0.8.11 transport-resilience repair is strongly supported by sustained error-free activity far beyond both prior fatal provider-transport runs. Long-horizon acceptance is nevertheless **not GREEN until natural terminal completion and the exact final-report contract are proven**.

No product source, backend lifecycle, Android state, APK state, Relay state or OpenCode state was mutated in Ops391–395. Historical RED/YELLOW evidence remains preserved.
