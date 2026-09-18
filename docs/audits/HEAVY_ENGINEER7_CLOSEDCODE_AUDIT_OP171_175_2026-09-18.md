# Heavy Engineer 7 — ClosedCode Audit Operations 171–175

Date: 2026-09-18

## Scope

This audit closes the five-operation window from Operation 171 through Operation 175 and records the Delivery-phase checkpoint state.

## Results

- **Op171 — PARTIAL.** The missing Android `PathInterpolator` import was repaired, `0.1.7-cleanroom` built successfully, and the installer was presented. NVIDIA and Z.AI were still unauthenticated at the start of this operation. The disposable runtime prompt probe was invalid because the curl request was malformed (`PROMPT_ASYNC_HTTP=000`), so its empty polling result was not admissible backend-failure evidence.
- **Op172 — RED/PARTIAL with important positive proofs.** Persistent `nvidia` and `zai` API credentials were present in OpenCode's auth store with mode `0600`; both providers became connected after canonical instance disposal. Exact NVIDIA target `nvidia/nemotron-3-ultra-550b-a55b` was present and active. `prompt_async` returned HTTP 204, proving transport/schema acceptance, but the first turn died in OpenCode's hidden automatic `title` agent with `TypeError: undefined is not an object (evaluating 'a.name')`.
- **Op173 — TRANSPORT REJECT.** Relay accessibility capture reported invalid/truncated JSON before a valid packet ID could be parsed. No shell execution and no device mutation occurred.
- **Op174 — GREEN.** A non-default-titled disposable session bypassed the OpenCode 1.18.31 automatic title-generation crash and produced a real NVIDIA Nemotron completion. This isolated the failure to the hidden title-agent path rather than NVIDIA authentication, the exact model, `prompt_async`, or the build agent. The compatibility repair was documented and wired into the Android client.
- **Op175 — PARTIAL DELIVERY CHECKPOINT.** `0.1.8-cleanroom` built successfully and installer handoff succeeded. The Android-equivalent titled-session sequence completed against exact NVIDIA Nemotron on the first poll. Provider state remained `nvidia,opencode,zai` connected. The disposable coding-tool qualification did not create `proof.txt` and exposed no tool event within 50 seconds, so tool/file execution remains the blocking core-delivery proof.

## Accepted delivery state at Op175

GREEN:
- persistent NVIDIA and Z.AI credentials in backend-owned auth storage;
- exact NVIDIA Nemotron discovery/connectivity;
- real NVIDIA prompt completion;
- client-side compatibility bypass for OpenCode's broken first-turn title generation;
- Android v0.1.8 build;
- non-default session creation and first-prompt title update;
- selected provider/model/agent/variant prompt wiring;
- visible send/stop state and abort wiring;
- automatic event reconnect wiring;
- session open/back motion;
- file browser and diff surfaces exist;
- installer handoff.

INCOMPLETE:
- real coding-tool invocation / file mutation proof;
- visible tool event from that real coding task;
- end-to-end file/diff verification after agent mutation;
- Z.AI exact `zai/glm-4.7-flash` remains absent from the current catalog even though provider auth is connected.

## Additional observation

The build qualification emitted an `aapt` architecture warning because the newest SDK build-tools directory contains an x86_64 `aapt`. This happened only in an optional APK-badging inspection after the Termux-native build had already completed successfully with `aapt2` and `zipalign`; it did not invalidate the produced APK.

## Governance

- Delivery phase Ops151–175 is complete as an operation window, but the product target is only PARTIAL because real tool/file execution is not yet qualified.
- GPT-Termux-Relay protected implementation mutation: **NONE**.
- Historical RED/PARTIAL/transport-reject events remain preserved.
- Stabilization Ops176–200 may proceed under the already-authorized roadmap; no new Director approval gate exists at Op175.

## Next bounded work

Start Op176 by inspecting the preserved backend log for the failed Op175 tool session `ses_f4ddbd413ffeWuzZNjGLsEaxas` and the NVIDIA model capability metadata. Determine whether the failure is model tool-call capability/behavior, permission/tool registration, or another runtime error before mutating Android or backend configuration.
