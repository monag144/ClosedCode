# Heavy Engineer 8 ClosedCode Twenty-Operation Review — Ops201-220

Mission: deliver a usable ClosedCode Android passthrough path for NVIDIA and Z.AI/GLM without mutating protected GPT-Termux-Relay infrastructure.
Anchor: recovered Op200 hard checkpoint
Review window: Ops201-220
Required boundary: Op220
Status: REVIEW MATERIAL RECORDED after Op220 COMMAND_FAILED; Op221 boundary recovery still required.

## Are we still executing the Director's mission?
Yes. Work remains centered on ClosedCode Android -> localhost ClosedCode/OpenCode control layer -> providers/models, with protected Relay kept separate. The campaign pivoted from trying to force NVIDIA/GLM through OpenCode's failing compiled agent graph to a ClosedCode-owned provider passthrough sidecar, which directly serves the requested usability objective.

## Scope/repository/branch/app/runtime/protected-infrastructure drift
No mission drift established.
- canonical repo remains monag144/ClosedCode
- branch remains closedcode/android-cleanroom-opencode-mobile-20260916
- app remains package com.monag.closedcode.mobile
- live OpenCode remains 1.18.31
- GPT-Termux-Relay remains protected and was not reused as ClosedCode implementation scaffolding
- no protected Relay implementation/config mutation occurred in this interval

## Assumption review
Changed assumption:
The earlier assumption that NVIDIA/GLM should traverse OpenCode's compiled Layer/agent graph is no longer valid for delivery. Prior A/B work established a compiled split-graph failure mode; the Director authorized a ClosedCode-owned passthrough pivot.

Validated assumption:
A loopback ClosedCode sidecar can reuse provider credentials from OpenCode auth storage while keeping provider secrets out of Android, and Android can route selected NVIDIA/Z.AI providers to that sidecar.

Newly validated:
Session-aware NVIDIA passthrough supports real multi-turn persisted context. Op219 proved two-turn recall with exact model nvidia/nemotron-3-ultra-550b-a55b.

## What the four five-operation audits established

### Ops201-205
- Op201 recovered Op200 checkpoint evidence.
- Op202 failed on wrong repo path without mutation.
- Op203 created the passthrough sidecar foundation.
- Op204 live-qualified NVIDIA non-stream and stream; Z.AI remained partial due live 429.
- Op205 failed transport at the audit boundary.
Established: the sidecar concept was viable and NVIDIA upstream worked independently of the failing OpenCode graph.

### Ops206-210
- Op206 recovered governance.
- Op207 integrated basic Android NVIDIA/Z.AI passthrough and built the APK.
- Ops208-210 were command_b64 transport rejections before execution.
Established: Android routing seam was working; transport reliability, not product code, blocked the first persistence attempts.

### Ops211-215
- Op211 recovered governance.
- Op212 added secure hashed session-history storage.
- Op213 added Android session/history API plumbing.
- Op214 made history/context persistence provider-atomic and wired Android history reload.
- Op215 failed during first live NVIDIA qualification with transient HTTP 503.
Established: persistence implementation was committed and structurally validated; the boundary failure was provider-side/live qualification, not a source failure.

### Ops216-220
- Op216 recovered boundary state.
- Op217 was a pre-execution transport rejection.
- Op218 proved both plain and session-aware NVIDIA requests HTTP 200 and correct history permissions.
- Op219 proved two-turn persisted recall and rebuilt the APK GREEN.
- Op220 failed only in governance capture due malformed git-log argument after docs-only reconciliation.
Established: NVIDIA passthrough persistence and multi-turn context are now evidence-backed in the rebuilt Android product.

## Material progress in Ops201-220
- ClosedCode-owned passthrough server created.
- NVIDIA exact model live-qualified.
- Z.AI endpoint/auth path established but still requires fresh qualification after earlier 429.
- Android routes NVIDIA/Z.AI selections to port 4097 sidecar.
- sessionID-aware passthrough implemented.
- hashed per-session history implemented with 0700 directory / 0600 file permissions.
- sessionID stripped before upstream provider forwarding.
- persisted prior turns are reinjected as provider context.
- successful non-stream user/assistant turns persist atomically.
- Android reloads passthrough history when reopening the session.
- Op219 proved exact-model two-turn memory continuity.
- Android 0.1.8-cleanroom rebuilt GREEN, 95,572 bytes, SHA256 2c4dd24cafe4de76cd0e19bcb15ffb536ef0553ba550a513ab1d8eb0430696fd.

## Failure classes preserved
- wrong-path command failure
- repeated rendered command_b64 transport rejection on large packets
- transient NVIDIA HTTP 503
- malformed governance git-log invocation at Op220
Historical RED events remain RED; none are rewritten by later success.

## Current gaps before Op225
- Op221 must recover Op220 governance boundary.
- Z.AI/GLM needs renewed live qualification beyond the earlier partial/429 result.
- sidecar operational lifecycle is not yet integrated into a simple ClosedCode startup path.
- Android passthrough remains non-streaming even though the sidecar can forward SSE.
- Android Stop still targets OpenCode abort rather than an active passthrough request.
- real-device end-to-end install/use proof remains desirable before checkpoint.
- tool execution/file-agent behavior through the passthrough path is not yet equivalent to full OpenCode agent mode.

## Review conclusion
The mission remains on target, with the largest technical risk substantially reduced: NVIDIA passthrough is no longer only a single-turn prototype; it has proven persisted multi-turn context and a GREEN Android build. The remaining Ops221-225 should avoid broad expansion and concentrate on governance recovery, GLM/provider parity, startup/usability, cancellation/streaming only where bounded, and final device-facing proof.

Next governance:
Op221 recovery only because Op220 failed at the audit/review boundary.
Next hard checkpoint: Op225.
