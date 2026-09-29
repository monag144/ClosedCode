# Heavy Engineer 7 — ClosedCode Audit Operations 166–170

Date: 2026-09-18

## Scope

This audit closes the five-operation window from Operation 166 through Operation 170.

## Results

- **Op166 — GREEN.** Literal valid-config bisection proved the incompatible project-config feature was `references`: either checked-in reference independently returned `/agent` HTTP 500, while `full_no_refs` returned HTTP 200. Provider, permission, MCP, and the exact tools block did not independently reproduce the failure.
- **Op167 — RED/PARTIAL.** The incompatible `references` entries were removed from the checked-in ClosedCode config and the troubleshooting records were synchronized, but the already-cached OpenCode workspace instance still returned `/agent` HTTP 500. The repository repair was valid; runtime state remained stale.
- **Op168 attempt 1 — PACKET_REJECTED.** Invalid `command_b64`; shell did not run.
- **Op168 reissue — GREEN.** Canonical instance disposal returned HTTP 200 / `true`, then `/agent` recovered to HTTP 200 with visible primary agents `build,plan`. Provider/model contracts were captured. The exact target `nvidia/nemotron-3-ultra-550b-a55b` exists and is active, but provider `nvidia` was not connected at this point.
- **Op169 — GREEN.** Built and presented `0.1.6-cleanroom` with live model/agent/effort controls. APK: `/sdcard/Download/ClosedCode-cleanroom-v0.1.6-debug.apk`, SHA-256 `79cb11f94bcebf73a88d0ff5823a6e1d3ac9e055e1b577e16ea79c8fe600ecb9`. Backend health and visible `build,plan` agent contract remained GREEN.
- **Op170 — RED/PARTIAL.** Useful pre-build probes completed: backend healthy; OpenCode auth store contained no provider credentials; NVIDIA and ZAI were not stored; the running backend inherited neither `NVIDIA_API_KEY` nor `ZAI_API_KEY`; only `opencode` was connected; the exact NVIDIA Nemotron target remained present but disconnected. The v0.1.7 session-motion source was synchronized, including a 240 ms `(0.22,1,0.36,1)` transition and prompt-refresh fallback, but compilation failed because `PathInterpolator` was referenced without importing `android.view.animation.PathInterpolator`. No v0.1.7 APK or runtime prompt qualification was produced.

## Current accepted state

- Workspace `references` incompatibility is repaired and the live OpenCode instance was canonically disposed/reloaded successfully.
- Android provider/model/agent controls are present in the v0.1.6 runtime and direct screenshots confirm the model picker and selected-state UI operate.
- The current blocker for the v0.1.7 motion build is a bounded Java import error, not an architecture failure.
- NVIDIA credentials are **not currently persisted into the backend used by ClosedCode**, despite the target model being discoverable in the provider catalog.
- ZAI / GLM credentials are also not configured.
- A real model completion through the ClosedCode backend remains unqualified.

## Governance

- GPT-Termux-Relay mutation during Ops166–170: **NONE**
- Historical RED/PARTIAL events remain RED/PARTIAL.
- Op170 did not reach installer handoff or the disposable runtime-prompt phase because the Android build failed first.
- The post-Op170 smallest repair is limited to adding the missing Android `PathInterpolator` import; no broader redesign is justified.

## Next bounded work

Rebuild the already-authored v0.1.7 transition source after the missing import repair. Re-run the credential-presence check, qualify a disposable prompt against the currently connected OpenCode provider as a transport/control proof, and present the installer if the build is GREEN. NVIDIA should be connected through the backend credential store separately; do not embed or print API keys in ClosedCode logs or Relay output.
