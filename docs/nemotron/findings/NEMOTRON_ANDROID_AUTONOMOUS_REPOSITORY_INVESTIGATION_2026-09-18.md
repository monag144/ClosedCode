# Nemotron Finding — Android Autonomous Repository Investigation — 2026-09-18

**Status:** POSITIVE PRODUCT FINDING  
**Evidence class:** Director-provided live Android user test plus Heavy Engineer interpretation  
**Project:** ClosedCode

## Finding

Nemotron is not merely answering questions about a repository from prompt context.

During the Director's live Android test, Nemotron operated the ClosedCode native agent loop and invoked real project tools against the selected workspace.

The observed investigation included agent activity corresponding to:

- workspace listing;
- workspace search;
- workspace reads;
- inspection of Android and backend source;
- inspection of provider/passthrough implementation;
- inspection of prior Z.AI/GLM evidence.

Heavy Engineer reported observed searches for subjects including:

- GLM 4.7;
- Z.AI / zai;
- provider adapter;
- passthrough;
- 429;
- ClosedCodeApi.

Relevant files inspected reportedly included:

- `MainActivity.java`;
- `ClosedCodeApi.java`;
- `passthrough_server.py`;
- provider documentation/evidence;
- relevant OpenCode provider transformation/source material.

## Interpretation

This is meaningful Android-client acceptance evidence.

It demonstrates that the installed ClosedCode client can drive Nemotron through the native `/agent` path and expose real tool execution rather than merely presenting a model-generated narrative.

That materially strengthens the earlier synthetic/backend acceptance evidence.

## Quality of Nemotron's diagnosis

Nemotron correctly recovered an important historical fact:

- prior Z.AI testing had shown non-stream requests returning HTTP 429 while streaming requests could succeed.

Nemotron then moved close to the current implementation defect but initially stopped one layer short.

The Android method name `streamAgentPrompt` is potentially misleading: Android receives a streaming SSE connection from the local ClosedCode backend, but the backend's upstream GLM agent completion path was still using `"stream": false`.

Thus the local Android/backend leg was streaming while the actual backend→Z.AI leg was not.

That distinction explains why the Android UI could show live tool activity while GLM still hit the same non-stream behavior previously associated with 429s.

## Grounding limitation observed

Nemotron also mixed in generic OpenCode guidance such as `/connect` or `/models` that does not precisely describe the ClosedCode Android UI.

Assessment:

**strong autonomous repository investigation with real tool use, but not yet perfect runtime/product grounding.**

This is a product-quality finding, not a reason to reject the agent architecture.
