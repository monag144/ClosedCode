# HE8 Operation Resilience — Op193

Status: YELLOW / partial read-only diagnostic
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP193.direct-source-vs-compiled-layer-graph
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Local HEAD before/after: 6452767b80d69223a6f64fd633ffae7adf735cd2
Local worktree before/after: clean
Mutation: none

Purpose: compare direct-source LayerNode graph integrity with the installed compiled runtime implicated by the a.name resolver stack.

Findings:
- bun is not available on PATH in the current Termux shell, so the intended direct-source integrity probe did not execute.
- Installed OpenCode is /data/data/com.termux/files/usr/bin/opencode, version 1.18.31.
- Installed binary is a stripped 64-bit arm64 Android ELF built for Android 28.
- The binary contains the exact chunk name chunk-cc8ps5vb.js 60 times.
- The binary contains the LayerNode replacement error marker "Cannot replace" 5 times.
- No standalone chunk-cc8ps5vb.js file or source map was found in the searched locations.
- This proves the failing chunk identity is embedded in the installed compiled binary and is consistent with the runtime stack, but does not yet map offset 2:1659 to a specific source expression.

Next:
Use a bounded binary-string/context inspection around the embedded chunk and LayerNode markers to establish whether the failing resolve routine corresponds to LayerNode walk/resolve/replacement logic. Preserve Op195 for the mandatory twenty-operation review.

No product source, runtime, Relay, APK, Git working tree, or shared storage changed.
