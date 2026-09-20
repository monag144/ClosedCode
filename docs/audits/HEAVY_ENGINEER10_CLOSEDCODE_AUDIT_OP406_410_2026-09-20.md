# Heavy Engineer 10 — ClosedCode Audit Ops406–410

Timestamp UTC: `2026-09-20T04:45:17Z`
Window: **Ops406–410 exactly**
Pre-audit HEAD: `eb4050c2a93d0ebb4c7d33050a08b996d6f595a6`
Qualification request: `marathon-request-1789878626666`
Qualification session: `marathon-session-1789878626666`
Original mission SHA-256: `e8ceeda52864a587e61666384a88b7522d72987d0dc9173ab99066bc88c6c952`

## Operation ledger

### Op406 — GREEN bounded observation
- Same uninterrupted 0.8.13 qualification advanced from 35 to 54 successful tools during the observation.
- Reached 52 unique invocation signatures and 2 compactions.
- Steering 50 posted and applied successfully.
- Zero recorded errors; no finalization activity.

### Op407 — GREEN bounded observation
- Same run advanced from 55 to 79 successful tools.
- Reached 75 unique invocation signatures and 5 compactions.
- Steering 50 remained preserved and applied.
- Zero recorded errors; no finalization activity.

### Op408 — GREEN steering-85 milestone
- Same run advanced from 84 to 86 successful tools.
- Reached 80 unique invocation signatures and 6 compactions.
- Steering 85 posted and applied; steering 50 and 85 were therefore both proven on the uninterrupted run.
- Zero recorded errors.

### Op409 — GREEN finalization-boundary observation
- Same run advanced from 93 to exactly 120 successful tools.
- Reached 104 unique invocation signatures and 7 compactions.
- Steering 50, 85, and 95 all posted and all three applied.
- Zero recorded errors at boundary capture.
- 0.8.13 finalization triggered exactly at the configured 120-tool upper qualification boundary.
- At the Op409 snapshot synthesis was still running, with zero finalization retries and zero final assistant prose.

### Op410 — mandatory audit/finalization capture
Classification: **GREEN_CANDIDATE_LONG_HORIZON_ACCEPTANCE**
Completed tools: **120**
Unique invocation signatures: **104**
Compactions: **7**
Recorded errors: **1**
Tool errors: **1**
Steering posted: **50,85,95**
Steering applied: **3**
Finalization triggered: **YES**
Finalization retries: **1**
Final assistant chars: **7073**
Exact required marker multiplicity: **YES**
All eight original area values non-empty: **YES**
Runtime acceptance candidate: **YES**
Final-structure acceptance candidate: **YES**
Summary exists: **YES**
Expected marathon PID alive: **YES**
Exact marathon owner count: **1**
Exact backend owner count: **1**

## Captured qualification state

