# ClosedCode 0.8.13 — Long-Horizon Execution Acceptance

Timestamp UTC: `2026-09-20T04:46:45Z`
Heavy Engineer: **10**
Qualification request: `marathon-request-1789878626666`
Qualification session: `marathon-session-1789878626666`
Backend version: **0.8.13**

## Result

**GREEN — long-horizon execution acceptance is closed.**

This acceptance applies to the long-horizon execution/retention/finalization qualification only. It does **not** close deep cancellation, ASK/YOLO permission regression, Android correctness work, integrated product regression, or release-candidate APK acceptance.

## Evidence

- Accepted by qualification harness: **YES**
- Terminal outcome: **completed**
- Cancelled: **NO**
- Successful tool actions: **120**
- Unique invocation signatures: **104**
- Context compactions: **7**
- Scheduled steering posted/applied: **50, 85, 95 / all 3 applied**
- Finalization boundary: **triggered at 120 successful tools**
- Finalization retries: **1**
- Final assistant characters: **7073**
- Final SHA-256: `8b0f129acb92768dd0abb35fb808c89e16cbe98ba731b64d4c64d4764a6e5d06`
- Exact original-area markers: **all 8 present exactly once and non-empty**
- Exact preservation/read-only/definition-of-done/steering markers: **all present exactly once**
- Permission events: **0**
- Recoverable tool errors: **1** (`workspace_read`)
- Guardrail events: **0**

The single `workspace_read` tool error is retained as evidence and is not treated as a blanket veto: the configured error policy is observe-and-report, the mission continued, the provider completed naturally after the bounded synthesis transition, the harness accepted the result, and the complete final-report contract was preserved.

The 120-tool setting remains an opt-in qualification upper boundary, not a universal production mission limit.

## Next Core qualification phase

**Deep cancellation after substantial autonomous activity and compaction.**

That phase must independently prove responsive cancellation and absence of orphaned provider, permission, retry, observer, or runtime state.
