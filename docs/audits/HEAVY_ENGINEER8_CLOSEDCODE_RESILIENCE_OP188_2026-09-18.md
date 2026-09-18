# HE8 Operation Resilience — Op188

Status: GREEN / read-only reference schema trace
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP188.reference-service-schema-trace
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Local HEAD before/after: 6452767b80d69223a6f64fd633ffae7adf735cd2
Local worktree before/after: clean
Mutation: none

Purpose: trace Reference.Service schema/materialization and determine whether a missing reference.name can normally reach SystemPrompt.environment.

Findings:
- Reference.Service is implemented in packages/core/src/reference.ts.
- Draft.add requires a string name and stores sources in a Map<string, Source>.
- Finalization iterates [name, source] and constructs every materialized Reference.Info with that name at lines 65-71 for local references and 86-92 for git references.
- Reference.Service.list returns only materialized Info values.
- SystemPrompt.environment obtains Reference.Service.list(), filters only description != undefined, then sorts at session/system.ts:92 using a.name.localeCompare(b.name).
- Under the ordinary finalized Reference.Service path, name should therefore be present.
- The observed a.name failure cannot yet be explained simply as a normal reference lacking its map-key name.
- The next diagnostic should inspect the canonical Reference.Info schema and the LocationServiceMap/service provisioning path to determine whether malformed decoding, alternate service provisioning, or a wrong service/location instance can bypass the ordinary materializer.

No product source, runtime, Relay, APK, Git working tree, or shared storage changed.
