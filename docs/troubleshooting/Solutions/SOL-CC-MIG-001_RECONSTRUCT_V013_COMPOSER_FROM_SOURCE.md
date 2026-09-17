# SOL-CC-MIG-001 — Reconstruct v0.1.3 composer migration from authoritative source

**Tag:** `CC-V013-COMPOSER-MIGRATION-PAYLOAD-CORRUPT`  
**Status:** ACTIVE RECOVERY PROCEDURE  
**Date:** 2026-09-17

## Use when

`apply_composer_ui_v013.py` cannot be decoded/validated because its embedded payload is malformed.

## Procedure

1. Do not attempt Base64 character guessing or permissive decoding.
2. Prove current branch/HEAD/worktree after the failed helper inspection.
3. Read the current Android composer implementation and relevant upstream OpenCode composer controls.
4. Reconstruct only the intended bounded v0.1.3 slice:
   - provider-grouped model selection with the selected model reflected on the model button;
   - Auto/reasoning controls and Plan/Build mode controls;
   - reasoning-effort selector/window;
   - microphone/voice input control;
   - ClosedCode branding/icon treatment;
   - preserve concrete provider/model IDs in prompt submission.
5. Bump build metadata only as part of the explicit replacement patch.
6. Diff and compile/build before installation.
7. Preserve the malformed helper as historical evidence until the replacement implementation is proved; do not silently rewrite its history.

## Acceptance

Recovery is complete when the replacement source is reviewable as ordinary tracked code, builds into a signed APK, and the intended controls are verified on-device.
