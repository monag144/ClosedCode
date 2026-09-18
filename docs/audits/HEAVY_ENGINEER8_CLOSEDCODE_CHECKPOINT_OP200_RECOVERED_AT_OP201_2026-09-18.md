# Heavy Engineer 8 ClosedCode — Op200 Checkpoint Recovered at Op201

Date: 2026-09-18 UTC
Mission: ClosedCode stabilization
Anchor: Op175
Required hard checkpoint: Op200
Checkpoint operation result: RED / PACKET_REJECTED
Recovery operation: Op201 GREEN / checkpoint evidence recovery only
Repository: /data/data/com.termux/files/home/ClosedCode
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Recovered HEAD: a9bee0b795d9a22f8eb0040f4b3e476e6020cf24
Recovered worktree: clean
Protected GPT-Termux-Relay implementation mutation: none established

## Governance accounting

Authoritative operation history preserves:
- Op181: never executed.
- Op183: never executed.
- Op200: consumed and PACKET_REJECTED.
- Op201: consumed as governance recovery only.

The four complete five-consumed-operation audits before the numeric Op200 checkpoint are:
1. Ops176-180.
2. Consumed Ops182,184,185,186,187.
3. Ops188-192.
4. Consumed Ops193-197.

The final pre-checkpoint substantive span is Ops198-200:
- Op198 GREEN / read-only.
- Op199 YELLOW / partial mutation.
- Op200 RED / PACKET_REJECTED.

That span contains only three consumed operations before the numeric hard checkpoint because the historical operation gaps prevent pretending there are five distinct consumed operations aligned to numeric 196-200. Op201 is checkpoint recovery and is recorded separately rather than misrepresented as substantive Audit-5 work.

## Audit 1 — Ops176-180

- Op176: terminal OK but historically unauthorized checkpoint crossing. Diagnosed both NVIDIA and OpenCode control tool paths failing before actual tool execution with TypeError involving a.name. No protected Relay mutation.
- Op177: read-only workspace/agent-init isolation.
- Op178: read-only prompt-loop versus shell isolation.
- Op179: read-only stack capture narrowed failure toward SystemPrompt/environment/location graph.
- Op180: read-only source archaeology.
Conclusion: failure was not NVIDIA-specific and did not originate in the local shell bridge.

## Audit 2 — Consumed Ops182,184,185,186,187

- Op182: governance recovery; overbroad/truncated output.
- Op184: RED objective failure due embedded Python SyntaxError.
- Op185: RED shell parse failure.
- Op186: GREEN authoritative ledger reconciliation; proved Op181 and Op183 were never executed.
- Op187: partial source inspection; reference sorting was initially suspected.
Conclusion: operation accounting restored; no mutation; reference-sort theory remained unproven.

## Audit 3 — Ops188-192

- Op188: normal Reference.Service materialization always supplies name.
- Op189: canonical Reference.Info.name is required Schema.String.
- Op190: Agent and SystemPrompt share the same location-service map path; Agent additionally waits for config-reference.
- Op191: LayerNode resolver/hoist/compile machinery contains many name dereferences.
- Op192: runtime logs show the same resolve -> a.name stack beneath SystemPrompt.environment, Agent.state, and Server.listen.
Conclusion: evidence shifted toward a shared compiled LayerNode/location-service graph failure.

## Audit 4 — Consumed Ops193-197

- Op193: partial; direct source Bun probe unavailable, compiled artifact provenance captured.
- Op194: inconclusive binary correlation.
- Op195: partial mandatory review evidence capture; full review completed via GitHub callbacks.
- Op196: GREEN device/GitHub reconciliation and build trace; main Bun build path proven to use splitting:true.
- Op197: RED / PACKET_REJECTED invalid Base64.
Conclusion: build-time splitting became a high-value hypothesis; no product runtime changed.

## Final checkpoint span — Ops198-200

### Op198 — GREEN / read-only
Recovered the earlier Android/Bionic A/B evidence:
- Bun 1.4.1 + splitting:true reproduced internal reference/agent failures.
- Same source + splitting:false passed.
- Bun 1.4.0 compiled control passed.
No mutation.

### Op199 — YELLOW / partial mutation
Attempted to change build.ts to explicit splitting:false and pushed commit 0a1331f6b0560663df57cdbbe0420a38153b3b8b.
Post-verification proved literal backslash-n text left the intended splitting:false inside a // comment, so the patch is malformed.
Live runtime was not replaced.
Historical artifacts were rediscovered.

