# HE8 Operation Resilience — Op243

Status: RED / COMMAND_FAILED
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP243.prove-approved-agent-continuation-repeatability
Relay status: COMMAND_FAILED
Exit code: 1

Repository:
- local branch fast-forwarded to f46b8f4ffe38ed4acf9b4842397a7b0198b47848
- provider adapter remained healthy at version 0.7.0

NVIDIA A:
- permission allow resolved=true
- workspace_write ran/completed
- workspace_read ran/completed
- zero agent error events
- exact final response FINAL_NVIDIA_A
- non-cancelled terminal marker
- APPROVED_CONTINUATION=GREEN

NVIDIA B:
- failed before any permission or tool event
- provider returned HTTP 500 Internal Server Error
- artifact absent
- qualifier terminated with RuntimeError: NVIDIA_B artifact missing

Classification:
Historical RED remains RED. Evidence isolates the failure to transient upstream/provider reliability because the first identical NVIDIA approved continuation completed cleanly, while the second failed before the model emitted any tool call. No permission-gate or tool-result-format failure was observed in the failed case.

Mutation:
- only docs/test fast-forward occurred
- no product source mutation by Op243
- no protected GPT-Termux-Relay mutation
- no OpenCode runtime replacement

Next bounded target:
Add bounded retries for retryable upstream statuses (429/500/502/503/504) inside the ClosedCode native agent provider request loop, respecting cancellation and preserving explicit terminal errors after retry exhaustion. Re-run the same repeatability qualifier at Op244. Op245 remains the mandatory audit + twenty-operation review boundary.
