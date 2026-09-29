# Android Product Request — Human-Readable Agent Progress Feedback — 2026-09-19

**Status:** OPEN PRODUCT REQUEST  
**Surface:** ClosedCode Android agent transcript / progress presentation  
**Requested by:** Director

## Product intent

ClosedCode should be able to present long-running agent work in ordinary human-readable progress language rather than requiring the user to interpret a stream dominated by technical lifecycle labels such as:

- operation running;
- operation completed;
- raw tool name;
- raw tool argument/result payload.

The desired feel is closer to mature coding-agent progress narration: concise sentences explaining what the agent is doing and why, while preserving access to the underlying technical evidence.

Examples of the desired presentation style:

- "I’m checking the Android session-history path to see why the first message disappears."
- "The backend path looks correct; I’m comparing it with the reload logic now."
- "I found the ordering race. I’m verifying that the proposed fix won’t reorder existing sessions."
- "The tests passed. I’m checking the final diff before I finish."

These are presentation summaries of real work, not invented chain-of-thought.

## Toggleable presentation

Place the preference in Settings rather than adding another permanent primary-screen control.

Suggested setting:

`Settings → Agent Activity → Progress detail`

Possible values:

- **Readable** — human-readable progress summaries are primary; raw tool cards remain expandable/inspectable.
- **Technical** — preserve the direct tool-running/tool-completed presentation.
- **Compact** — show only major milestones, warnings, permissions, and terminal result.

Exact labels may be refined during implementation.

## Token/API-cost principle

Human-readable progress should **not require extra provider calls by default**.

Preferred implementation order:

1. derive readable progress locally from already-emitted structured tool/event data;
2. use agent-supplied safe progress/status text when the existing provider round already contains it;
3. only introduce additional model-generated progress narration as an explicit optional mode if it demonstrably improves usefulness enough to justify added latency/token/API cost.

A cosmetic progress feature must not silently multiply provider usage.

## Evidence preservation

Readable progress is a projection, not a replacement for evidence.

The user must remain able to inspect:

- exact tool name;
- running/completed/error state;
- relevant safe arguments/path;
- relevant safe result/error;
- permission events;
- steering events;
- cancellation;
- terminal classification.

Do not remove the technical event stream merely to make the UI friendlier.

## Security / reasoning boundary

Human-readable feedback may summarize observable work and tool outcomes.

It must not expose hidden chain-of-thought, secrets, unrestricted hidden prompts, credential values, or private backend reasoning state.

Examples of safe summaries:

- "I’m reading the build configuration."
- "The test failed because the expected file is missing."
- "I’m retrying with the repository’s documented build command."

Avoid presentation framed as hidden internal deliberation.

## Long-horizon behavior

The feature should remain useful during 100+ tool-call missions.

Requirements:

- avoid one prose bubble for every trivial low-level event if that creates transcript spam;
- coalesce repetitive progress where appropriate;
- surface meaningful phase changes;
- preserve chronological ordering;
- keep steering/permission/Stop state obvious;
- never allow generated progress text to delay or block tool execution;
- final completion report remains distinct from progress narration.

## Acceptance conditions

1. A user can understand the broad activity of a long coding task without expanding every raw tool card.
2. Raw technical evidence remains available.
3. Readable mode does not add provider/API calls in its default implementation.
4. Progress presentation remains chronological with tool/final-response ordering.
5. Switching presentation mode does not alter agent behavior, session state, autonomy, or provider routing.
