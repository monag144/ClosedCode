# Nemotron Issues — Android Agent Interaction Parity — 2026-09-18

**Status:** OPEN PRODUCT ISSUES

The core autonomous project-control surface is now strong, but the Director's live Android test exposed several interaction gaps relative to a mature Codex-style experience.

## Steering

A running agent currently cannot naturally accept a new user instruction and incorporate it into the active task.

Current behavior reportedly rejects/blocks a new send while `promptRunning == true`.

Desired behavior:

- keep a dedicated Stop control;
- allow the composer to remain usable while the agent is running;
- a new Send becomes a steering message;
- incorporate steering at the next safe reasoning/tool boundary without discarding the original task.

## Stop discoverability

Cancellation exists functionally, but the running-state control is not sufficiently explicit.

The send arrow silently changing into a stop glyph is not enough.

Desired behavior:

- dedicated, obvious Stop control;
- Stop remains separate from Send/Steer;
- cancellation state should be visible and unambiguous.

## Transcript copy/selection

Normal Android text selection is insufficient for long agent/tool transcripts.

Desired behavior:

- long-press a user, ClosedCode, or tool card to enter selection mode;
- tap additional cards while scrolling;
- copy selected cards in chronological order;
- provide a separate `Copy Session` action exporting the full transcript with role/tool boundaries.

## Model prose streaming

Tool events are emitted live, but final provider prose has historically arrived as an assembled terminal response rather than genuinely streamed upstream prose through the full provider path.

This reduces responsiveness even when the agent is actively working.

## Long-running process/task control

Shell execution is bounded and useful, but not yet equivalent to a mature persistent-process/task-control environment.

Future parity may require:

- durable long-running task ownership;
- attach/status/stop semantics;
- richer process output handling;
- build/test jobs that outlive one short command window when legitimately needed.

## Installed-package visibility mismatch

Heavy Engineer's shell query reported `ANDROID_APP_INSTALLED=NO`, while the Director supplied screenshots of ClosedCode actually installed and running.

Therefore the prior `pm --user 0` package visibility probe is not authoritative for the Director's active app/profile context.

Future package-state qualification must use evidence appropriate to the actual Android user/profile or direct running-app evidence.

## Priority

These are interaction/product-parity issues.

They should not be allowed to obscure the stronger finding that the native agent itself is already performing real repository inspection and autonomous tool use through the Android client.
