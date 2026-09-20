# ClosedCode 0.8.13 — ASK/GUARDED Permission Acceptance

Timestamp UTC: `2026-09-20T05:27:36Z`
Heavy Engineer: **10**
Backend version: **0.8.13**

## Result

**GREEN — ASK/GUARDED permission regression is closed.**

This acceptance is based on three independent disposable-workspace requests exercising the guarded `workspace_write` boundary.

## Proof 1 — Allow after an actual wait

- Exactly one `workspace_write` permission event was emitted.
- Target was absent when permission was requested.
- Approval was deliberately withheld for **2.0002076029777527 seconds**.
- Target remained absent throughout the pending interval.
- Decision `allow` resolved the permission.
- Exactly one write entered `running` and exactly one write completed.
- Resulting content was exactly `ASK_ALLOW_PROOF_417`.
- Terminal state was `completed`, not cancelled.
- Final assistant response length: **127 characters**.

## Proof 2 — Reject blocks mutation

- Exactly one `workspace_write` permission event was emitted.
- Decision `reject` resolved the permission.
- The guarded write produced **zero running events** and **zero completed events**.
- One rejected/error tool result was returned to the agent.
- Target remained absent before and after rejection.
- Agent settled with a truthful `completed` terminal after the denied action.
- Final assistant response length: **208 characters**.

## Proof 3 — Cancellation interrupts a pending permission

- Exactly one `workspace_write` permission event was pending.
- No mutation had begun.
- Cancellation was posted without sending Allow or Reject.
- Cancel-to-terminal latency observed: **0.004168594256043434 seconds**.
- Terminal state was `cancelled` with `cancelled=true`.
- Write emitted zero running, completed, and error execution events.
- Target remained absent.
- A second cancel after terminal reported the request inactive.
- Attempting to resolve the old permission ID afterward returned `resolved=false`.
- Session history remained valid and no established non-loopback provider socket remained after terminal.

## Acceptance boundary

ASK/GUARDED now has direct evidence that:

1. **Allow releases a guarded mutation only after explicit approval.**
2. **Reject prevents the guarded mutation from executing.**
3. **Cancel interrupts an unresolved permission wait without executing the mutation or leaving stale permission state.**

This does not close YOLO/FULL DANGER behavior, remaining Android correctness work, integrated product regression, or release-candidate APK acceptance.

## Next Core qualification phase

**YOLO/FULL DANGER regression on a disposable fixture.**