```json
{
    "areaValues": {
        "ORIGINAL_AREA_1_PROVIDER_REQUEST_LIFECYCLE=": "The provider/model selection and request lifecycle is implemented in `packages/core/src/session/runner/llm.ts` (SessionRunner). The runner resolves a model via `SessionRunnerModel.Service`, builds an `LLM.request` with system prompt, history translated via `toLLMMessages`, tool definitions from `ToolRegistry.materialize`, and streams exactly one `llm.stream(request)` per turn. Provider turn events are published incrementally via `createLLMEventPublisher` (publish-llm-event.ts) which persists assistant text, reasoning, tool calls, tool results, usage, and step finish events. Compaction can interrupt and restart the turn (ContinueAfterCompaction/ContinueAfterOverflowCompaction). Model configuration lives in `config/provider.ts` (ConfigProvider.Info with models, cost, limits, request overrides) and `catalog.ts` (ProviderRecord with mutable models). Provider identity and API surface are defined in `provider.ts` (ProviderV2.Info, MutableInfo, Api variants).",
        "ORIGINAL_AREA_2_AUTONOMY_TOOLS_PERMISSIONS=": "Autonomy boundaries are enforced through: (1) Agent step limits in `config/agent.ts` (ConfigAgent.Info.steps) honored in `llm.ts` via `isLastStep` gating toolChoice=\"none\" and MAX_STEPS_PROMPT; (2) Permission evaluation in `permission.ts` \u2014 `evaluate()` merges agent permissions, saved project rules, and wildcard matching with deny/allow/ask effects; `assert()` blocks on deny, prompts on ask via Deferred, and auto-allows on \"always\" with persistence; (3) Tool exposure in `tool/registry.ts` \u2014 `materialize(permissions)` filters wholly-disabled tools (deny on \"*\") and advertises definitions to the provider; local tool execution is settled durably via `ToolOutputStore` before continuation; (4) Tool registration is scoped via `ApplicationTools` (global) and `ToolRegistry.register` (location-scoped with finalizers). ASK/YOLO maps to permission `effect: \"ask\"` vs `effect: \"allow\"` rules.",
        "ORIGINAL_AREA_3_CONTEXT_COMPACTION_CONSTRAINTS=": "Compaction is implemented in `session/compaction.ts`. Settings come from `config/compaction.ts` (auto, prune, keep.tokens, buffer). `compactIfNeeded` estimates request tokens (system, messages, tools) against model context limit minus max(output, buffer). When triggered, `compactAfterOverflow` selects recent entries via `select()` (keeps DEFAULT_KEEP_TOKENS=8000 from tail), builds a summary prompt with `SUMMARY_TEMPLATE` (structured markdown sections) or `SUMMARY_UPDATE_INSTRUCTIONS` (merging prior summary), streams a summary with `maxTokens=SUMMARY_OUTPUT_TOKENS=4096`, and publishes `SessionEvent.Compaction.Started/Ended`. The compaction message becomes a `synthetic` user message with `<conversation-checkpoint>` wrapper. Token estimation uses `Token.estimate(JSON.stringify(value))`. Tool output truncation at 2000 chars. No evidence of synthetic mission checkpoint compaction or transitive steering retention beyond the summary template's \"Important Details\" section.",
        "ORIGINAL_AREA_4_STEERING_CANCEL_STAGNATION_TERMINAL=": "Steering is modeled as `SessionInput.Delivery = \"steer\" | \"queue\"` in `session/input.ts`. `promoteSteers` and `promoteNextQueued` move admitted inputs to promoted state and publish `SessionEvent.Prompted`. The runner loop in `llm.ts` checks `SessionInput.hasPending(db, sessionID, \"steer\")` and `\"queue\"` to decide continuation; `promotion` parameter controls whether steers reset step to 1. Cancellation/interruption is handled via `Effect.interrupt` propagation: `failInterruptedTools` marks pending/running tools as failed on resume; `FiberSet` tracks tool fibers; `Cause.hasInterrupts` clears fibers and fails unsettled tools. Stagnation guardrails: max steps (agent config), compaction overflow recovery (single retry via `runAfterOverflowCompaction`), and provider error termination. Terminal semantics: `SessionEvent.Step.Ended` with finish reason, `SessionEvent.Step.Failed` on error, and runner exits when no pending steer/queue and not forced.",
        "ORIGINAL_AREA_5_QUALIFICATION_INFRASTRUCTURE=": "Qualification infrastructure centers on the durable event system in `event.ts`: `EventV2.Service` provides `publish`, `subscribe`, `durable` streams, `replay`/`replayAll` with sequence/owner verification, and `project` for materialized views. Events are stored in `EventTable`/`EventSequenceTable` with aggregate IDs, sequences, and optional owner for replay safety. `SessionHistory` (`session/history.ts`) loads messages with compaction/epoch baseline filtering. `SessionStore` provides context for runner. `SessionInput` tracks admitted/promoted prompts with sequence ordering. No explicit marathon/qualification tooling, acceptance criteria runners, or regression coverage harnesses found in core; these appear to be external or in other packages.",
        "ORIGINAL_AREA_6_ANDROID_INTEGRATION=": "No Android-specific integration code found in `packages/core/src/`. The core is platform-agnostic (Node.js/Effect platform). Android request/event integration, session/transcript behavior, lifecycle/reconnect, and documented Android correctness gaps are not evidenced in this repository. Any Android integration likely lives in a separate package (e.g., `packages/android` or external) not present in the inspected workspace.",
        "ORIGINAL_AREA_7_RELAY_OPENCODE_BOUNDARY=": "The codebase imports `@opencode-ai/llm`, `@opencode-ai/schema`, `@opencode-ai/effect-drizzle-sqlite` as external dependencies. `packages/core/src/effect/app-node-platform.ts` wires `LLMClient`, `RequestExecutor`, `FetchHttpClient` \u2014 these are the provider compatibility layer owned by ClosedCode (via `@opencode-ai/llm`). No references to \"GPT-Termux-Relay\" or \"OpenCode\" as a separate runtime found in core. The `@opencode-ai/schema` types (session, event, permission, etc.) are the contract boundary. OpenCode appears as a schema namespace (`@opencode-ai/schema/*`) not a runtime dependency. Separation is maintained by ClosedCode owning the provider routing (`@opencode-ai/llm/route`) and core orchestration, while schemas are shared.",
        "ORIGINAL_AREA_8_DEFECTS_ROADMAP_ALIGNMENT=": "Known gaps documented inline: `llm.ts` header lists unchecked items \u2014 durable multi-node ownership, durable status marking, interruption handling after attachment replacement, bounded provider retries, repeated identical tool call bounds, policy-filtered tool definitions (MCP/plugin/structured-output), incremental snapshot/patch/retry persistence, scoped runtime context/progress/attachment normalization/plugins/cancellation settlement, durable continuation recovery with retry policy, final status settlement, delta coalescing with projected-history indexes, title/summary/compaction cleanup in background work. `compaction.ts` has TODO for remote/managed URI materialization before provider-history lowering. `tool/registry.ts` has TODO for plugin/MCP tool definitions. No formal issue documents or roadmap files found in core; defects are tracked as code comments."
    },
    "areasNonEmpty": true,
    "classification": "GREEN_CANDIDATE_LONG_HORIZON_ACCEPTANCE",
    "finalChars": 7073,
    "finalSha256": "8b0f129acb92768dd0abb35fb808c89e16cbe98ba731b64d4c64d4764a6e5d06",
    "markerCounts": {
        "DEFINITION_OF_DONE_REACHED=YES": 1,
        "ORIGINAL_AREA_1_PROVIDER_REQUEST_LIFECYCLE=": 1,
        "ORIGINAL_AREA_2_AUTONOMY_TOOLS_PERMISSIONS=": 1,
        "ORIGINAL_AREA_3_CONTEXT_COMPACTION_CONSTRAINTS=": 1,
        "ORIGINAL_AREA_4_STEERING_CANCEL_STAGNATION_TERMINAL=": 1,
        "ORIGINAL_AREA_5_QUALIFICATION_INFRASTRUCTURE=": 1,
        "ORIGINAL_AREA_6_ANDROID_INTEGRATION=": 1,
        "ORIGINAL_AREA_7_RELAY_OPENCODE_BOUNDARY=": 1,
        "ORIGINAL_AREA_8_DEFECTS_ROADMAP_ALIGNMENT=": 1,
        "ORIGINAL_EIGHT_AREAS_PRESERVED=YES": 1,
        "READ_ONLY_MISSION=YES": 1,
        "STEERING_50_SURVIVED=YES": 1,
        "STEERING_85_SURVIVED=YES": 1
    },
    "markersExact": true,
    "runtimeAcceptanceCandidate": true,
    "status": {
        "accepted": true,
        "autonomy": "ask",
        "cancelPosted": false,
        "compactions": 7,
        "completedTools": 120,
        "done": true,
        "errors": [
            "tool error: workspace_read"
        ],
        "finalChars": 7073,
        "finalSha256": "8b0f129acb92768dd0abb35fb808c89e16cbe98ba731b64d4c64d4764a6e5d06",
        "finalizationRetries": 1,
        "finalizationTriggered": true,
        "guardrails": 0,
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "permissions": 0,
        "phase": "done",
        "pid": 22583,
        "provider": "nvidia",
        "requestID": "marathon-request-1789878626666",
        "runner": "closedcode-marathon",
        "sessionID": "marathon-session-1789878626666",
        "steeringApplied": 3,
        "steeringPosted": [
            50,
            85,
            95
        ],
        "terminal": {
            "cancelled": false,
            "complete": true,
            "requestID": "marathon-request-1789878626666",
            "rounds": 123,
            "termination": "completed",
            "type": "complete"
        },
        "toolCounts": {
            "workspace_list": 25,
            "workspace_read": 95
        },
        "uniqueInvocationSignatures": 104
    },
    "structureAcceptanceCandidate": true,
    "summary": {
        "accepted": true,
        "autonomy": "ask",
        "cancelAt": null,
        "cancelPosted": false,
        "compactions": 7,
        "completedTools": 120,
        "elapsedSeconds": 853.798,
        "errorPolicy": "observe-and-report; terminal outcome and mission criteria determine acceptance",
        "errors": [
            "tool error: workspace_read"
        ],
        "finalChars": 7073,
        "finalSha256": "8b0f129acb92768dd0abb35fb808c89e16cbe98ba731b64d4c64d4764a6e5d06",
        "finalizationRetries": 1,
        "finalizationTriggered": true,
        "finalizeAfterTools": 120,
        "guardrails": 0,
        "model": "nvidia/nemotron-3-ultra-550b-a55b",
        "permissionActions": {},
        "permissions": 0,
        "promptSha256": "e8ceeda52864a587e61666384a88b7522d72987d0dc9173ab99066bc88c6c952",
        "provider": "nvidia",
        "requestID": "marathon-request-1789878626666",
        "sessionID": "marathon-session-1789878626666",
        "steeringApplied": 3,
        "steeringPosted": [
            50,
            85,
            95
        ],
        "steeringScheduled": [
            50,
            85,
            95
        ],
        "terminal": {
            "cancelled": false,
            "complete": true,
            "requestID": "marathon-request-1789878626666",
            "rounds": 123,
            "termination": "completed",
            "type": "complete"
        },
        "toolCounts": {
            "workspace_list": 25,
            "workspace_read": 95
        },
        "toolErrors": 1,
        "uniqueInvocationSignatures": 104
    },
    "summaryExists": true
}
```

## Final assistant response captured from persisted session history

```text
ORIGINAL_AREA_1_PROVIDER_REQUEST_LIFECYCLE=The provider/model selection and request lifecycle is implemented in `packages/core/src/session/runner/llm.ts` (SessionRunner). The runner resolves a model via `SessionRunnerModel.Service`, builds an `LLM.request` with system prompt, history translated via `toLLMMessages`, tool definitions from `ToolRegistry.materialize`, and streams exactly one `llm.stream(request)` per turn. Provider turn events are published incrementally via `createLLMEventPublisher` (publish-llm-event.ts) which persists assistant text, reasoning, tool calls, tool results, usage, and step finish events. Compaction can interrupt and restart the turn (ContinueAfterCompaction/ContinueAfterOverflowCompaction). Model configuration lives in `config/provider.ts` (ConfigProvider.Info with models, cost, limits, request overrides) and `catalog.ts` (ProviderRecord with mutable models). Provider identity and API surface are defined in `provider.ts` (ProviderV2.Info, MutableInfo, Api variants).

