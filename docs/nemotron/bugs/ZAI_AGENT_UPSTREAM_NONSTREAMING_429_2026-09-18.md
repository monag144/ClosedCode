# Nemotron Bug — Z.AI Agent Upstream Was Non-Streaming — 2026-09-18

**Status:** CONFIRMED IMPLEMENTATION BUG / HEAVY ENGINEER FOLLOW-UP ACTIVE

## Symptom

The Android ClosedCode client could display live tool events while a GLM-4.7-Flash agent request failed with:

`Agent: provider HTTP 429 after 3 attempt(s)`

Historical provider qualification had already shown a useful contrast:

- GLM-4.7-Flash non-stream request → HTTP 429;
- GLM-4.7-Flash streaming request → HTTP 200 with SSE.

## Root cause identified

The Android method is named `streamAgentPrompt` and the Android client receives SSE from the local ClosedCode provider adapter.

However, inside the native agent loop the backend's actual upstream Z.AI completion request used:

`"stream": false`

Therefore there were two different streaming boundaries:

1. local ClosedCode backend → Android: streaming;
2. ClosedCode backend → Z.AI/GLM: non-streaming.

The first did not make the second streaming.

## Why this matters

The implementation could appear to be a "streaming agent" from the Android UI while still exercising the exact upstream Z.AI request form previously associated with 429 behavior.

This is a real provider-path bug, not merely a UI-label problem.

## Intended repair direction

For the Z.AI native agent path:

- use the provider's real SSE streaming mode upstream;
- reconstruct the complete assistant/tool-call message required by the autonomous agent loop from streamed deltas;
- preserve tool-call correctness and conversation state;
- keep Nemotron on its already-working path unless evidence requires otherwise;
- preserve sanitized provider error/business-code details when failures occur.

## Acceptance gate

The repaired path should prove from the Android client that GLM can:

- receive a natural-language task;
- stream through the actual backend→Z.AI leg;
- emit/use tool calls correctly;
- continue after tool results;
- complete without the prior non-stream 429 failure mode under comparable conditions.

Historical 429s remain historical evidence.
