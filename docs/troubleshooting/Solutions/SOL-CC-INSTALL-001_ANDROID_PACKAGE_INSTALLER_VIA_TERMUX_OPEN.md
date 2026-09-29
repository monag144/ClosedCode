# SOL-CC-INSTALL-001 — Open the APK through Android package installer with termux-open

**Tag:** `CC-ANDROID-INSTALL-APPUID-BLOCKED`  
**Status:** ACTIVE RECOVERY PROCEDURE  
**Date:** 2026-09-17

## Use when

ClosedCode APK is build-proven but direct `pm install` from the Termux application UID fails and no authorized adb/rish bridge exists.

## Procedure

1. Verify the expected APK hash before presentation.
2. Use `termux-open --view --content-type application/vnd.android.package-archive <apk>` to hand the APK to Android's package-installer flow.
3. Do not treat invocation of the installer UI as proof of installation.
4. After the user/platform completes or cancels the installer UI, verify with `pm path <package>` and `dumpsys package <package>`.
5. Confirm the exact installed version before launch.
6. Use `$TMPDIR` or `$PREFIX/tmp` for Termux temporary artifacts; do not assume `/tmp` exists.
7. Re-establish the ClosedCode backend before end-to-end coding-agent runtime proof.

## Acceptance

Installation recovery is GREEN only after Android reports package `com.monag.closedcode.mobile` installed with versionName `0.1.3-cleanroom`.