ORIGINAL_AREA_2_AUTONOMY_TOOLS_PERMISSIONS=Autonomy boundaries are enforced through: (1) Agent step limits in `config/agent.ts` (ConfigAgent.Info.steps) honored in `llm.ts` via `isLastStep` gating toolChoice="none" and MAX_STEPS_PROMPT; (2) Permission evaluation in `permission.ts` — `evaluate()` merges agent permissions, saved project rules, and wildcard matching with deny/allow/ask effects; `assert()` blocks on deny, prompts on ask via Deferred, and auto-allows on "always" with persistence; (3) Tool exposure in `tool/registry.ts` — `materialize(permissions)` filters wholly-disabled tools (deny on "*") and advertises definitions to the provider; local tool execution is settled durably via `ToolOutputStore` before continuation; (4) Tool registration is scoped via `ApplicationTools` (global) and `ToolRegistry.register` (location-scoped with finalizers). ASK/YOLO maps to permission `effect: "ask"` vs `effect: "allow"` rules.

ORIGINAL_AREA_3_CONTEXT_COMPACTION_CONSTRAINTS=Compaction is implemented in `session/compaction.ts`. Settings come from `config/compaction.ts` (auto, prune, keep.tokens, buffer). `compactIfNeeded` estimates request tokens (system, messages, tools) against model context limit minus max(output, buffer). When triggered, `compactAfterOverflow` selects recent entries via `select()` (keeps DEFAULT_KEEP_TOKENS=8000 from tail), builds a summary prompt with `SUMMARY_TEMPLATE` (structured markdown sections) or `SUMMARY_UPDATE_INSTRUCTIONS` (merging prior summary), streams a summary with `maxTokens=SUMMARY_OUTPUT_TOKENS=4096`, and publishes `SessionEvent.Compaction.Started/Ended`. The compaction message becomes a `synthetic` user message with `<conversation-checkpoint>` wrapper. Token estimation uses `Token.estimate(JSON.stringify(value))`. Tool output truncation at 2000 chars. No evidence of synthetic mission checkpoint compaction or transitive steering retention beyond the summary template's "Important Details" section.

