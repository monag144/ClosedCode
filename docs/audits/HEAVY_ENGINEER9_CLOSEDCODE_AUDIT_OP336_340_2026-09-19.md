# Heavy Engineer 9 — ClosedCode Audit — Ops336–340 — 2026-09-19

**Mission:** Long-horizon execution guardrails and live qualification.
**Anchor:** Op325
**Audit window:** Ops336–340
**Repo:** `~/ClosedCode` / `monag144/ClosedCode`
**Branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`
**Final HEAD:** `8efc6095c8bd9efdb06d29488cf8c74633a1651c`
**Worktree:** clean
**Live backend:** `0.8.9`, healthy, loopback-only, PID `11790`
**Protected Relay:** untouched, PID `17138`

## Op336 — GREEN
Added progress-aware stagnation guardrails:
- four identical action/result signatures trigger reassessment;
- repeated 2/3/4-step cycles repeated three times trigger reassessment;
- up to three reassessment interventions;
- interventions reset after twelve productive tool results;
- high tool count alone is not stagnation;
- changing evidence is not treated as identical stagnation.

Backend advanced to 0.8.8.
Commit: `5520e35ed6504c9be728021fa35be9be2243e9ce`.

## Op337 — GREEN
Added explicit terminal classifications:
- `completed`;
- `cancelled`;
- `blocked_stagnation`;
- `resource_limit`;
- `error`.

Completion markers now include termination and round count.
Backend advanced to 0.8.9.
Commit: `8efc6095c8bd9efdb06d29488cf8c74633a1651c`.

## Op338 — TIMEOUT / UNKNOWN-UNPROVEN
Started a real NVIDIA/Nemotron read-only long-horizon qualification requiring:
- at least 50 meaningful completed tool calls;
- at least 35 distinct workspace file reads;
- model-controlled evidence gathering;
- no harness-supplied tool work;
- no repository mutation.

The Relay observer timed out after 300 seconds before terminal evidence was returned.
No qualification credit is assigned.

## Op339 — GREEN
Mandatory read-only reconstruction after the interrupted Op338 result proved:
- local HEAD == remote HEAD == `8efc6095...`;
- worktree clean;
- source SHA unchanged:
  `fe87b602f96ee78fc1937200b01864a596c7cc130fbde2f4ea7dbc4fdce8c909`;
- backend still 0.8.9 PID 11790;
- mutating agent tools require permission in ASK mode;
- no repository mtime changes after Op338 start;
- orphan observer PID 13057 remained alive.

## Op340 — GREEN
Mandatory read-only audit confirmed:
- source/runtime/Git remain unchanged after Op338;
- all long-horizon static controls are present;
- backend remains 0.8.9;
- observer PID 13057 is still alive, PPID 1, sleeping in poll with one socket open;
- 50+/100+ live runtime acceptance is still not credited.

## Window mutation ledger
- **Source:** Op336 progress guardrails; Op337 terminal metadata.
- **Git:** Op336 and Op337 commits only.
- **Runtime:** backend restarts for 0.8.8 and 0.8.9; Op338 started the live qualification and left an orphan observer.
- **Provider requests:** Op338 live NVIDIA only.
- **Android/APK:** none.
- **Protected GPT-Termux-Relay:** untouched.
- **OpenCode runtime:** not replaced.

## Preserved failure
Op338 remains TIMEOUT / UNKNOWN-UNPROVEN.

## Current product state
Implemented and locally qualified:
- no small 32-round ceiling;
- high configurable emergency failsafe;
- context compaction with mission/negative-constraint/steering retention;
- progress-aware stagnation reassessment;
- explicit termination classification.

## Current blocker
- orphan Op338 observer PID 13057;
- no terminal evidence yet for 50+ or 100+ runtime acceptance.

## Next bounded target
Cleanly resolve the orphan observer without touching repository/source, then redesign long-run observation to survive Relay timeout without writing debug/feedback artifacts to the device.

## Governance
Audit 336–340 complete.
Next Relay op: Op341.
Next audit + twenty-operation review: Op345.
Hard checkpoint: Op350.
