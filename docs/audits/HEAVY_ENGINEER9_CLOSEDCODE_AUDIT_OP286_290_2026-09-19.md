# Heavy Engineer 9 — ClosedCode Audit — Ops286–290 — 2026-09-19

**Mission:** ClosedCode provider regression closure and Android interaction-parity discovery  
**Anchor:** Op275  
**Audit window:** Ops286–290  
**Canonical repo:** `~/ClosedCode` / `monag144/ClosedCode`  
**Branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`  
**Final HEAD:** `c9e1e5ffc88c2379cfe62f65f88ac033881ba6c9`  
**Worktree:** clean  
**Backend:** healthy `0.8.2`; NVIDIA=true; Z.AI=true  
**Protected infrastructure:** GPT-Termux-Relay untouched  
**APK installation:** none attempted  
**Next audit:** Op295  
**Twenty-operation review:** Op295  
**Hard checkpoint:** Op300

## Op286 — RED / COMMAND_FAILED

**Objective:** live NVIDIA agent sanity after the Z.AI selector change.

**Action/evidence:**
- fast-forwarded only the known Op281–285 audit document;
- backend health remained GREEN at `0.8.2`;
- static selector checks GREEN;
- local `/agent` returned HTTP 200/SSE;
- NVIDIA upstream failed after all three built-in attempts with `provider HTTP 500 after 3 attempt(s)`;
- no assistant text, no tool events.

**Mutation:** known audit-document Git fast-forward only; no source/runtime mutation.

**Classification:** historical RED. Result alone did not prove selector regression.

## Op287 — GREEN

**Objective:** isolate NVIDIA provider availability from agent/tool-payload compatibility.

**Evidence:**
- backend health GREEN `0.8.2`;
- exact-model raw NVIDIA request: HTTP 200 / `NVIDIA_RAW_OK`;
- exact-model request with current full `AGENT_TOOLS`: HTTP 200 / `NVIDIA_TOOLSHAPE_OK`;
- interpretation: Op286 upstream 500 was transient/recovered, not evidence of Z.AI-selector regression.

**Mutation:** none.

## Op288 — RED / COMMAND_FAILED

**Objective:** corrected end-to-end NVIDIA `/agent` requalification attempt.

**Failure:** embedded diagnostic Python contained a syntax error:
`SyntaxError: closing parenthesis '}' does not match opening parenthesis '('`.

The provider was not contacted.

**Mutation:** none.

## Op289 — GREEN

**Objective:** syntax-corrected end-to-end NVIDIA agent requalification.

**Evidence:**
- backend health GREEN `0.8.2`;
- exact model `nvidia/nemotron-3-ultra-550b-a55b`;
- local agent HTTP 200;
- SSE events: 2;
- tool events: 0;
- errors: none;
- assistant text: `NVIDIA_REGRESSION_OK`;
- complete=true;
- cancelled=false.

**Conclusion:** NVIDIA remains live-functional after the Z.AI selector repair.

**Mutation:** none.

## Op290 — GREEN

**Objective:** mandatory 286–290 read-only audit boundary plus Android interaction-parity discovery.

**Evidence:**
- canonical Android files identified:
  - `apps/closedcode-android/src/com/monag/closedcode/mobile/MainActivity.java`
  - `apps/closedcode-android/src/com/monag/closedcode/mobile/ClosedCodeApi.java`;
- current send behavior:
  - send-button click calls `abortPrompt()` while `promptRunning`;
  - otherwise it calls `sendPrompt()`;
- `sendPrompt()` explicitly returns when `promptRunning` is true;
- `setPromptRunning(true)` changes the Send button to a stop-square glyph and stop content description;
- `abortPrompt()` already supports provider request cancellation and ordinary session abort;
- provider streaming already maintains `activeProviderRequestId`, completion/cancel state, permission events, tool events, and streaming body;
- message bodies are individually text-selectable, but no session-wide copy/multi-card selection architecture was found in this bounded discovery.

**Mutation:** none.

## Window mutation ledger

- **Git/history:** Op286 fast-forwarded the previously persisted audit-document commit only.
- **Source:** no source mutation in Ops286–290.
- **Runtime:** no process/service mutation.
- **Providers:** NVIDIA transient upstream failure at Op286; provider/tool-shape checks GREEN at Op287; full agent requalification GREEN at Op289.
- **APK/package:** none.
- **Protected GPT-Termux-Relay:** no source/config mutation.
- **OpenCode runtime:** not replaced.

## Preserved failures

- Op286 remains RED / live upstream NVIDIA HTTP 500 after three attempts.
- Op288 remains RED / diagnostic packet-authoring syntax error.

Later success does not rewrite either failure.

## Provider stabilization conclusion

Provider stabilization is closed:
- Z.AI exact model `glm-4.7-flash` live-qualified at Op285 through the repaired upstream streaming path.
- NVIDIA exact model `nvidia/nemotron-3-ultra-550b-a55b` live-requalified at Op289.
- Backend remains healthy at `0.8.2`.

## Current Android interaction-parity blocker

The existing Android interaction model conflates Send and Stop:
- while idle, Send submits;
- while running, the same control becomes Stop;
- `sendPrompt()` refuses input during active work.

Therefore active-task steering cannot be implemented cleanly until:
1. Stop becomes a dedicated control;
2. composer/send remains usable while a task is active;
3. steering input is routed separately and queued/applied at a safe agent boundary;
4. original task state remains active;
5. cancellation remains explicit and independent.

Secondary parity targets remain:
- Copy Session;
- Telegram-style multi-card transcript selection/copy;
- prose streaming/latency polish after correctness.

## Governance

- Audit 286–290 complete and persisted non-Relay.
- Anchor: Op275.
- Next Relay op: Op291.
- Next audit and twenty-operation review: Op295.
- Hard checkpoint: Op300.
- No hard stop active.

## Next bounded target

Op291 should implement the smallest coherent interaction-parity foundation after fresh governance verification:
- dedicated Stop control;
- keep Send available while running;
- add backend/API steering endpoint or queue only if required by the exact current architecture;
- preserve current cancel behavior;
- compile/test Android and backend as appropriate;
- no APK installation through Relay.
