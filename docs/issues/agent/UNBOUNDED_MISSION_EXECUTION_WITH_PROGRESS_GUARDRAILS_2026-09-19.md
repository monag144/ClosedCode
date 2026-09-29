# Agent Product Requirement — Effectively Unbounded Mission Execution with Progress Guardrails — 2026-09-19

**Status:** OPEN / HIGH PRIORITY PRODUCT REQUIREMENT  
**Surface:** ClosedCode autonomous agent runtime  
**Requested by:** Director  
**Trigger:** AGT-003 standalone long-horizon qualification terminated at the current agent round ceiling

## Product requirement

ClosedCode must support long-running autonomous coding missions without a small fixed reasoning/tool-round ceiling prematurely terminating productive work.

The intended product behavior is:

- the user gives the agent a mission;
- the agent continues inspecting, editing, testing, diagnosing, and repairing as needed;
- the agent stops when the mission is actually complete, genuinely blocked, explicitly cancelled, or a meaningful safety/resource condition requires intervention;
- the agent does not stop merely because it crossed an arbitrary low round count.

The Director's desired user experience is effectively:

**"Keep working until the mission is done. Do not lollygag. As soon as it is done, report completion."**

## Why the current behavior is insufficient

The current agent loop has historically used a fixed low maximum-round limit (e.g. 32 rounds in recent evidence).

That ceiling is incompatible with:

- long-horizon repository investigation;
- complex multi-file coding tasks;
- build/test/repair loops;
- repeated provider/tool rounds;
- mission steering;
- realistic Codex-style autonomous engineering;
- qualification tests that intentionally require 30+ meaningful tool actions.

A productive mission should not fail with `agent exceeded maximum tool rounds` simply because legitimate work requires more steps.

## Required execution model

The runtime should move from a small hard round cap to a **mission-scoped continuation model**.

### Default behavior

- no small user-visible fixed round ceiling;
- continue while the agent is making meaningful progress;
- preserve mission state across many reasoning/tool rounds;
- preserve steering and cancellation throughout;
- preserve permission/autonomy semantics throughout;
- report completion immediately once definition of done is satisfied.

### Progress guardrails

"Effectively unlimited" does not mean an uncontrolled infinite loop.

The runtime should detect stagnation using progress-aware safeguards such as:

- repeated identical or near-identical tool calls without new evidence;
- repeated failures with no changed recovery strategy;
- cycling between the same files/commands;
- repeated restatement without action;
- no new repository state/evidence over a configurable window;
- excessive retries beyond bounded provider/tool retry policy;
- explicit token/context pressure requiring compaction/checkpointing.

When stagnation is detected, the agent should:

1. reassess its plan;
2. compact/checkpoint useful state if needed;
3. try a materially different authorized approach;
4. only escalate/block if productive continuation is no longer possible.

Do not treat ordinary long duration or high tool-call count by itself as stagnation.

## Context longevity

Long missions require context management rather than premature termination.

Preferred architecture:

- mission-state checkpointing;
- durable structured task state;
- summarization/compaction of old tool chatter while preserving constraints, decisions, failures, and remaining acceptance criteria;
- continuation after compaction without losing the original mission;
- explicit preservation of negative constraints and protected scope.

## Resource controls

Reasonable safety/resource controls may still exist, but they should be:

- high enough not to constrain ordinary engineering;
- configurable rather than a tiny universal constant;
- based on actual resource/safety conditions where practical;
- surfaced clearly if they stop a run;
- capable of user override/continuation when safe.

A large emergency ceiling may exist internally as a final failsafe, but it should not be the normal completion mechanism.

## Completion discipline

The agent should not exploit a larger budget by meandering.

Required behavior:

- maintain a concrete definition of done;
- avoid unnecessary duplicate reads/searches;
- avoid unrelated cleanup/refactors;
- stop promptly when acceptance criteria are met;
- return a concise completion report with evidence.

## Acceptance criteria

A qualifying implementation should demonstrate all of the following:

1. A 50+ meaningful tool-call mission can complete without an arbitrary max-round termination.
2. A 100+ meaningful tool-call mission can continue when it is still making measurable progress.
3. Steering remains functional deep into a long mission.
4. Stop/cancel remains responsive deep into a long mission.
5. ASK/YOLO permission semantics remain intact across long missions.
6. Context compaction does not lose the original mission or negative constraints.
7. Repeated/no-progress behavior is detected and corrected without relying on a tiny fixed round ceiling.
8. The agent terminates promptly once the mission's definition of done is satisfied.
9. The final report distinguishes completion, blocker, cancellation, and resource/safety termination.
10. Long missions do not silently mutate unrelated scope merely because they run for many rounds.

## Relationship to qualification

The AGT-003 standalone run on 2026-09-19 was invalidated by the current execution ceiling.

Until this product limitation is removed or materially raised, long-horizon qualification results can be confounded by the runtime budget rather than the model's actual focus capability.
