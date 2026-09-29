# Heavy Engineer 10 — ClosedCode Release-Exit RC Qualification — Op477

Timestamp UTC: `2026-09-21T06:39:52Z`

## Provenance
- Qualified product-source commit: `974e7cc4bf110f0b4bcc168a03d96db02953d178`
- Packaging repository HEAD before certificate: `6fd0c566905528f2a456de688e842d1632807929`
- Product paths are byte-equivalent between those commits; intervening commits are governance/audit documentation only.
- ClosedCode backend source/runtime contract: **0.8.17 / 0.8.17**.
- OpenCode runtime: **1.18.31**.
- NVIDIA and ZAI are configured/connected; no fresh provider request was spent for this packaging operation because existing provider acceptance was already sufficient and no provider path changed after Op472.

## Local release gates
- Steering durability: GREEN
- Device interaction: GREEN
- Sheet drag: GREEN
- Theme: GREEN
- Notification/sound: GREEN
- Permission policy: GREEN
- Transcript: GREEN
- Integrated UI: GREEN
- Fresh Android build: GREEN

## Synthetic qualification-residue cleanup
The only two Op473 residue files were first matched against their exact expected synthetic contents, then removed:
- history SHA-256: `f9ca6bbd8fbbf44e68797d0f156656ad5986d511ed2de38ae2ac33f314493f38`
- timeline SHA-256: `547df954298df33ad45905b2268003b422eadb69e339e1c05315bb19aded3a62`
No unrelated ClosedCode session history was touched.

## Immutable release candidate
- Path: `/sdcard/Download/ClosedCode-RC-0.2.7-release-exit-op477.apk`
- Bytes: **124856**
- SHA-256: `ac615d7e761978af13d5a34185161087f3088a66c9bb308016b1c720e7fafac0`
- Checksum file: `/sdcard/Download/ClosedCode-RC-0.2.7-release-exit-op477.apk.sha256`
- Historical RC files were not overwritten.
- APK installation: **NOT PERFORMED**. Installation remains Director-controlled.

## Remaining device acceptance
This candidate is source/regression/build/runtime qualified but **not device accepted**. The Director must manually install this RC and verify:
1. permission interaction is usable and never layered/blocked;
2. Delete Session responds only to its constrained visible hit target;
3. Dark mode is genuinely black/white and legible;
4. Session Context has a physically usable drag target;
5. a submitted steering/history message survives a true cold reopen;
6. normal send → steer → tool → final-message chronology remains correct.

No additional feature work is authorized while this RC awaits device evidence.
