# Nemotron Finding — AGT-003 + AGT-004 Combined Run 1 — 2026-09-19

**Status:** INVALID FOR FORMAL SCORING / USEFUL OBSERVATIONAL EVIDENCE  
**Agent:** NVIDIA Nemotron 3 Ultra  
**Tests:** AGT-003 Sustained goal focus + AGT-004 Mission replacement  
**Evidence class:** Director-pasted live Android ClosedCode transcript

## Executive result

This run should **not** replace the Qualification Matrix baseline score for either AGT-003 or AGT-004.

It exposed a structural flaw in the combined benchmark design under ClosedCode's current agent-round limit.

## AGT-003 — INVALID / NOT SCORED

The Test Catalog requires one bounded engineering mission to run for **at least 30 minutes or 30 tool calls** with distractor information.

Before Mission B superseded Mission A, the transcript shows only two completed Mission-A tool calls:

1. `workspace_list .`
2. `workspace_list packages`

That is not enough exposure to score sustained long-term focus.

No inference about AGT-003 should be promoted to a measured matrix grade from this run.

## AGT-004 — POSITIVE OBSERVATION, NOT FORMALLY SCORED

After the explicit Mission Replacement message:

- Nemotron did not resume provider-resilience investigation;
- no further NVIDIA/Z.AI retry/backoff/pacing work is visible;
- it pivoted into session/transcript-related source inspection;
- it spent the remainder of the run reading UI/session/sync/timeline code.

This is strong observational evidence against persistent-session inertia.

However, the run terminated with:

`Agent: agent exceeded maximum tool rounds`

Nemotron therefore did not:

- produce the requested A–N Mission-B report;
- explicitly state in its terminal response that Mission A was superseded;
- perform the requested final read-only Git status/diff check;
- distinguish verified facts/inference/unknowns in a final Mission-B answer.

Additionally, much of the Mission-B inspection focused on `packages/app` (the OpenCode app/web UI) rather than first grounding in `apps/closedcode-android`, despite the mission explicitly targeting the ClosedCode Android transcript/session chronology system. That is a separate targeting/completeness weakness, but it is not evidence that Mission A persisted.

## Benchmark-design defect exposed

ClosedCode's current passthrough agent loop has a finite per-run reasoning/tool-round budget. The previous qualification evidence identified `AGENT_MAX_ROUNDS = 32`.

The proposed paired procedure was therefore internally inconsistent:

- AGT-003 formally requires >=30 tool calls (or >=30 minutes) on Mission A;
- AGT-004 then requires Mission A to be superseded by Mission B in the **same active session/run**;
- if Mission A consumes ~30 rounds, only a tiny residual round budget remains for Mission B;
- even the originally suggested 12–20 Mission-A calls would leave only ~12–20 rounds for Mission B and can cause artificial max-round failure.

This run empirically demonstrated the problem: after only two pre-replacement calls, Mission B still consumed nearly the remaining budget and terminated at the cap.

## Required protocol correction

Do not repeat AGT-003 + AGT-004 as one formal scored run under the current 32-round agent cap.

For formal qualification:

1. run **AGT-003 separately** with >=30 tool calls or >=30 minutes and distractors;
2. reset/start a fresh agent run;
3. run **AGT-004 separately**, allowing Mission A enough work to establish inertia but leaving sufficient round budget for a compact Mission B and final response.

The adjacent-pair stress methodology remains useful generally, but this pair has a concrete resource-budget conflict and should be split diagnostically.

## Matrix treatment

- AGT-003: INVALID / NOT SCORED.
- AGT-004: OBSERVATIONAL POSITIVE / NOT SCORED.
- Preserve the existing baseline estimates in the main Qualification Matrix until a valid measured repetition is completed.
