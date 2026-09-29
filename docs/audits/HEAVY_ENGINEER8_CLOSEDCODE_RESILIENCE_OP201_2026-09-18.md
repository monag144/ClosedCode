# HE8 Operation Resilience — Op201

Status: GREEN / checkpoint recovery only
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP201.recover-op200-checkpoint-evidence
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Final local HEAD: a9bee0b795d9a22f8eb0040f4b3e476e6020cf24
Final worktree: clean

Purpose:
Recover the checkpoint evidence that Op200 failed to capture after Op200 was PACKET_REJECTED.

Recovery actions:
- Reconciled documentation-only remote changes by ff-only merge.
- No non-doc remote change was accepted.
- Captured current malformed build-source state.
- Verified installed live runtime identity and size.
- Verified historical no-split/control artifact hashes and sizes.
- Captured backend health.
- Captured protected Relay process/path state.
- Recovered authoritative Relay ledger entries for Ops196-201.

Key evidence:
- Live runtime:
  - /data/data/com.termux/files/usr/bin/opencode
  - version 1.18.31
  - SHA256 3d082b4a3e75346de3a516d63a2e84cb812761478c9d97da65bedbac13c14b32
  - size 141,560,072 bytes
- Backend health: {"healthy":true,"version":"1.18.31"}
- Known-good no-split artifact verified at:
  /data/data/com.termux/files/usr/tmp/he-opencode-op22/build/packages/opencode/dist/opencode-android-arm64-he-op43-nosplit/bin/opencode
  SHA256 02367cb9fa073ab37acadd6d4ca35db590f7fd4c775147541104ec604fee6e4e
  size 188,614,920 bytes
- Same known-good hash verified for:
  /data/data/com.termux/files/usr/tmp/he-opencode-op22/candidates/opencode-bun141-nosplit-repair-op47
- Bun 1.4.0 compiled control verified:
  SHA256 26c7610ef19d4982dbd72ed3db7663813543bfcaf4d99834665df1f365bb9905
- Current malformed build source preserved: literal backslash-n text leaves the intended splitting:false inside a // comment.
- Protected Relay path present; installed copy is not a Git checkout in this shell.
- service_watchdog.py and socket_relay.py were running.
- Protected Relay mutation by Op201: none.
- Live runtime replacement by Op201: none.

Governance:
- Op201 is checkpoint recovery only under the boundary-failure rule.
- It does not authorize substantive continuation.
- Op200 remains historically RED/PACKET_REJECTED.
- The Op200 hard stop remains active until the recovered checkpoint review is surfaced and the Director explicitly releases it.
