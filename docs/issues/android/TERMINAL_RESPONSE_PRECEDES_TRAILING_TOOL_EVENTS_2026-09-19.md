# Android Issue — Terminal Response Appears Before Trailing Tool Events — 2026-09-19

**Status:** OPEN / USER-OBSERVED  
**Surface:** ClosedCode Android transcript/history  
**Evidence class:** Director-pasted live Nemotron qualification transcript

## Observation

During the combined AGT-001 + AGT-002 Nemotron stress run, the ClosedCode terminal prose response appeared in the transcript before a substantial tail of workspace/tool events that logically belonged to the same investigation.

The visible order was approximately:

1. user submits the long-horizon forensic mission;
2. ClosedCode presents a comprehensive final architecture report;
3. additional `workspace_list`, `workspace_read`, `workspace_search`, `git_status`, and `git_diff` events then appear afterward.

That ordering is inconsistent with the expected causal order if those tool calls informed the terminal response.

## Expected behavior

For one agent run, the visible chronological transcript should preserve:

user prompt
→ reasoning/tool activity
→ tool results
→ final assistant prose
→ terminal completion state.

No tool event belonging to the completed run should render after the final response unless it genuinely occurred afterward as a separate operation.

## Current unknowns

The transcript proves an ordering/presentation anomaly but does not yet prove which layer is responsible.

Possible causes include:

- Android transcript insertion ordering;
- asynchronous SSE event delivery/rendering;
- terminal response being committed/rendered before queued tool events are flushed;
- session-history reload merging events in the wrong order;
- copy-session/export ordering differing from on-screen ordering;
- stale events from a prior run being appended late.

Do not classify this as a provider/model sequencing defect until request IDs/timestamps are correlated.

## Acceptance condition

For a long agent run with many tools:

- each event is timestamp/order correlated to one request ID;
- tool-running/completed events render before terminal prose when they precede it causally;
- terminal prose is the last content event for the run except an explicit terminal completion marker;
- Copy Session/export preserves the same chronology as the visible transcript;
- reopening the thread does not reorder the sequence.

## Relationship to other history issue

This is related to, but distinct from:

`docs/issues/android/NEW_THREAD_FIRST_MESSAGE_HISTORY_DISAPPEARANCE_2026-09-19.md`

Together they suggest the transcript/session presentation layer needs explicit chronology and persistence qualification.
