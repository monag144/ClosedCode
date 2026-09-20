# Heavy Engineer 10 — ClosedCode Audit Ops411–415

Timestamp UTC: `2026-09-20T05:03:11Z`
Window: **Ops411–415 exactly**
Pre-audit HEAD: `68ba4d458b8a116af9e70c4bca2775b35fefd092`

## Operation ledger

### Op411 — GREEN long-horizon acceptance closure
- Revalidated the completed 0.8.13 long-horizon qualification contract.
- Closed long-horizon execution acceptance with 120 successful tools, 104 unique signatures, 7 compactions, steering 50/85/95 applied, completed terminal, one bounded finalization retry, and complete eight-area final markers.
- Retired the completed qualification observer through its authenticated done-only shutdown endpoint.
- Left exactly one healthy backend and zero marathon observers.

### Op412 — GREEN deep-cancellation launch
- Launched one fresh read-only qualification against the exact original mission.
- Configured cancellation at 90 successful tools, steering at 50/85, no finalization boundary, ASK autonomy, and zero allowed permission events.
- Request: `marathon-request-1789879900460`.
- Session: `marathon-session-1789879900460`.

### Op413 — GREEN bounded deep-run capture
- Same uninterrupted request advanced from 10 to 44 successful tools during the observation.
- Reached 44 unique invocation signatures and 2 context compactions.
- Zero errors and zero permission events.
- Cancellation had not yet been posted because the configured 90-tool threshold had not been reached.

### Op414 — RED preflight control-data failure
- Relay operation was consumed and failed before runtime observation or mutation.
- Terminal output: `ERROR=HARNESS_SHA_MISMATCH`.
- Current harness SHA-256: `0b2793bf31d760d2cc0738321b3e3495af844b11480c3444629aa437674901d4`.
- Harness SHA-256 reconstructed directly from source-repair commit `957a78551ca35241dcb73272864794e701c3cb15`: `0b2793bf31d760d2cc0738321b3e3495af844b11480c3444629aa437674901d4`.
- Current harness matches that committed repair exactly: **YES**.
- Op414 embedded expected literal: `0b2793bf31d760d2cc0738321b3e3495af844b11480c3444629aa437674901d4c9`.
- Embedded literal length: **66** hexadecimal characters; SHA-256 requires 64.
- Classified cause: **INVALID_EXPECTED_SHA_LITERAL_IN_OP414_PRECHECK**.
- Therefore Op414 does **not** establish a product/source regression. It is preserved as a RED Heavy Engineer control/preflight defect.

### Op415 — mandatory audit snapshot
Deep-cancellation classification: **RUNNING_DEEP_CANCELLATION_QUALIFICATION**
Cancellation contract status: **NOT_TERMINAL**
Completed tools: **72**
Unique invocation signatures: **61**
Compactions: **26**
Permissions: **0**
Steering posted: **50**
Steering applied: **1**
Cancellation posted: **NO**
Harness accepted: **PENDING**
Summary exists: **NO**
Exact marathon owner count: **1**
Exact backend owner count: **1**

## Captured deep-cancellation state

```json
{
    "accepted": null,
    "cancelPosted": false,
    "classification": "RUNNING_DEEP_CANCELLATION_QUALIFICATION",
    "compactions": 26,
    "completedTools": 72,
    "done": false,
    "errors": [],
    "permissions": 0,
    "steeringApplied": 1,
    "steeringPosted": [
        50
    ],
    "summaryExists": false,
    "terminal": {},
    "toolErrors": 0,
    "uniqueInvocationSignatures": 61
}
```

## Audit assessment

The long-horizon gate remains closed GREEN from Op411. The project then moved directly into the ordered deep-cancellation phase; there was no shift to Android UI work or unrelated engineering.

Op414's RED result is retained without reinterpretation. Direct repository evidence shows that the working harness is unchanged from the committed 0.8.13 repair. The failed precondition came from the expected SHA literal embedded in the Op414 Relay packet, not from a detected source mutation.

Deep-cancellation credit is granted only if its actual terminal contract is GREEN. If Op415 captured `NOT_TERMINAL`, Op416 should perform the remaining teardown/certification work that Op414 never reached. If the run remains active, Op416 should continue observing the same request rather than launch a replacement.

No source code, backend process, qualification request, or protected Relay process is mutated by Op415 itself. The only repository additions are this mandatory audit and the paired formal review.
