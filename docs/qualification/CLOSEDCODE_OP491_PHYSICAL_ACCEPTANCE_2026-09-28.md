# ClosedCode Op491 Physical Acceptance — 2026-09-28

## Verdict

**GREEN — Op491 is physically accepted. No replacement RC is warranted.**

Accepted artifact:

- `/sdcard/Download/ClosedCode-RC-0.2.7-full-access-op491.apk`
- SHA-256: `0a87502c6d6f68a3faa1ffe8f3ff1f8c5e924c0ceb55e42a5f6ca64862b5c212`

## Director device acceptance

The Director manually exercised the Op491 APK on the physical Android device and confirmed:

1. Full Access warning is displayed correctly.
2. Enabling Full Access disables YOLO.
3. Enabling YOLO disables Full Access.
4. Permitted absolute-path access outside the repository workspace works; Android-scoped `/Android/data` remained correctly unavailable, while shared Documents access worked.
5. Full Access allowed the shell stress-test path without YOLO approval prompting.
6. Returning to YOLO restored shell approval prompting.
7. Permission containment remained intact after switching modes.
8. Cold-kill/reopen preserved the selected permission mode.
9. Mid-run steering remained attached to the active run and was applied at the next safe tool/provider boundary.

## Steering evidence

Persisted session history and timeline:

- User: `Create 100 files`
- The already-active shell operation completed creation/checking of the batch.
- User steering then arrived: `Nevermind, delte what you just created and don't continue after`
- The next tool operation deleted the created `file_*.txt` files.
- A following check returned zero matching files.
- Assistant reported cleanup complete.
- No subsequent mission work occurred.

Timeline event order observed during audit:

- `030` user — create request
- `031–033` shell — original in-flight creation/check completion
- `034` user — steering correction
- `035` shell — cleanup
- `036` shell — zero-residue verification
- `037` assistant — completion acknowledgement

Current residue proof:

- `FILE_TXT_COUNT=0`

This behavior matches the intended ClosedCode steering contract: steering does not destructively interrupt an already-executing tool call; it is consumed at the next safe agent boundary and becomes controlling context for subsequent actions.

## Runtime observed during acceptance

- OpenCode service `127.0.0.1:4096`: healthy, version `1.18.31`
- ClosedCode passthrough `127.0.0.1:4097`: healthy, version `0.8.19`
- NVIDIA provider available
- Z.AI provider available

## Release conclusion

The physical acceptance gap recorded after Op491 is closed. Combined with the previously green regression/build/provider acceptance evidence, no demonstrated product defect remains in the Op491 candidate.

The remaining release-administration work is repository synchronization / authenticated push and PR creation; it does not require another APK or product-code modification.