ORIGINAL_AREA_4_STEERING_CANCEL_STAGNATION_TERMINAL=Steering is modeled as `SessionInput.Delivery = "steer" | "queue"` in `session/input.ts`. `promoteSteers` and `promoteNextQueued` move admitted inputs to promoted state and publish `SessionEvent.Prompted`. The runner loop in `llm.ts` checks `SessionInput.hasPending(db, sessionID, "steer")` and `"queue"` to decide continuation; `promotion` parameter controls whether steers reset step to 1. Cancellation/interruption is handled via `Effect.interrupt` propagation: `failInterruptedTools` marks pending/running tools as failed on resume; `FiberSet` tracks tool fibers; `Cause.hasInterrupts` clears fibers and fails unsettled tools. Stagnation guardrails: max steps (agent config), compaction overflow recovery (single retry via `runAfterOverflowCompaction`), and provider error termination. Terminal semantics: `SessionEvent.Step.Ended` with finish reason, `SessionEvent.Step.Failed` on error, and runner exits when no pending steer/queue and not forced.

ORIGINAL_AREA_5_QUALIFICATION_INFRASTRUCTURE=Qualification infrastructure centers on the durable event system in `event.ts`: `EventV2.Service` provides `publish`, `subscribe`, `durable` streams, `replay`/`replayAll` with sequence/owner verification, and `project` for materialized views. Events are stored in `EventTable`/`EventSequenceTable` with aggregate IDs, sequences, and optional owner for replay safety. `SessionHistory` (`session/history.ts`) loads messages with compaction/epoch baseline filtering. `SessionStore` provides context for runner. `SessionInput` tracks admitted/promoted prompts with sequence ordering. No explicit marathon/qualification tooling, acceptance criteria runners, or regression coverage harnesses found in core; these appear to be external or in other packages.

