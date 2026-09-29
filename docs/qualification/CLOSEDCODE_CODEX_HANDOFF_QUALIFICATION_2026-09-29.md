# ClosedCode Codex Handoff Qualification — 2026-09-29

## Candidate identity

- Branch: `closedcode/android-cleanroom-opencode-mobile-20260916`
- Starting HEAD: `9cd5458f4b0941cd9edb56eb08da3888e9e2d0f8`
- Qualified product commit: `35151242eb27c4af4cf8f431663f5d614a4d4b25`
- Base comparison: 350 commits ahead of and 0 behind `origin/dev`
- Protected user state: 21 files, digest
  `86defec32e511b1e406e80ffd0b9b597be7a9fc278860cafa8180104a8a25d80`

## Automated qualification

The following current regressions passed:

- device interaction;
- Full Access;
- integrated UI;
- notification and sound;
- permission policy;
- Session Context drag;
- steering durability;
- themes;
- transcript durability and chronology.

The Android client built successfully using the Termux SDK/build tools. The
result was package `com.monag.closedcode.mobile`, version
`0.2.7-cleanroom`, 128,952 bytes. This rebuild was qualification output only;
it did not replace or recertify the immutable Op491 candidate.

## Real integrated coding-agent workflow

A fresh isolated scratch project contained a deliberately incorrect Python
implementation and its fixed test. Through backend `0.8.19`, the configured
NVIDIA provider, and exact model `nvidia/nemotron-3-ultra-550b-a55b`, ClosedCode:

1. read the implementation and test;
2. ran the test and observed the failure;
3. diagnosed subtraction where multiplication was required;
4. applied a targeted patch only to the implementation;
5. reran the test successfully;
6. returned a correct final report and `termination=completed`.

Observed completed tool sequence:

`workspace_read`, `workspace_read`, `shell`, `workspace_patch`, `shell`.

YOLO generated permission requests for both shell invocations and did not prompt
for workspace reads or patching. The test file remained byte-for-byte unchanged,
the implementation changed once, no tool error occurred, and terminal accounting
reported five provider rounds with exact usage: 10,136 prompt tokens, 428
completion tokens, 10,564 total tokens.

## Immutable release candidate

The existing candidate remains:

`/sdcard/Download/ClosedCode-RC-0.2.7-full-access-op491.apk`

- bytes: 128,952
- SHA-256: `0a87502c6d6f68a3faa1ffe8f3ff1f8c5e924c0ceb55e42a5f6ca64862b5c212`
- overwritten: NO
- installed by engineering: NO

## Remaining external gate

Physical-device acceptance remains pending rather than failed. The Director must
manually install the exact Op491 APK and verify:

- Full Access default/preference behavior and danger confirmation;
- Full Access/YOLO mutual exclusion;
- permitted absolute-path read/write/delete outside the selected workspace;
- Full Access shell auto-approval;
- restored YOLO shell prompts and ASK containment;
- repeat cold-reopen persistence;
- mid-run steering/task continuity on the latest build.

The repository's device-installation rule prohibits engineering installation
through Termux. No product blocker was demonstrated during this qualification,
so no product code was changed and no replacement RC was created.
