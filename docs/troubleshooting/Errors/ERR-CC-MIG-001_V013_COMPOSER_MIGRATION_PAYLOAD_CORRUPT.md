# ERR-CC-MIG-001 — Embedded v0.1.3 composer migration payload is malformed

**Tag:** `CC-V013-COMPOSER-MIGRATION-PAYLOAD-CORRUPT`  
**Status:** CONFIRMED  
**First observed operation:** `HEAVY-ENGINEER7-CLOSEDCODE-OP151.refinement-entry-sync-and-inspect-v013`  
**Date:** 2026-09-17

## Signature

After the phone checkout fast-forwarded successfully to `aaecaf39d3a0e2bbdb426fabfd00fc2aca68b583`, read-only inspection of:

`apps/closedcode-android/tools/apply_composer_ui_v013.py`

failed while decoding the helper's own embedded Base64 payload:

```text
binascii.Error: Invalid base64-encoded string:
number of data characters (9833) cannot be 1 more than a multiple of 4
```

GitHub-side inspection independently found the embedded payload span length is 9835 characters, modulo 4 = 3, while the helper declares decoded-source SHA-256:

`b52ba6d98cfdc15406f648a32ece85f1039b373bc74eef266c091ddc512d949f`

## Meaning

This is **not** a GPT-Termux-Relay packet-transport failure. The Op151 Relay packet executed and the guarded Git fast-forward completed before the helper inspection failed.

The defect is inside the committed ClosedCode migration helper itself. The embedded compressed/Base64 source is malformed or truncated and must not be executed or repaired by guessing missing Base64 characters.

## Safety rule

- Preserve Op151 as `COMMAND_FAILED`.
- Preserve its successful fast-forward as real partial mutation.
- Do not execute the broken helper.
- Reconstruct the intended v0.1.3 composer changes from authoritative existing source/reference and the Director-defined UI requirements.
- Apply a new explicit source patch under a later operation after read-only state/source proof.