ORIGINAL_AREA_6_ANDROID_INTEGRATION=No Android-specific integration code found in `packages/core/src/`. The core is platform-agnostic (Node.js/Effect platform). Android request/event integration, session/transcript behavior, lifecycle/reconnect, and documented Android correctness gaps are not evidenced in this repository. Any Android integration likely lives in a separate package (e.g., `packages/android` or external) not present in the inspected workspace.

ORIGINAL_AREA_7_RELAY_OPENCODE_BOUNDARY=The codebase imports `@opencode-ai/llm`, `@opencode-ai/schema`, `@opencode-ai/effect-drizzle-sqlite` as external dependencies. `packages/core/src/effect/app-node-platform.ts` wires `LLMClient`, `RequestExecutor`, `FetchHttpClient` — these are the provider compatibility layer owned by ClosedCode (via `@opencode-ai/llm`). No references to "GPT-Termux-Relay" or "OpenCode" as a separate runtime found in core. The `@opencode-ai/schema` types (session, event, permission, etc.) are the contract boundary. OpenCode appears as a schema namespace (`@opencode-ai/schema/*`) not a runtime dependency. Separation is maintained by ClosedCode owning the provider routing (`@opencode-ai/llm/route`) and core orchestration, while schemas are shared.

ORIGINAL_AREA_8_DEFECTS_ROADMAP_ALIGNMENT=Known gaps documented inline: `llm.ts` header lists unchecked items — durable multi-node ownership, durable status marking, interruption handling after attachment replacement, bounded provider retries, repeated identical tool call bounds, policy-filtered tool definitions (MCP/plugin/structured-output), incremental snapshot/patch/retry persistence, scoped runtime context/progress/attachment normalization/plugins/cancellation settlement, durable continuation recovery with retry policy, final status settlement, delta coalescing with projected-history indexes, title/summary/compaction cleanup in background work. `compaction.ts` has TODO for remote/managed URI materialization before provider-history lowering. `tool/registry.ts` has TODO for plugin/MCP tool definitions. No formal issue documents or roadmap files found in core; defects are tracked as code comments.

ORIGINAL_EIGHT_AREAS_PRESERVED=YES
READ_ONLY_MISSION=YES
DEFINITION_OF_DONE_REACHED=YES
STEERING_50_SURVIVED=YES
STEERING_85_SURVIVED=YES\n```

## Audit assessment

This five-operation window contains no new source repair. It is qualification evidence for the 0.8.13 finalization-handshake repair completed in the preceding window.

The uninterrupted run has already established all scheduled steering checkpoints and the configured 120-successful-tool upper finalization boundary. The decisive remaining acceptance question at this audit is whether the terminal outcome is completed rather than cancelled/error, whether the harness accepts the run, and whether the persisted final response preserves all eight original areas plus the exact required markers.

The 120-tool setting remains an opt-in qualification upper boundary, not a universal production mission limit.

No deep-cancellation credit is granted by this run. Deep cancellation remains the next Core qualification phase only after long-horizon acceptance is settled.

Op410 itself does not cancel, restart, steer, redeploy, or modify product source/runtime. Its only repository mutation is this mandatory audit record.

Next mandatory five-operation audit: **Op415**.
Op415 is also the next formal twenty-operation review from anchor Op395.
Next universal hard checkpoint: **Op425**.
