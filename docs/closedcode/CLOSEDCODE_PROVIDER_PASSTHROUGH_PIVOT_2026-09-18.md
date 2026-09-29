# ClosedCode Provider Passthrough Pivot — 2026-09-18

Status: DIRECTOR-RATIFIED ARCHITECTURE PIVOT / SUBSEQUENTLY PROVEN IN OPS201–225
Repository: monag144/ClosedCode
Branch: closedcode/android-cleanroom-opencode-mobile-20260916

## Director decision

ClosedCode will stop treating OpenCode's compiled agent/runtime graph as a requirement for NVIDIA and GLM operation.

For NVIDIA and GLM, ClosedCode adopts a first-class provider compatibility architecture: provider/model interaction and resulting stream/events originate in the Termux-side ClosedCode control layer and are presented to the Android application through the stable ClosedCode protocol/UI.

The intent is solution-first:
- do not spend the next campaign reverse-engineering OpenCode's LayerNode/location-service graph merely to make NVIDIA or GLM fit it;
- preserve OpenCode as a baseline/reference where useful;
- own the provider path in ClosedCode;
- keep GPT-Termux-Relay protected and separate;
- preserve normal OpenCode-backed behavior for providers/features where it is useful and functional;
- make the ClosedCode-owned provider path a supported first-class architecture for NVIDIA and GLM.

## Why the direction changed

The new research index at:
docs/research/OPENCODE_ANDROID_BIONIC_SPLITTING_RESEARCH_INDEX_2026-09-18.md

consolidates the earlier Agent-17/OpenCode archaeology and current HE8 work.

Established evidence:
- Bun 1.4.1 compiled with splitting:true reproduced the internal reference/agent failure.
- Same source with splitting:false passed the Android/Bionic qualification gates.
- Known-good no-split artifact SHA256:
  02367cb9fa073ab37acadd6d4ca35db590f7fd4c775147541104ec604fee6e4e
- Bun 1.4.0 compiled control SHA256:
  26c7610ef19d4982dbd72ed3db7663813543bfcaf4d99834665df1f365bb9905
- Current HE8 runtime-stack work independently converged on the shared LayerNode/location-service resolver.
- Upstream reports show the underlying compiled graph failure is not proven Android-exclusive.

Therefore the no-split artifact remains useful as a diagnostic/control, but fixing upstream/OpenCode internals is no longer the primary ClosedCode delivery strategy for NVIDIA/GLM.

## Proposed Ops201-225 mission

After the Op200 checkpoint is completed and released:

1. Define the minimal ClosedCode passthrough contract between Termux backend/control layer and Android client.
2. Route NVIDIA Nemotron through passthrough first.
3. Add Z.AI/GLM passthrough using the live provider contract.
4. Preserve streaming, cancellation, session identity, visible errors, provider/model identity, and safe tool/permission events.
5. Integrate passthrough cleanly into the current Android UI rather than building a second app.
6. Qualify real prompt/stream behavior on-device.
7. Qualify tool/file execution through the ClosedCode-owned Termux path where provider/model capabilities permit.
8. Retain OpenCode-backed mode where it remains functional/useful.
9. Avoid GPT-Termux-Relay implementation reuse.
10. Reach an officially usable passthrough implementation by Operation 225.

## Governance

Op200 remains the current checkpoint and has not yet been consumed at the time of this document.

This document records Director direction and proposed bounded continuation. It does not itself replace the required Op200 checkpoint evidence or the Heavy Engineer control harness.


## Architectural status after implementation

The implementation work completed through Op224 materially changed the status of this decision.

This is no longer merely a proposed emergency bypass around OpenCode.

The ClosedCode-owned provider compatibility architecture has now demonstrated:

- NVIDIA exact-model provider reachability;
- Android routing through the ClosedCode-owned path;
- secure per-session history;
- persisted multi-turn NVIDIA context continuity;
- Android history reload;
- Z.AI/GLM provider discovery and authenticated reachability;
- successful Z.AI streaming/SSE;
- persistent/idempotent startup ownership for the localhost provider service;
- separation from protected GPT-Termux-Relay implementation.

Remaining gaps such as Android-side streaming/cancellation parity and broader tool/file parity are product-completion work, not evidence that the architecture itself is an invalid workaround.

Accordingly, future documents should prefer terms such as:

- `ClosedCode-native provider compatibility architecture`;
- `ClosedCode provider adapter`;
- `ClosedCode-owned provider path`.

Historical references to `passthrough` or `sidecar` remain valid provenance and do not need to be rewritten out of old evidence.

Avoid describing the architecture as an awkward workaround, temporary hack, or second-class bypass unless referring specifically to its earlier experimental phase.
