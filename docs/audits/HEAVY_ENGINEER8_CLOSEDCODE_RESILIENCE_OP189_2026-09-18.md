# HE8 Operation Resilience — Op189

Status: YELLOW / partial read-only diagnostic
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP189.reference-info-location-service-trace
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Local HEAD before/after: 6452767b80d69223a6f64fd633ffae7adf735cd2
Local worktree before/after: clean
Mutation: none

Purpose: inspect canonical Reference.Info schema and LocationServiceMap provisioning to explain the undefined .name crash in SystemPrompt.environment.

Findings:
- Canonical Reference.Info is declared in packages/schema/src/reference.ts.
- Reference.Info.name is required: name: Schema.String.
- Reference.Info.path is required and description is optional.
- Config references are stored as a string-keyed record; the config plugin iterates Object.entries and rejects invalid/empty aliases.
- Config plugin calls draft.add(name, source), and ordinary Reference.Service materialization then constructs Info with that name.
- Therefore a normally materialized/configured reference should not have an undefined name.
- LocationServiceMap is involved in SystemPrompt.environment and many other location-scoped services.
- The intended LocationServiceMap implementation body was not fully captured because relay stdout was truncated after a broad declaration listing.
- Exact root cause remains unproven.

Diagnostic direction:
The stronger remaining hypotheses are:
1. wrong/stale/mismatched location-scoped Reference.Service instance;
2. alternate construction/provisioning path bypassing ordinary Reference.Service materialization/schema guarantees;
3. malformed runtime state injected before the final materialized list.

Next:
Perform a narrowly bounded read of packages/core/src/location-service-map.ts and packages/core/src/location-services.ts, plus the exact SystemPrompt and Agent provisioning sites. Avoid broad recursive searches.

No product source, runtime, Relay, APK, Git working tree, or shared storage changed.
