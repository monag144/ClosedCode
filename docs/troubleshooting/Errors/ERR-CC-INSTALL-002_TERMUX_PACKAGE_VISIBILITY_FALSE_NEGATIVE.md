# ERR-CC-INSTALL-002 — Termux package visibility false-negative after successful Android launch

**Tag:** `CC-ANDROID-PACKAGE-VISIBILITY-FALSE-NEGATIVE`  
**Status:** CONFIRMED  
**First observed operation:** `HEAVY-ENGINEER7-CLOSEDCODE-OP157.icon-v014-backend-runtime-recovery`  
**Date:** 2026-09-17

## Signature

A Termux-side precheck using Android package-manager visibility reported that `com.monag.closedcode.mobile` was not installed and aborted the operation.

However, the Director had already supplied direct device runtime evidence showing ClosedCode launched successfully on the phone and rendered its Sessions screen. The app also correctly displayed the backend-unavailable state for `127.0.0.1:4096`.

## Meaning

From this Termux application UID/context, `pm path` / package visibility is not authoritative enough to negate stronger direct runtime evidence. Android package visibility, user/profile context, or Binder permission boundaries can yield a false negative.

Do not infer uninstallation solely from an empty Termux package query when the app has been directly observed running.

## Safety

Preserve the failed precheck as historical evidence. Do not weaken Android security or request cross-user privileges merely to make package discovery authoritative.