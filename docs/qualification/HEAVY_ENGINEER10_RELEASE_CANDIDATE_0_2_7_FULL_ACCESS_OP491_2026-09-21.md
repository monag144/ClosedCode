# Heavy Engineer 10 — ClosedCode Full Access RC Qualification — Op491

Timestamp UTC: `2026-09-21T08:25:07Z`

## Exact provenance
- Product source commit: `35151242eb27c4af4cf8f431663f5d614a4d4b25`
- Packaging base HEAD: `cffa877e0995e2167b827abcb7b296fe57e6d741`
- ClosedCode backend source/runtime: **0.8.19 / 0.8.19**
- OpenCode: **1.18.31**
- NVIDIA/ZAI: configured and connected
- Provider inference rerun for packaging: **NO**

## Full Access semantics
- Full Access is **OFF by default**.
- Enabling it requires an explicit danger confirmation.
- Full Access and YOLO are mutually exclusive.
- ASK and YOLO remain workspace-contained.
- YOLO still permission-gates shell.
- Full Access removes ClosedCode's workspace-path boundary.
- Absolute paths may reach any filesystem location the Termux process is legally permitted to access.
- Full Access auto-approves filesystem mutation tools and shell.
- Android/Linux permissions, SELinux, mounts, and root status remain hard operating-system limits.

## Qualification inherited from exact Op489 build and revalidated at Op490
- Full Access regression: **GREEN**
- Permission policy: **GREEN**
- Theme: **GREEN**
- Steering durability: **GREEN**
- Device interaction: **GREEN**
- Sheet drag: **GREEN**
- Notification/sound: **GREEN**
- Transcript: **GREEN**
- Integrated UI: **GREEN**
- Android build: **GREEN**

## Immutable candidate
- Source APK: `/sdcard/Download/ClosedCode-cleanroom-v0.2.7-debug.apk`
- RC path: `/sdcard/Download/ClosedCode-RC-0.2.7-full-access-op491.apk`
- Bytes: **128952**
- SHA-256: `0a87502c6d6f68a3faa1ffe8f3ff1f8c5e924c0ceb55e42a5f6ca64862b5c212`
- Checksum: `/sdcard/Download/ClosedCode-RC-0.2.7-full-access-op491.apk.sha256`
- User-owned untracked state: **21 files**, digest `86defec32e511b1e406e80ffd0b9b597be7a9fc278860cafa8180104a8a25d80`
- Historical RCs overwritten: **NO**
- APK installed by engineering: **NO**

## Required physical acceptance
The Director must manually install this exact candidate and verify Full Access enable/disable behavior, warning confirmation, access outside the selected workspace where Android/Termux permits it, shell auto-approval only in Full Access, YOLO shell gating, mutual exclusion of YOLO and Full Access, plus the deferred cold-persistence and task-continuity observations.

Device acceptance remains **PENDING**.
