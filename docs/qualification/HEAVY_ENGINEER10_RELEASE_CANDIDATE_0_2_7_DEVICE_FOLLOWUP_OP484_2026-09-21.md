# Heavy Engineer 10 — ClosedCode Device-Follow-Up RC Qualification — Op484

Timestamp UTC: `2026-09-21T07:52:29Z`

## Exact source and runtime provenance
- Product source commit: `33cb5afb0f5ff1196b7c1465bb6ed406820545e9`
- ClosedCode backend source/runtime: **0.8.18 / 0.8.18**
- OpenCode 4096: **1.18.31**
- NVIDIA: configured/connected
- ZAI: configured/connected
- No provider inference request was rerun for packaging; provider paths did not change in this repair.

## Qualification inherited directly from Op483
The exact APK bytes packaged here are the already-qualified Op483 build. Op483 produced GREEN results for:

- permission-policy regression;
- theme regression;
- steering-durability regression;
- device-interaction regression;
- sheet-drag regression;
- notification/sound regression;
- transcript regression;
- integrated-UI regression;
- Android build.

## Repair represented by this candidate
- persistent safe workspace mutation approvals are scoped by **workspace + tool** rather than exact path/content arguments;
- persistent shell approval remains **exact command only**;
- **Approve all for this task** remains request scoped;
- YOLO now means **contained workspace auto-approve**, explicitly not Full Access;
- YOLO continues to permission-gate shell;
- Chocolate Mint interactive controls use mint fill with black/dark text;
- no session/history architecture rewrite was introduced.

## Immutable release candidate
- Source APK: `/sdcard/Download/ClosedCode-cleanroom-v0.2.7-debug.apk`
- Immutable RC: `/sdcard/Download/ClosedCode-RC-0.2.7-device-followup-op484.apk`
- Bytes: **124858**
- SHA-256: `13e68f0a65cfe426f69b8f4c13e0424fd41614079d27377fc21a62ab7d8bef6d`
- Checksum: `/sdcard/Download/ClosedCode-RC-0.2.7-device-followup-op484.apk.sha256`
- Historical RC artifacts were not overwritten.
- APK installation: **NOT PERFORMED**; installation remains Director-controlled.
- FoxyApp tree SHA-256: `386c69ceb5a2c893bb4273f2567e75c4189e3d98af0fd03a2c6a2927f54c3b3c` and was not modified.

## Required Director retest
1. In ASK mode, choose **Always allow this tool in this workspace** for `workspace_write`; then repeat writes using different filenames/content and verify no repeated `workspace_write` prompt.
2. Separately authorize `workspace_delete` persistently; repeated deletes in that same workspace should stop prompting, while that approval must not implicitly approve unrelated tool classes.
3. Verify shell remains approval-gated and is not silently authorized by a workspace-write/delete approval.
4. Turn YOLO on and verify ordinary workspace mutation tools auto-approve while shell still asks; treat YOLO as contained auto-approve, not Full Access.
5. Verify Chocolate Mint interactive chips/buttons are visibly mint with black/dark text.
6. Repeat a true cold-reopen steering/history persistence test.
7. Observe send → steer → tool → final chronology and whether casual mid-run steering still causes task-continuity confusion.

Device acceptance remains **PENDING** until this exact RC is manually installed and tested.
