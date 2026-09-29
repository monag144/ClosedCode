# ERR-CC-BACKEND-003 — prompt_async dies during automatic title generation

**Tag:** `CC-PROMPT-ASYNC-TITLE-AGENT-CRASH`  
**Status:** PROVED / CLIENT WORKAROUND SELECTED  
**Date:** 2026-09-18

## Symptom

The ClosedCode/OpenCode backend accepts a real async prompt with HTTP 204, but no assistant completion appears. Polling the session messages shows the selected NVIDIA model recorded for the pending assistant turn while the backend logs report:

`prompt_async failed ... TypeError: undefined is not an object (evaluating 'a.name')`

The same log shows the failure occurs immediately after OpenCode starts the hidden `title` agent stream:

`agent=title mode=primary small=true`

## Proven context

- Native OpenCode version: `1.18.31`.
- Backend health remains GREEN before and after the failure.
- `/agent?directory=<ClosedCode>` is HTTP 200 after the earlier `references` compatibility repair and canonical instance disposal.
- Persistent provider credentials are present for `nvidia` and `zai` with auth file mode `0600`.
- Provider catalog reports `nvidia` connected.
- Exact target `nvidia/nemotron-3-ultra-550b-a55b` exists, is active, and exposes `low,medium,high` variants.
- `POST /session/:id/prompt_async` returns HTTP 204, so transport/schema acceptance is GREEN.
- The first-session title path in `SessionPrompt.ensureTitle` runs only while the session still has a default title. It resolves the hidden `title` agent and a small/fallback model before the main loop proceeds.

## Current fault boundary

The failure is after prompt transport acceptance and before a normal assistant completion. Current evidence points specifically at the automatic first-turn title-generation path, but bypass behavior has not yet been proved.

Do not classify NVIDIA authentication or Android transport as the cause based on this failure alone.

## Next proof

Create a disposable session with an explicit non-default title so `SessionPrompt.ensureTitle` is skipped, then submit the same NVIDIA prompt. Compare:

- prompt HTTP result
- message completion
- backend log agent/model path
- session status

If the titled session succeeds, isolate the fault to automatic title generation and select the smallest compatibility repair.


## Op174 proof

A disposable session created with an explicit non-default title skipped the automatic title-generation path and completed successfully on the first poll using the exact NVIDIA target `nvidia/nemotron-3-ultra-550b-a55b`.

This proves the main NVIDIA prompt path is functional and isolates the failure to automatic first-turn title generation on default-titled sessions.

The selected ClosedCode compatibility repair is client-side: create sessions with a non-default placeholder title and replace that placeholder with a deterministic title derived from the first user prompt before dispatch. This avoids modifying or restarting the protected native OpenCode backend.