### Op200 — RED / PACKET_REJECTED
Checkpoint packet rejected because command_b64 was invalid.
No shell execution and no mutation occurred.
Checkpoint evidence therefore required recovery under Op201.

## Op201 recovery evidence

- ClosedCode reconciled documentation-only remote changes and ended clean at a9bee0b795d9a22f8eb0040f4b3e476e6020cf24.
- Live OpenCode runtime remains 1.18.31, SHA256 3d082b4a3e75346de3a516d63a2e84cb812761478c9d97da65bedbac13c14b32.
- Backend is healthy on 127.0.0.1:4096.
- Known-good no-split artifact hash verified twice:
  02367cb9fa073ab37acadd6d4ca35db590f7fd4c775147541104ec604fee6e4e
  size 188,614,920 bytes.
- Bun 1.4.0 compiled control hash verified:
  26c7610ef19d4982dbd72ed3db7663813543bfcaf4d99834665df1f365bb9905.
- service_watchdog.py and socket_relay.py are running.
- Protected Relay implementation unchanged.
- Live runtime unchanged.

## Twenty-operation review carry-forward

The mandatory Op195 review concluded:
- Mission alignment remained valid.
- No protected Relay implementation mutation was established.
- The failure was not provider-specific.
- Ordinary Reference.Info construction did not support a naturally nameless reference.
- Shared LayerNode/location-service resolver failure became the favored root-cause area.
- Exact compiled-source mapping remained unproven at that time.
- Continuation was technically justified but required Director release.

Subsequent Ops196-201 materially strengthened the build-level conclusion:
- Current compiled CLI build path uses splitting:true.
- Historical A/B records prove splitting:false passes the Android/Bionic qualification gates.
- Surviving no-split binaries exactly match historical known-good hashes.
- Upstream research also shows analogous compiled graph failures on non-Android platforms, so the underlying defect is not proven Android-exclusive.

## Architecture pivot

The Director has now changed the ClosedCode delivery strategy for NVIDIA and GLM.

Instead of spending the next campaign deeply reverse-engineering OpenCode's compiled LayerNode/location-service graph, ClosedCode will implement a supported provider passthrough mode owned by the ClosedCode Termux backend/control layer and integrated into the Android client.

The pivot is recorded in:
docs/closedcode/CLOSEDCODE_PROVIDER_PASSTHROUGH_PIVOT_2026-09-18.md

This keeps:
- NVIDIA/Nemotron as first priority.
- Z.AI/GLM as second priority.
- OpenCode as a useful baseline/reference where functional.
- GPT-Termux-Relay protected and separate.

## Mutation accounting

Product source:
- Op199 changed packages/opencode/script/build.ts, but the change is malformed and does not establish active splitting:false.

Git/device state:
- Op196 and Op201 performed safe ff-only reconciliation of documentation/evidence commits.
- Final recovered worktree is clean.

Installed runtime:
- Unchanged throughout the checkpoint recovery.

Backend process:
- Healthy OpenCode 1.18.31 service running.

Protected Relay:
- No implementation mutation established.
- Runtime watchdog/socket relay processes active.

## Unresolved defects / unknowns

- build.ts still contains malformed comment text from Op199 and should be repaired or reverted when substantive work resumes.
- The live runtime is still the old compiled OpenCode binary, not the known-good no-split artifact.
- Real tool/file execution through the current OpenCode prompt path remains unqualified.
- The new passthrough mode is not yet implemented.
- Exact GLM live contract and tool behavior still need qualification.

## Proposed bounded next mission — Ops202-225

Only after fresh Director checkpoint release:
- Implement a minimal ClosedCode-owned passthrough protocol between Termux backend/control layer and Android client.
- Route NVIDIA first.
- Add Z.AI/GLM second.
- Preserve provider/model identity, streaming, cancellation, sessions, visible errors, permissions/tool events, and safe file/tool execution where capabilities permit.
- Integrate into the existing ClosedCode app, not a separate plumbing demo.
- Keep OpenCode-backed mode where useful.
- Do not reuse GPT-Termux-Relay implementation.
- Target officially usable passthrough by Op225.

## Checkpoint disposition

CHECKPOINT EVIDENCE RECOVERED AT OP201 AFTER OP200 PACKET_REJECTED.

HARD STOP ACTIVE.
No Operation 202+ substantive mission work, preparation, patching, scripting, packet construction, or runtime mutation until the Director explicitly releases the Op200 checkpoint.
