# HE8 Operation Resilience — Op223

Status: GREEN / Z.AI qualification + picker catalog proof
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP223.qualify-zai-glm-and-picker-catalog
Relay status: OK
Exit code: 0

Repository/state:
- branch: closedcode/android-cleanroom-opencode-mobile-20260916
- docs-only remote reconciliation to c73110c3ca98227fec4ff4b03a60e5f2bc77ca1e
- final worktree clean
- no source mutation
- no live OpenCode runtime replacement
- no GPT-Termux-Relay mutation

Picker/catalog proof:
- nvidia connected=true
- exact NVIDIA model exposed: nvidia/nemotron-3-ultra-550b-a55b
- zai connected=true
- Z.AI models exposed include glm-4.7-flash and glm-4.7-flashx
- existing Android ComposerUiController consumes OpenCode connected provider/model catalog, so no separate passthrough picker implementation is required for these providers

Sidecar:
- isolated sidecar healthy
- version 0.2.1
- nvidia=true
- zai=true

Z.AI qualification:
- non-stream glm-4.7-flash returned HTTP 429
- upstream error code: 1305
- upstream message: service may be temporarily overloaded, try again later
- stream glm-4.7-flash returned HTTP 200
- SSE chunks arrived successfully
- stream included reasoning_content deltas and ended with [DONE]
- model field matched glm-4.7-flash
- finish_reason=length at the deliberately small 48-token limit

Interpretation:
Z.AI endpoint/auth/model routing is live and valid. Streaming is positively qualified. Non-stream remains intermittently provider-capacity-limited rather than structurally broken.

Governance:
Op224 is the final substantive operation before the mandatory Op225 hard checkpoint. Prioritize ClosedCode-owned sidecar startup/usability; do not expand scope unnecessarily.
