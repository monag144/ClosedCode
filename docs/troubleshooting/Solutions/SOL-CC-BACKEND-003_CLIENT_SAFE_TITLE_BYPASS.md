# SOL-CC-BACKEND-003 — Client-safe title bypass for OpenCode 1.18.31

**Tag:** `CC-PROMPT-ASYNC-TITLE-AGENT-CRASH`  
**Status:** ACTIVE COMPATIBILITY REPAIR  
**Date:** 2026-09-18

## Use when

OpenCode 1.18.31 accepts `POST /session/:id/prompt_async` with HTTP 204 but the first prompt on a default-titled session dies inside automatic title generation with:

`TypeError: undefined is not an object (evaluating 'a.name')`

and backend logs identify the hidden `title` agent immediately before the failure.

## Proven bypass

Operation 174 created a disposable session with a non-default title and sent the same exact NVIDIA Nemotron prompt. The request returned HTTP 204 and the assistant completion appeared on the first poll.

This isolates the defect to automatic title generation rather than:

- provider credential loading
- NVIDIA connectivity
- the exact Nemotron model
- prompt_async transport
- the primary build agent

## ClosedCode repair

ClosedCode should not create an untitled/default-titled session against this backend version.

1. Create new sessions with a non-default placeholder title.
2. Before the first user prompt, replace the placeholder title with a deterministic title derived from the prompt text.
3. For legacy default-titled sessions, patch the title before dispatch.
4. If patching a legacy default title fails, do not dispatch the prompt into the known crashing path.
5. Keep the backend itself unchanged.

This is a compatibility shim for the current native OpenCode backend. It can be removed after the underlying backend title-agent defect is fixed and requalified.

## Acceptance

The Android build is GREEN only after:

- new sessions are created with a non-default title;
- first prompt title replacement is wired;
- `prompt_async` uses the selected provider/model/agent/variant;
- cancel/stop remains available;
- event-stream reconnect is automatic;
- exact NVIDIA Nemotron completion succeeds in runtime qualification.
