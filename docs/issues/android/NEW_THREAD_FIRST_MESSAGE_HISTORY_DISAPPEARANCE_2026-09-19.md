# Android Issue — New-Thread First Message Disappears from Visible History — 2026-09-19

**Status:** OPEN / USER-OBSERVED  
**Surface:** ClosedCode Android client  
**Evidence class:** Director live-use report

## Observation

The Director created a new ClosedCode thread/session and cheekily sent the AGT qualification test prompt to the agent.

Immediately after sending, the text disappeared from the visible conversation history instead of remaining at the top of the new thread in chronological order.

## Expected behavior

When the first user message is sent in a new thread:

1. the user message should appear immediately in the transcript;
2. it should remain visible as the first chronological message;
3. subsequent tool events and assistant/model responses should appear after it;
4. re-rendering, streaming state changes, session creation, or agent startup must not remove it.

## Current unknowns

The observed symptom proves a visible transcript/history problem but does **not yet prove** which layer is responsible.

Possible classes to distinguish during diagnosis:

- message was never persisted;
- message was persisted but omitted from session-history reload;
- message exists in backend history but Android failed to render it;
- new-session/thread initialization replaced the in-memory transcript;
- streaming/agent-start state cleared or rebuilt the message list incorrectly;
- session ID/thread transition raced with prompt insertion.

Do not classify this as a backend persistence defect until the stored session/history is inspected.

## Acceptance condition

On a brand-new thread:

- send one user prompt;
- observe it remain visible immediately;
- allow the agent to begin tool/model work;
- refresh/reopen the thread;
- confirm the same prompt remains first in chronological history;
- confirm no duplicate or reordered copy appears.

## Priority

High usability priority.

A coding-agent transcript must be trustworthy as an audit trail. A disappearing initial instruction makes later tool activity and agent behavior difficult to interpret and undermines confidence in session continuity.
