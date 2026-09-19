# ClosedCode Android User Acceptance Test — 2026-09-18 23:16 PDT

**Status:** RED / REAL USER-DEVICE ACCEPTANCE FAILURE  
**Evidence class:** Director-provided live Android test + screenshot  
**Repository:** `monag144/ClosedCode`  
**Branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`  
**Checkpoint context:** Op275 hard stop remains active; this non-Relay record does not authorize Op276.

## Test context

The Director manually exercised the installed ClosedCode Android application after the Heavy Engineer Op275 checkpoint.

Visible application state in the supplied screenshot:

- app title: `ClosedCode`
- connection state: `connected`
- session title: `Number 123`
- workspace: `~/ClosedCode`
- selected model shown at capture: `GLM-4.7-Flash`
- agent status shown at capture: `Agent complete`

Visible user prompts:

- `123`
- `hello`
- `Hi`

Visible ClosedCode result:

`Agent: provider HTTP 429 after 3 attempt(s)`

## Director-reported routing

The Director reports:

- `123` was invoked through NVIDIA Nemotron;
- `hello` was invoked through NVIDIA Nemotron;
- `Hi` was invoked after selecting GLM-4.7-Flash;
- the visible ClosedCode provider error appeared only after the GLM request.

The Director's acceptance conclusion is that the application is **not currently working as a usable chat/coding-agent experience**.

## Expected target models

The Heavy Engineer qualification history establishes the intended exact models as:

### NVIDIA

`nvidia/nemotron-3-ultra-550b-a55b`

This is the exact NVIDIA model previously live-qualified by HE8.

### Z.AI

`glm-4.7-flash`

This is the exact Z.AI target previously live-qualified by HE8.

The connected catalog also previously exposed `glm-4.7-flashx`, but the ratified/qualified target in this campaign is `glm-4.7-flash`.

## Prior provider evidence relevant to this failure

HE8 Op223 previously observed on `glm-4.7-flash`:

- non-stream response: HTTP 429;
- Z.AI business code: `1305`;
- message: service may be temporarily overloaded, try again later;
- a streaming request in the same qualification returned HTTP 200 and valid SSE.

HE8 later live-qualified `glm-4.7-flash` successfully in Op247 through the native agent path.

Therefore this user-visible 429 must not automatically be classified as exhausted quota merely from the outer HTTP status.

## Diagnostic weakness exposed by user test

The Android UI currently surfaces only:

`provider HTTP 429 after 3 attempt(s)`

That message is insufficient to distinguish among materially different provider conditions such as:

- request-rate limit;
- temporary provider overload;
- account/package usage exhaustion;
- model-plan exclusion;
- other provider business-code conditions.

The user-facing error should preserve the sanitized provider business code and useful message when available.

For Z.AI, an error should ideally surface enough information to distinguish examples such as:

`HTTP 429 / code 1305 / temporary overload`

from an actual quota/plan limit.

## User acceptance result

### NVIDIA/Nemotron

**RED / visible response path not accepted.**

The Director reports two user prompts routed through Nemotron (`123`, `hello`) without a usable visible assistant response in the captured session.

This record does not infer whether the failure occurred in:

- provider invocation;
- response parsing;
- SSE/event delivery;
- Android rendering;
- session/history correlation;
- request completion handling.

That must be diagnosed from runtime evidence.

### Z.AI / GLM-4.7-Flash

**RED / provider request failed visibly.**

The `Hi` request produced:

`Agent: provider HTTP 429 after 3 attempt(s)`

Prior HE8 evidence makes temporary overload a plausible explanation, but the current Android error does not expose the Z.AI inner business code, so the exact cause of this specific user attempt remains unproved.

## Acceptance implication

Backend/provider qualification performed by Heavy Engineer is not sufficient to declare the Android product accepted.

The current required product gate is:

**A real user prompt entered in the installed Android app must produce a visible, correct agent response and, for a coding task, a functioning Android-client → provider → agent-tools → completion loop.**

Current user acceptance: **RED**.

## Recommended bounded diagnosis after checkpoint release

Do not rebuild architecture blindly.

For the first authorized post-Op275 work:

1. reproduce one minimal Nemotron prompt from Android;
2. correlate Android request ID, adapter request, upstream result, history persistence, SSE/events, and final UI rendering;
3. reproduce one GLM prompt;
4. retain and display sanitized Z.AI business code/message on failure;
5. distinguish provider-side 429/overload from ClosedCode transport/rendering failures;
6. only then patch the smallest proved defect.

This test result itself does not release the Op275 hard checkpoint.

## Provider/model double-check — external documentation

### NVIDIA target

The intended exact model remains:

`nvidia/nemotron-3-ultra-550b-a55b`

NVIDIA's current Build/NIM model page describes this as an agentic/reasoning/tool-calling model with a 1M-token context window and exposes a free prototype endpoint.

NVIDIA's NIM/API guidance states that hosted free/trial endpoint rate limits are evaluation/prototyping limits and can vary by model and concurrent demand; the signed-in NVIDIA account view is the correct place to verify the live allowance.

Therefore a public fixed RPM number should not be hard-coded into ClosedCode from third-party anecdotes.

### Z.AI target

The campaign's intended exact Z.AI model remains:

`glm-4.7-flash`

Z.AI's current public developer-document index now foregrounds newer GLM-5.3 / GLM-5.3-Flash models. The project's use of GLM-4.7-Flash is therefore a historical/qualified target rather than the newest model family.

Z.AI's official Rate Limits documentation redirects to the signed-in account rate-limit page. The exact live allowance for the Director's account/key cannot be determined from a public static quota table.

Important distinction:

- prior HE8 `HTTP 429 + code 1305` evidence means temporary overload;
- a bare `HTTP 429` in the Android UI is insufficient to prove quota exhaustion;
- ClosedCode should expose the sanitized provider business code/message so overload, rate-limit, plan, and quota conditions can be distinguished.

Current external-provider documentation check does **not** change the ratified model target by itself. Any move from GLM-4.7-Flash to a newer GLM model should be a deliberate compatibility/quality decision after checking the connected catalog and provider entitlement.

