# ClosedCode Project Charter — 2026-09-15

## Status
FOUNDATION / ACTIVE DESIGN

## Identity
ClosedCode is an Android-first coding-agent platform derived from the OpenCode codebase and maintained as an independent downstream fork.

ClosedCode exists to provide a coding-agent client/runtime that is diagnosable, provider-flexible, Android/Termux friendly, and under direct project control rather than dependent on opaque upstream assumptions.

## Upstream provenance
- Upstream: `anomalyco/opencode`
- Fork: `monag144/ClosedCode`
- Upstream default branch at fork creation: `dev`
- License: MIT; preserve upstream copyright and license notices.

## North star
A user with a valid provider credential and a supported model should be able to use that compute through ClosedCode without unrelated client/runtime assumptions preventing the request from reaching the provider.

Provider differences must be isolated behind explicit adapters rather than leaking across the application.

## Initial architecture
ClosedCode will retain useful OpenCode machinery where it is reliable, including agent/session/tool/server components, while treating each subsystem as replaceable.

Primary product layers:
1. Android client/UI owned by ClosedCode.
2. ClosedCode runtime/server derived from OpenCode.
3. Provider adapter layer.
4. Local execution bridge for Termux/files/Git/shell.
5. Diagnostics, retries, telemetry, and recovery as first-class features.

## Initial providers
Priority order:
1. NVIDIA / Nemotron
2. Z.AI / GLM
3. OpenAI-compatible providers
4. Additional providers as qualified

No provider should receive hidden preferential assumptions in core architecture.

## Android build baseline
The initial Android/Bionic build baseline is informed by the OpenCode 1.18.31 investigation:
- Bun 1.4.1 compiled with `splitting:true` reproduced the internal `/api/reference` and `/api/agent` failure.
- The same source under Bun 1.4.1 with `splitting:false` passed those gates.
- Bun 1.4.0 compiled control also passed.
- Direct source execution under both Bun versions passed.

Until superseded by stronger evidence, Android/Bionic ClosedCode builds must explicitly qualify compile-time splitting behavior and must not assume upstream build defaults are safe.

## Diagnostics principle
Failures must be attributable to a layer. At minimum, diagnostics should distinguish:
- Android UI/client
- local ClosedCode server/runtime
- provider adapter
- remote provider/API
- model response
- tool invocation
- local execution bridge

Useful telemetry should include provider, model, HTTP status, retry count, latency, tool stage, token usage when available, sanitized errors, and correlation/trace IDs. Never expose secrets.

## Governance
- Timestamped design and audit records are historical evidence, not mutable CURRENT owners.
- Destructive operations require explicit Director authorization.
- Hard checkpoints remain binding when a Heavy Engineer mission declares them.
- Historical unauthorized operations remain historically unauthorized even when harmless.
- No credential values in Git, docs, prompts, logs, telemetry, or screenshots.
- Upstream OpenCode provenance and MIT license text must be preserved.

## Immediate objective
Qualify the repaired Android runtime path, then move engineering authority from the temporary OpenCode-repair workspace into this fork. Subsequent Android/provider work should target ClosedCode rather than patching the installed upstream runtime directly.
