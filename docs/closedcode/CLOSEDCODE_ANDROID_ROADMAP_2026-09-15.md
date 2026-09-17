> **STATUS: CLOSED / SUPERSEDED**
>
> Closed: 2026-09-17
> Superseded by: `docs/closedcode/CLOSEDCODE_DELIVERY_AND_STABILIZATION_ROADMAP_2026-09-17.md`
>
> Historical record only; no longer an active implementation roadmap.

# ClosedCode Android Roadmap — 2026-09-15

## Phase 0 — Fork foundation
- Preserve MIT license and upstream provenance.
- Establish ClosedCode charter and Android-first scope.
- Keep upstream `dev` available for comparison/sync.
- Move active ClosedCode engineering onto a dedicated downstream branch before source modification.

## Phase 1 — Reproduce known Android baseline
- Reproduce OpenCode 1.18.31 behavior on Android/Bionic from the fork.
- Preserve the known A/B controls:
  - Bun 1.4.0 compiled control.
  - Bun 1.4.1 + `splitting:true` failing control.
  - Bun 1.4.1 + `splitting:false` repaired control.
- Confirm `/api/config`, `/api/reference`, and `/api/agent` gates.
- Record hashes and build recipe.

## Phase 2 — Provider qualification
### NVIDIA / Nemotron
- Load credential without exposing it.
- Prove provider discovery.
- Prove `build` agent reaches `nvidia/nemotron-3-super-120b-a12b`.
- Receive a real response.
- Execute one harmless local tool operation.
- Test transient 429/5xx retry behavior separately from internal runtime failures.

### Z.AI / GLM
- Add/qualify a dedicated provider adapter.
- Prove basic chat completion.
- Prove tool-call compatibility.
- Normalize provider-specific streaming, errors, usage metadata, and model IDs.
- Ensure GLM incompatibilities cannot crash unrelated providers.

## Phase 3 — Diagnostics
Create an operator-visible diagnostic pipeline that can identify whether a failure occurred in:
1. UI/client request construction.
2. local server/runtime.
3. provider adapter.
4. remote provider/API.
5. model output parsing.
6. tool dispatch.
7. local execution.

Minimum safe telemetry:
- trace/correlation ID
- provider/model
- request stage
- HTTP status
- retries
- latency
- input/output/cache/reasoning tokens when provider supplies them
- tool name/stage without secret arguments
- sanitized error class/message

Never log credential values.

## Phase 4 — ClosedCode Android client
Build an Android-first client owned by this project.

Initial UI:
- Sessions
- Agent list
- Workspace selector
- Provider/model selector
- Credential management
- Build/Plan mode
- Tool approval prompts
- Diffs
- Diagnostics
- Runtime status

The UI must not require OpenCode Mobile.

## Phase 5 — Execution plane
Initially support a localhost runtime with Termux as the execution plane.

Requirements:
- explicit workspace boundary
- typed shell/file/Git operations
- permission profiles
- operation IDs/idempotence where replay could mutate state
- clear distinction between model retry and tool retry

Later evaluate bundling/managing the runtime directly from the APK only after the localhost architecture is stable.

## Phase 6 — Upstream strategy
Treat OpenCode as upstream source, not product authority.

For each upstream sync:
- inspect changes
- preserve ClosedCode provider contracts
- rebuild Android controls
- run provider qualification
- run diagnostics regression suite
- never inherit upstream build flags blindly

## Phase 7 — Product hardening
- credential storage via Android Keystore or equivalent secure mechanism
- bounded retry/backoff
- crash recovery
- session persistence
- provider failover only when explicitly configured
- qualification matrix for supported models/providers
- reproducible Android build pipeline
- signed APK release pipeline

## Acceptance target for first usable ClosedCode build
GREEN requires:
1. Android/Bionic runtime passes reference/agent endpoints.
2. NVIDIA Nemotron completes a real build-agent request.
3. One harmless tool operation succeeds.
4. GLM basic provider path succeeds.
5. ClosedCode Android client can create/connect to a session.
6. Diagnostics correctly identify at least runtime vs provider failure.
7. No secret leakage.
8. Reproducible build recipe is documented.
