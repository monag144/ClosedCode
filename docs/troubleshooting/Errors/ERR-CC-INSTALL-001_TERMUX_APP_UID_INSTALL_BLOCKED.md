# ERR-CC-INSTALL-001 — Termux app UID cannot silently install ClosedCode APK

**Tag:** `CC-ANDROID-INSTALL-APPUID-BLOCKED`  
**Status:** CONFIRMED  
**First observed operation:** `HEAVY-ENGINEER7-CLOSEDCODE-OP154.install-launch-runtime-proof`  
**Date:** 2026-09-17

## Signature

ClosedCode v0.1.3 was build-proven and hash-verified, but runtime installation could not be completed from the ordinary Termux application UID.

Observed capability state:

- `adb`: absent
- `rish`: absent
- direct `pm install -r`: failed
- existing ClosedCode package: absent
- confirmed install mutation: none
- `termux-open`: present
- `/tmp`: absent
- `$TMPDIR`: `/data/data/com.termux/files/usr/tmp`

## Meaning

This is not an APK build failure and not a GPT-Termux-Relay failure. Android package management prevents the ordinary Termux app UID from silently installing an APK through direct package-manager shell commands.

The next valid route is the platform package-installer UI opened through Termux file sharing/content-URI support.

## Safety

Do not grant new privileged Android permissions, root the device, alter GPT-Termux-Relay, or invent a hidden-install bypass merely to install ClosedCode.