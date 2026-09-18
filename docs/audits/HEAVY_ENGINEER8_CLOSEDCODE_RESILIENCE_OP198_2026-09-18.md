# HE8 Operation Resilience — Op198

Status: GREEN / read-only
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP198.locate-build-environment-and-nonsplit-precedent
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
HEAD before/after: cefdd5a47be570a07884858940c4deda8de32ccd
Worktree before/after: clean
Mutation: none

Purpose:
Locate the proven Android/OpenCode build environment and any non-splitting precedent before modifying runtime build configuration.

Findings:
- Current primary packages/opencode build history includes the active splitting:true build.
- Existing ClosedCode documentation explicitly records prior proof:
  - docs/closedcode/CLOSEDCODE_ANDROID_ROADMAP_2026-09-15.md: Bun 1.4.1 + splitting:true failing control; Bun 1.4.1 + splitting:false repaired control.
  - docs/closedcode/CLOSEDCODE_PROJECT_CHARTER_2026-09-15.md: splitting:true reproduced internal /api/reference and /api/agent failure; same source with splitting:false passed those gates.
- Installed native runtime remains /data/data/com.termux/files/usr/bin/opencode version 1.18.31 with SHA256 3d082b4a3e75346de3a516d63a2e84cb812761478c9d97da65bedbac13c14b32.
- No usable bun executable was found in the searched Termux/proot locations, despite a populated ~/.bun install cache.
- freebuff-lab proot exists, but no bun executable was found there by this bounded search.
- No product source, runtime binary, package, protected Relay implementation, or shared storage changed.

Interpretation:
The no-splitting remedy is already historically proven for the same OpenCode failure class. The remaining blocker is operational: locate/recover a build-capable Bun environment or otherwise use the prior proven build procedure before changing/installing the runtime.

Next:
Use non-Relay GitHub evidence to recover the exact earlier build procedure if available. Reserve Op199 for the smallest justified repair/test before the Op200 checkpoint.
