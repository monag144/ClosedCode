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

## Runtime cache invalidation

OpenCode caches per-directory instance state. After changing project config, use the server's canonical instance-disposal endpoint before judging the repair:

`POST /instance/dispose?directory=<ClosedCode>`

The endpoint marks the workspace instance for disposal after the response and the server lifecycle invalidates the registered per-directory InstanceState caches. A stale already-created instance may otherwise continue reproducing the old failure after the config file itself has been corrected.

Do not restart or kill the whole backend merely to invalidate one known workspace when this canonical disposal path is available.

## Acceptance

Recovery is GREEN only after disposing the stale ClosedCode workspace instance and then proving all of the following against the same native backend:

1. `GET /global/health` succeeds.
2. `GET /agent?directory=<ClosedCode>` returns HTTP 200.
3. visible primary agents can be enumerated from the live response.
4. `GET /provider?directory=<ClosedCode>` returns HTTP 200.
5. `GET /session?directory=<ClosedCode>` returns HTTP 200.
6. repository worktree is clean after synchronization.

The removed references were developer convenience metadata, not required Android client functionality.