# HE8 Operation Resilience — Op196

Status: GREEN / controlled reconciliation + read-only build trace
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP196.reconcile-and-build-trace
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916

Purpose: reconcile the clean device checkout to the authoritative GitHub evidence branch, then identify the actual OpenCode runtime build configuration relevant to the shared resolver failure.

Pre-state:
- local HEAD: 6452767b80d69223a6f64fd633ffae7adf735cd2
- worktree: clean
- remote HEAD: cefdd5a47be570a07884858940c4deda8de32ccd

Mutation:
- git fetch + ff-only merge advanced local HEAD to cefdd5a47be570a07884858940c4deda8de32ccd.
- Incoming changes were exclusively docs/audits/incidents created by Operation Resilience.
- No product-source changes were introduced by the reconciliation.
- Final worktree: clean.

Build findings:
- packages/opencode/script/build.ts contains Bun.build and explicitly sets splitting: true near lines 163-172.
- packages/opencode/script/build-node.ts also contains Bun.build.
- Root package declares packageManager bun@1.3.14.
- No bun/bunx executable is currently present on PATH.
- Installed runtime remains /data/data/com.termux/files/usr/bin/opencode version 1.18.31.
- Installed runtime SHA256 remains 3d082b4a3e75346de3a516d63a2e84cb812761478c9d97da65bedbac13c14b32.

Interpretation:
- The active source build configuration confirms code splitting is enabled for the compiled runtime path.
- This is materially relevant to the shared resolver/chunk failure hypothesis but does not yet prove splitting is causal.
- Before modifying build configuration, inspect the exact build block, build-node alternative, targets, outputs, and prior packaging/install mechanism.

Protected GPT-Termux-Relay implementation mutation: none.
