# Heavy Engineer 8 ClosedCode Audit — Ops216-220

Mission: ClosedCode NVIDIA/GLM passthrough delivery
Anchor: recovered Op200 checkpoint
Audit window: Ops216-220
Repository: /data/data/com.termux/files/home/ClosedCode
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Boundary operation: Op220

## Op216 — GREEN / governance recovery only
Recovered failed Op215 boundary state:
- governance docs reconciled
- port 4098 closed
- no isolated Op215 sidecar process
- ~/.cache/closedcode-op215-history exists mode 0700 with zero files
- live OpenCode healthy 1.18.31
- protected Relay watchdog and socket relay alive
- authoritative Ops211-216 ledger reconciled
- final worktree clean
- no protected Relay mutation
- no live OpenCode runtime replacement

## Op217 — RED / PACKET_REJECTED
Attempted compact NVIDIA 503 classification. Relay rejected invalid command_b64 before execution. No provider call, no sidecar/process/history/source/APK mutation.

## Op218 — GREEN / diagnostic qualification
Compared exact-model NVIDIA requests through sidecar 0.2.1:
- plain request: HTTP 200, exact model, stop, PASS
- session-aware request: HTTP 200, exact model, stop, PASS
- persisted history: user + assistant
- history root 0700
- history file 0600
Conclusion: Op215's HTTP 503 was not reproduced and is not attributable to sessionID/history persistence.

## Op219 — GREEN / qualification + Android build
Proved real two-turn persisted NVIDIA context:
- turn 1 HTTP 200: STORED
- turn 2 HTTP 200: recalled codeword COBALT-219
- rememberedCodeword=true
- history roles: user, assistant, user, assistant
- history root 0700 / file 0600
Android build GREEN:
- package com.monag.closedcode.mobile
- version 0.1.8-cleanroom
- APK bytes 95,572
- APK SHA256 2c4dd24cafe4de76cd0e19bcb15ffb536ef0553ba550a513ab1d8eb0430696fd
- final worktree clean
- no protected Relay mutation
- no live OpenCode runtime replacement

## Op220 — RED / COMMAND_FAILED / partial governance execution
Intended read-only audit/review capture.
Completed:
- branch/pre-state clean proof
- docs-only fast-forward to a3fa2bd3b0775d56b0c925aad7ff935ecf118846
Failed:
- PRODUCT_SOURCE_PROOF git log invocation received invalid standalone '-' argument
Not completed:
- product/runtime/ledger/final-state capture
No source/provider/APK/process mutation established.

## Window mutation summary

Source:
- No product source changes in Ops216-220.
- Product source entering this window remained the Op212-214 persistence/history implementation.

Git:
- direct GitHub audit/resilience docs advanced remote state
- Op216 and later operations reconciled those docs-only changes
- no product-code commit in this window

Runtime/config:
- live OpenCode remained 1.18.31
- no protected Relay config/source mutation
- temporary isolated sidecars used only in Ops218-219 validation and cleaned by their traps

Process/service:
- Op216 proved no leftover Op215 sidecar
- no persistent process/service mutation established in this window

Package/APK:
- Op219 rebuilt ClosedCode 0.1.8-cleanroom successfully
- SHA256 2c4dd24cafe4de76cd0e19bcb15ffb536ef0553ba550a513ab1d8eb0430696fd

Shared storage:
- normal build path updated /sdcard/Download/ClosedCode-cleanroom-v0.1.8-debug.apk at Op219
- no destructive action performed

## Preserved failures
- Op217 RED / PACKET_REJECTED
- Op220 RED / COMMAND_FAILED at governance boundary

## Current blocker
Governance recovery only. Op221 must positively recover the failed Op220 audit/review boundary state before substantive work resumes.

## Next bounded target after recovery
After Op221, remaining pre-Op225 delivery should prioritize:
- GLM live qualification/retry
- sidecar startup/lifecycle usability
- streaming/cancel behavior if safely deliverable
- final device-oriented proof
while preserving the Op225 hard checkpoint.

Protected infrastructure status:
No GPT-Termux-Relay implementation/config mutation in this window.

Governance status:
AUDIT MATERIAL RECORDED. Boundary-failure rule requires Op221 recovery before substantive continuation.
