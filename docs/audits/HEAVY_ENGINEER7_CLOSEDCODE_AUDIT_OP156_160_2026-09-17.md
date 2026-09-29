# Heavy Engineer 7 — ClosedCode Audit Operations 156–160

Date: 2026-09-17

## Scope

This audit closes the five-operation window from Operation 156 through Operation 160.

## Results

- Op156: GREEN for Android package-installer handoff. The verified v0.1.3 APK was presented through `termux-open`. The polling window did not observe the package, but later Director-supplied screenshots directly proved that ClosedCode v0.1.3 installed and launched.
- Op157: RED / COMMAND_FAILED because a Termux-side `pm path` precheck incorrectly treated package invisibility as proof that ClosedCode was not installed. Direct runtime evidence later overruled that false negative.
- Op158: RED / COMMAND_FAILED after fast-forwarding the icon/metadata documentation and producing a Director-icon derivative whose observed SHA did not match the precomputed expectation. No v0.1.4 build occurred in that operation.
- Op159: PARTIAL. v0.1.4 built successfully, launcher icon was embedded in the APK, the corrected icon asset was committed and pushed as `57c14c93a512faee532f269f302e2dd29226e0a5`, but backend recovery failed because the operation assumed Bun was required and Bun was absent.
- Op160 attempt 1: PACKET_REJECTED due invalid `command_b64`; shell did not run.
- Op160 reissue: GREEN / read-only. Confirmed source/remote HEAD `57c14c93a512faee532f269f302e2dd29226e0a5`, clean synchronized branch, valid v0.1.4 APK, native OpenCode binary available at `/data/data/com.termux/files/usr/bin/opencode` version `1.18.31`, and backend currently down on `127.0.0.1:4096`.

## Current v0.1.4 APK

Path: `/sdcard/Download/ClosedCode-cleanroom-v0.1.4-debug.apk`

Bytes: `54093`

SHA-256: `f81aa700a5d9bba89aef98af20f72abfac255eca5a56fd82a8f49cc3d47022aa`

`aapt2 dump badging` proved:

- package `com.monag.closedcode.mobile`
- versionCode `6`
- versionName `0.1.4-cleanroom`
- application label `ClosedCode`
- launcher icon resource `res/drawable/closedcode_icon.webp`

## Backend archaeology result

The correct host runtime is already installed and does not require the repository Bun toolchain:

`/data/data/com.termux/files/usr/bin/opencode`

Observed version: `1.18.31`

The repository CLI wiring also proves `serve` is an existing command backed by `Server.listen(opts)`.

## Protected boundary

GPT-Termux-Relay source/config mutation during Ops156–160: NONE.

## Next work

Start the existing native OpenCode binary with the existing `serve` command on `127.0.0.1:4096`, verify `/global/health`, then present the already-built v0.1.4 APK through the Android package installer for runtime acceptance.