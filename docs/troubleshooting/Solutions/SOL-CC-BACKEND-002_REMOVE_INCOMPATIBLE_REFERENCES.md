# SOL-CC-BACKEND-002 — Remove incompatible references block from ClosedCode project config

**Tag:** `CC-OPENCODE-REFERENCES-AGENT-STATE-CRASH`  
**Status:** ACTIVE COMPATIBILITY REPAIR  
**Date:** 2026-09-18

## Use when

Native OpenCode 1.18.31 is healthy, `/provider`, `/session`, and `/config` work, but project-scoped `/agent` fails in `Agent.state` and literal bisection proves any non-empty `references` block reproduces the crash.

## Repair

Remove only the project-level `references` block from `.opencode/opencode.jsonc`.

Preserve all unrelated configuration:

- `$schema`
- `provider`
- `permission`
- `mcp`
- `tools`

Do not remove custom agents or the project plugin because disposable isolation proved each works independently.

## Acceptance

Recovery is GREEN only when the real ClosedCode workspace satisfies all of the following against the same native backend:

1. `GET /global/health` succeeds.
2. `GET /agent?directory=<ClosedCode>` returns HTTP 200.
3. visible primary agents can be enumerated from the live response.
4. `GET /provider?directory=<ClosedCode>` returns HTTP 200.
5. `GET /session?directory=<ClosedCode>` returns HTTP 200.
6. repository worktree is clean after synchronization.

The removed references were developer convenience metadata, not required Android client functionality.