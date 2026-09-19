# Heavy Engineer 9 — ClosedCode Release Regression and Android Build — Op318

**Date:** 2026-09-19  
**Operation:** 318  
**Status:** GREEN  
**Branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`  
**HEAD after known qualification-doc reconciliation:** `ac302a93d418da0d2fe95d918984bbfe323b88eb`

## Backend regression

Backend 0.8.5 passed:
- source compile;
- provider retry-policy regression;
- Z.AI pacing regression;
- live health;
- post-build health.

Live passthrough PID remained `20808`.

No provider request and no backend restart occurred.

## Android source regression

Android source under `apps/closedcode-android` was unchanged from accepted 0.2.7 baseline commit `f3cbf7fe130b3d962dfcacacb664148bbf922a1d`.

Qualified identity:
- package: `com.monag.closedcode.mobile`
- version name: `0.2.7-cleanroom`
- version code: `19`

## Fresh no-delete build

The stock build script was intentionally not invoked because it removes its build directory and overwrites the standard Download APK.

Instead Op318 reproduced the compile/package/sign pipeline in a new external build directory without deleting or overwriting existing files.

Build directory:
`~/.local/state/closedcode/build-op318-android-027`

Fresh APK:
`/sdcard/Download/ClosedCode-cleanroom-v0.2.7-debug-op318.apk`

Qualification:
- bytes: `111955`
- SHA-256: `3fd5f3d4d46953c41ea9efffaac7af452546bee22c65f56ea4ada9e6235c6d8f`
- APK signature verification: GREEN
- manifest/package badging:
  - `com.monag.closedcode.mobile`
  - versionCode `19`
  - versionName `0.2.7-cleanroom`
  - compileSdk 34
  - application label `ClosedCode`

## Mutation accounting

- ClosedCode source: unchanged.
- Git content: no mutation; only known Op316 qualification-document fast-forward.
- Backend runtime: unchanged.
- Provider sessions: no requests.
- Android build artifacts: new non-conflicting paths only.
- Existing files: no overwrite.
- Files: no deletion.
- APK install: not attempted.
- Protected GPT-Termux-Relay: untouched.
- OpenCode runtime: not replaced.

## Release-readiness meaning

Op318 proves the current accepted Android source can still produce a correctly signed 0.2.7 APK after the backend 0.8.5 provider stabilization work, without regressing backend health or crossing protected boundaries.
