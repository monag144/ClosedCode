# Heavy Engineer 9 — ClosedCode Audit — Ops281–285 — 2026-09-19

**Mission:** ClosedCode provider stabilization — Z.AI upstream streaming repair  
**Anchor:** Op275  
**Audit window:** Ops281–285  
**Canonical repo:** `~/ClosedCode` / `monag144/ClosedCode`  
**Branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`  
**Final HEAD:** `766fb6c365b8d28648df9382378966bdd9a8f016`  
**Protected infrastructure:** GPT-Termux-Relay — no source/config mutation  
**APK installation:** prohibited through Relay; none attempted  
**Next audit:** Op290  
**Twenty-operation review:** Op295  
**Hard checkpoint:** Op300

## Op281 — RED / COMMAND_FAILED

**Objective:** Apply the bounded Z.AI upstream-streaming repair.

**Actual action:**
- local ClosedCode fast-forwarded from `88e92c5a415e3c6f306ec3a2008d129eb25949cd` to `912ca0d27c6e5e3da0a9e4b77a07807c6e9ba656`;
- process guard then counted three `passthrough_server.py` matches and aborted with exit 46 before patch application.

**Mutation:**
- Git history fast-forward only.

**Failure:**
- broad `pgrep -f` process counting falsely treated the diagnostic shell/processes as server instances.

**Not performed:**
- no source patch;
- no backend restart;
- no Z.AI qualification;
- no commit/push;
- no APK installation.

## Op282 — GREEN

**Objective:** Read-only reconstruction of passthrough process ownership.

**Evidence:**
- HEAD `912ca0d27c6e5e3da0a9e4b77a07807c6e9ba656`;
- worktree clean;
- source version `0.8.1`;
- PID `13911` was the real long-lived passthrough server:
  - cwd `~/ClosedCode`;
  - canonical passthrough source path;
  - host `127.0.0.1`;
  - port `4097`;
- PID `30581` was the Op282 diagnostic shell itself whose command text contained `passthrough_server.py`;
- PID `30602` was transient/gone during inspection;
- backend health GREEN at version `0.8.1`;
- source/helper hashes matched expected pre-repair objects.

**Mutation:** none.

## Op283 — RED / COMMAND_FAILED / PARTIAL MUTATION

**Objective:** Apply patch, restart proven server, live-qualify Z.AI, commit if GREEN.

**Successful pre-failure work:**
- source helper applied;
- static checks all GREEN:
  - version `0.8.2`;
  - `0.8.1` version marker removed;
  - streaming helper present;
  - upstream Z.AI payload forced `stream=true`;
  - Z.AI selector present;
  - NVIDIA remained on prior completion path;
  - old unconditional agent completion call removed;
- original PID `13911` stopped;
- replacement PID `32490` launched.

**Failure:**
- replacement never became healthy;
- exit 1 on post-relaunch health assertion.

**Mutation:**
- `scripts/closedcode/passthrough_server.py` modified and left uncommitted;
- live passthrough runtime stopped;
- attempted replacement exited.

**Not reached:**
- live Z.AI qualification;
- commit/push.

## Op284 — GREEN

**Objective:** Read-only reconstruction after Op283 partial mutation.

**Evidence:**
- HEAD still `912ca0d27c6e5e3da0a9e4b77a07807c6e9ba656`;
- worktree exactly:
  - ` M scripts/closedcode/passthrough_server.py`;
- patch size: 166 insertions / 2 deletions;
- source text SHA256:
  `8754a7bdf726f9b941d80c2b7f29312cec7591fd570dc94dfec5a091b6cf0fbf`;
- source version `0.8.2`;
- source compile GREEN;
- all intended streaming/static invariants present;
- exact passthrough server count: 0;
- PID `32490` absent;
- port 4097 had no listener;
- health unavailable.

**Root cause from passthrough log:**
Python attempted to parse `/data/data/com.termux/files/usr/bin/python` as source and raised:
`SyntaxError: source code cannot contain null bytes`.

The Op283 relaunch had replayed a captured `/proc/<pid>/cmdline` vector verbatim. That vector contained both an argv[0]-style `python` token and the interpreter path. Replaying it via `subprocess.Popen` duplicated the interpreter role and caused Python to interpret its own ELF binary as the script.

**Mutation:** none.

## Op285 — GREEN

**Objective:** mandatory 281–285 audit boundary; canonical runtime recovery, Z.AI live qualification, source commit/push if GREEN.

**Recovery path:**
- used the repository-owned canonical startup chain:
  - `scripts/closedcode/ensure-passthrough.sh`
  - → `scripts/closedcode/run-passthrough.sh`;
- pre-relaunch exact server count: 0;
- canonical launcher started PID `5566`;
- backend health:
  - healthy true;
  - service `closedcode-passthrough`;
  - version `0.8.2`;
  - loopback-only;
  - NVIDIA configured true;
  - Z.AI configured true.

**Live Z.AI qualification:**
- provider: `zai`;
- exact model: `glm-4.7-flash`;
- HTTP 200;
- SSE events: 2;
- tool events: 0;
- errors: none;
- final text: `ZAI_STREAM_OK`;
- complete: true;
- cancelled: false.

**Git result:**
- commit: `766fb6c365b8d28648df9382378966bdd9a8f016`;
- message: `fix(closedcode): stream Z.AI agent completions`;
- source delta: 166 insertions / 2 deletions;
- push GREEN;
- remote head equals local head;
- worktree clean.

## Window mutation ledger

- **Git/history:** Op281 fast-forwarded local history to the audited remote state.
- **Source:** Op283 applied the Z.AI streaming patch; Op285 committed that exact validated source.
- **Runtime:** Op283 stopped the old backend and failed to relaunch it; Op285 recovered through the canonical launcher and left backend healthy on version 0.8.2.
- **Providers:** live Z.AI exact-model agent qualification GREEN; NVIDIA code path statically preserved.
- **APK/package:** no APK installation attempted.
- **Protected GPT-Termux-Relay:** no source/config mutation.
- **OpenCode runtime:** not replaced.

## Preserved failures

- Op281 remains RED / COMMAND_FAILED exit 46.
- Op283 remains RED / COMMAND_FAILED partial-mutation failure.

Successful later operations do not rewrite those historical statuses.

## Current state / blocker

The Z.AI upstream non-streaming defect is repaired and live-qualified.

Immediate next risk is regression protection and Android interaction parity:
1. live NVIDIA regression sanity after the selector change;
2. explicit dedicated Stop control;
3. active-task steering without losing the original instruction;
4. Copy Session;
5. Telegram-style multi-card transcript selection/copy;
6. provider prose streaming/latency improvements after correctness.

## Governance

- Audit 281–285 complete and persisted non-Relay.
- Anchor: Op275
- Next Relay op: Op286
- Next audit: Op290
- Twenty-operation review: Op295
- Hard checkpoint: Op300
- No hard stop active.
