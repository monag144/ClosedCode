# Heavy Engineer 10 — ClosedCode Audit Ops366–370

Mission: ClosedCode delivery/stabilization and real autonomous coding-agent qualification.
Anchor: Op350.
Window: Ops366–370 exactly.
Canonical repo: `~/ClosedCode`.
Branch: `closedcode/android-cleanroom-opencode-mobile-20260916`.
Governance recovery: required audit artifact recovered during Op371 after Op370 failed at the boundary. Op371 is not part of this five-operation audit window.

## Operation ledger
- Op366 — GREEN — read-only mission-drift forensics. Proved repeated compaction could discard a prior synthetic mission checkpoint from active compacted context, losing transitive original mission/steering instructions. No source/runtime mutation.
- Op367 — GREEN — fixed transitive mission retention across repeated compaction in `scripts/closedcode/passthrough_server.py`; backend advanced 0.8.9 → 0.8.10. Four-successive-compaction deterministic regression proved original mission retention, steering retention, legacy checkpoint parsing, and stable de-duplication. Commit `b1b854bcf246752e2db24469a9787de5b7fed7c4`.
- Op368 — GREEN — restarted only the ClosedCode passthrough backend through its existing owner and reran the four-compaction regression against deployed 0.8.10 source. Protected GPT-Termux-Relay was not mutated. No provider request.
- Op369 — GREEN — corrected Marathon Harness acceptance so observed non-fatal tool errors are evidence rather than an automatic veto while terminal/error/steering/permission/cancellation gates remain enforced. Commit `8ae6c4717d2cd4eaae35254ecd63fe64522e1592`. No provider request.
- Op370 — RED / COMMAND_FAILED — mandatory audit/review packet aborted at backend process-count assertion with `ERROR=BACKEND_PROCESS_COUNT count=3 pids=7496 7566 22370`. The assertion used `pgrep -f '[p]assthrough_server.py'`, which can match command lines containing the source-path text rather than only the actual backend script argv. Op370 terminated before audit/review files were created, committed, or pushed. Preserve Op370 as RED permanently.

## Window assessment
Window mutations: product source/version at Op367; backend process state at Op368; qualification harness at Op369. Op370 made no product/source/runtime/process mutation and failed before documentation persistence.
Preserved failures: Op350 RED, Op351 RED, Op363 RED, and Op370 RED remain historical REDs. Historical Op357 qualification remains formally YELLOW.
Protected state: GPT-Termux-Relay remains protected; OpenCode was not replaced; no APK installation through Termux/Relay occurred.
Current blocker: formal long-horizon mission continuity still requires a fresh post-fix real provider qualification on backend 0.8.10.
Governance: required Audit 366–370 is recovered by Op371. Substantive work remained stopped during recovery. Next hard checkpoint remains Op375.

## Op371 governance-recovery verification
- Timestamp UTC: `2026-09-20T00:28:22Z`
- Local/remote HEAD before recovery: `8ae6c4717d2cd4eaae35254ecd63fe64522e1592` / `8ae6c4717d2cd4eaae35254ecd63fe64522e1592`
- Worktree before recovery: `CLEAN`
- Backend source SHA-256: `254d06947fb63396a53fbb812fa9e8646a864a1cb752503b75b3b267753be1c4`
- Marathon Harness SHA-256: `29bbf247a45f72caac9ff96025fadade18631820803d1f22ed0d08f8fdf4f991`
- Flawed Op370-style `pgrep -f` matches during recovery: `8931 8985 22370`
- Exact backend argv owners: `[{"pid":22370,"args":["python","/data/data/com.termux/files/usr/bin/python","/data/data/com.termux/files/home/ClosedCode/scripts/closedcode/passthrough_server.py","--host","127.0.0.1","--port","4097"]}]`
- Exact backend owner count: `1`
- Backend PID: `22370`
- Backend health: `{"healthy":true,"service":"closedcode-passthrough","version":"0.8.10","bind":"loopback-only","providers":{"nvidia":true,"zai":true}}`
- Protected Relay PID: `17138`
- Op370 reported PID follow-up:
```text
PID_7496=ABSENT
PID_7566=ABSENT
PID_22370=LIVE:python /data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/ClosedCode/scripts/closedcode/passthrough_server.py --host 127.0.0.1 --port 4097 
```
- Recovery conclusion: Op370 process-count assertion was overbroad; exact argv ownership establishes one actual passthrough backend owner at recovery time. Op370 remains RED because the failed assertion consumed the boundary operation.
