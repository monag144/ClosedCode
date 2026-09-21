# Heavy Engineer 10 — ClosedCode Audit Ops481–485

Timestamp UTC: `2026-09-21T07:53:57Z`
Window: **Ops481–485 exactly**
Storage format: **approved sideways / horizontal audit structure**

| Audit axis | Op481 | Op482 | Op483 | Op484 | Op485 |
|---|---|---|---|---|---|
| **Historical status** | **RED / AUDIT NOT COMMITTED** | **GREEN** | **GREEN** | **GREEN** | **GREEN — mandatory audit** |
| **Purpose** | Recover Ops476–480 audit | Recover same audit without removable-artifact precondition | Complete Director-follow-up permission/YOLO/Mint repair | Package immutable device-follow-up RC | Revalidate and audit Ops481–485 |
| **Repository outcome** | No commit; five Op478 product edits preserved | Audit-only commit `c1ae0230827f6aa8a11b56f0e2a976ee4a39cd5f` | Product commit `33cb5afb0f5ff1196b7c1465bb6ed406820545e9` | Certificate-only commit `77e62d9cab6ec95ee067c9a5c57cabbdfd25f2a9` | Commit only this audit |
| **Runtime outcome** | Backend stayed **0.8.17** | Backend stayed **0.8.17** | Structurally deployed **0.8.18** | Backend stayed **0.8.18** | Backend verified **0.8.18** |
| **APK outcome** | No build/package | No build/package | Fresh qualified debug APK, SHA `13e68f0a65cfe426f69b8f4c13e0424fd41614079d27377fc21a62ab7d8bef6d` | Immutable RC copied from exact Op483 build | RC identity revalidated |
| **Primary evidence** | Reconstruction/regressions succeeded; audit then failed because a Download artifact path was missing | Mandatory Ops476–480 audit finally persisted without making removable artifact presence a governance precondition | Both stale tests repaired; all eight regressions + Android build GREEN; backend 0.8.18 deployed | Exact qualified bytes certified without rebuild or provider rerun | Full regression/runtime/artifact/FoxyApp revalidation |
| **Failure cause** | Audit incorrectly required both APK paths to exist | — | — | — | — |
| **Release consequence** | Mandatory audit still pending | Governance recovered | Follow-up defects qualified in source/build/runtime | Exact candidate ready for Director phone retest | **STOP for device evidence** |

## Accepted Director evidence carried into this window

| Physical acceptance item | Current state |
|---|---|
| Delete Session hitbox | **GREEN** |
| Dark theme | **GREEN** |
| Session Context drag target | **GREEN** |
| Cold steering/history persistence | **GREEN 1/1**, repeat on current RC |
| Transcript ordering | **GREEN for chronology** |
| Permission-dialog mechanics | **GREEN mechanically** |
| Persistent permission policy | Prior RC **YELLOW**; repaired in Op483 and requires current-RC device retest |
| Chocolate Mint controls | Prior RC **YELLOW**; repaired in Op483 and requires current-RC device retest |
| Mid-run steering task continuity | **YELLOW observation**; monitor without architecture expansion |

## Op483 qualified repair

The accepted product repair at `33cb5afb0f5ff1196b7c1465bb6ed406820545e9` implements:

- persistent approvals for safe workspace mutation tools scoped by **workspace + tool**;
- filename/content variation under an already authorized workspace tool no longer creates a new persistent-approval identity;
- persistent shell approval remains **exact-command scoped**;
- **Approve all for this task** remains request scoped;
- YOLO is explicitly **contained workspace auto-approve**, not Full Access;
- YOLO does **not** auto-approve shell;
- Chocolate Mint interactive controls use mint fill with black/dark text;
- no transcript/history architecture redesign.

All eight local gates were GREEN at Op483 and are GREEN again at Op485:

- permission policy;
- theme;
- steering durability;
- device interaction;
- sheet drag;
- notification/sound;
- transcript;
- integrated UI.

## Current release candidate

- Product source: `33cb5afb0f5ff1196b7c1465bb6ed406820545e9`
- Packaging/certificate commit before this audit: `77e62d9cab6ec95ee067c9a5c57cabbdfd25f2a9`
- ClosedCode backend source/runtime: **0.8.18 / 0.8.18**
- OpenCode 4096: **1.18.31**
- RC: `/sdcard/Download/ClosedCode-RC-0.2.7-device-followup-op484.apk`
- RC bytes: **124858**
- RC SHA-256: `13e68f0a65cfe426f69b8f4c13e0424fd41614079d27377fc21a62ab7d8bef6d`
- Checksum file: `/sdcard/Download/ClosedCode-RC-0.2.7-device-followup-op484.apk.sha256`
- FoxyApp digest: `386c69ceb5a2c893bb4273f2567e75c4189e3d98af0fd03a2c6a2927f54c3b3c`

## Roadmap drift questions

- **Did this window add features unrelated to qualification defects?** No.
- **Did it add providers or rerun provider inference unnecessarily?** No.
- **Did it introduce Full Access?** No. YOLO was clarified as contained auto-approve; shell remains gated.
- **Did it broaden persistent permissions beyond the selected workspace/tool scope?** No.
- **Did it rewrite transcript/history architecture because of one ambiguous steering-continuity observation?** No.
- **Did it add a new theme?** No; it corrected existing Chocolate Mint presentation.
- **Did it touch protected GPT-Termux-Relay source/config?** No.
- **Did it mutate/delete FoxyApp?** No.
- **Did it overwrite historical RCs?** No.
- **Did engineering install an APK?** No.
- **Was device acceptance inferred from source/regression/build/runtime GREEN?** No.

## Audit disposition

The stabilization path is now **device-test gated**. No additional ClosedCode development is justified before the Director manually installs and tests the exact Op484 candidate.

Required remaining physical checks are narrowly limited to:

1. workspace-write persistent approval survives differing filenames/content without repeat prompts;
2. workspace-delete can be persistently approved independently;
3. shell remains permission-gated;
4. YOLO auto-approves contained workspace tools but not shell;
5. Chocolate Mint controls render mint with black/dark text;
6. repeat cold-reopen steering persistence;
7. observe task continuity during mid-run steering.

If those tests are GREEN and no new blocking defect appears, proceed toward minimum final integrated acceptance and campaign exit rather than another feature sprint.

Next mandatory five-operation audit: **Op490**. Op490 is also the next **20-operation review boundary**. Next hard checkpoint: **Op500**.
