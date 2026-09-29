# HE8 Operation Resilience — Op204

Status: YELLOW / partial overall; NVIDIA passthrough GREEN
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP204.live-provider-passthrough-qualification
Relay status: OK
Exit code: 0

Repository:
- branch: closedcode/android-cleanroom-opencode-mobile-20260916
- reconciled documentation-only remote through babce2cbb3eda759f74647389796dd6532070a8f
- ignore-rule commit: 74f245994546bdee5342517d9bb3adc6a7bbc312
- final worktree: clean

Non-destructive cleanup:
- Added Python bytecode/cache ignore rules to .gitignore.
- No cache files were deleted.
- Prior scripts/closedcode/__pycache__/ residue is now ignored.

Security:
- Auth metadata proved both nvidia and zai entries are API-key backed.
- Secret values were not printed.
- Sidecar remained loopback-only.
- GPT-Termux-Relay mutation: none.
- Live OpenCode runtime replacement: none.

Live sidecar:
- /health: healthy=true, service=closedcode-passthrough, version=0.1.0, bind=loopback-only.
- /providers: nvidia connected=true; zai connected=true.

NVIDIA exact model:
- requested nvidia/nemotron-3-ultra-550b-a55b
- non-stream: HTTP 200, response model preserved exactly, finish_reason=stop, content=PASS
- stream: HTTP 200, six SSE events, ten content chars, [DONE] observed
Classification: GREEN for basic live passthrough + SSE transport.

Z.AI / GLM:
- requested glm-4.7-flash
- non-stream: HTTP 200, response model preserved, finish_reason=length, zero visible content under a deliberately tiny max_tokens=16 probe
- stream: HTTP 429 from upstream, no SSE events
Classification: PARTIAL. Authentication/connectivity is proven, but useful completion and streaming are not yet qualified.

Interpretation:
The central architecture pivot is now validated for NVIDIA: ClosedCode can bypass OpenCode's compiled agent graph and communicate with the exact Nemotron target through the ClosedCode-owned Termux sidecar. GLM requires follow-up provider-specific qualification rather than architectural reconsideration.
