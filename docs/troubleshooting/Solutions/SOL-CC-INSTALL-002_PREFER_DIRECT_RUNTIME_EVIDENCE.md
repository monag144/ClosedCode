# SOL-CC-INSTALL-002 — Prefer direct runtime evidence over Termux package visibility

**Tag:** `CC-ANDROID-PACKAGE-VISIBILITY-FALSE-NEGATIVE`  
**Status:** ACTIVE RECOVERY PROCEDURE  
**Date:** 2026-09-17

## Use when

A Termux-side package query cannot see ClosedCode, but the Director or device runtime has directly shown the app installed and launched.

## Procedure

1. Treat the direct launch/runtime observation as stronger evidence that the package exists.
2. Do not gate source sync, APK rebuild, backend recovery, or installer-update presentation on `pm path`.
3. Verify APK identity independently with build metadata, hash, and `aapt2 dump badging`.
4. Present version updates through the normal Android package-installer UI.
5. Use post-install visual/runtime confirmation for acceptance when Termux package visibility remains restricted.
6. Do not attempt to obtain `INTERACT_ACROSS_USERS`, root, or other elevated Android privileges merely to improve package discovery.

## Acceptance

The false-negative is recovered when engineering proceeds without relying on the blocked package-visibility precheck and the updated APK/runtime can be independently verified.