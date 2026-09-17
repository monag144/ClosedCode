# ERR-CC-BACKEND-001 — Backend recovery incorrectly assumed Bun was required

**Tag:** `CC-BACKEND-NATIVE-OPENCODE-OWNER-MISSED`  
**Status:** CONFIRMED  
**First observed operation:** `HEAVY-ENGINEER7-CLOSEDCODE-OP159.recover-icon-build-backend-installer`  
**Date:** 2026-09-17

## Signature

Backend recovery aborted with:

`BACKEND_RECOVERY=RED_BUN_ABSENT`

The operation had attempted to launch the repository TypeScript entrypoint through Bun.

Subsequent read-only archaeology proved:

- `bun`: absent
- native `opencode`: present at `/data/data/com.termux/files/usr/bin/opencode`
- native OpenCode version: `1.18.31`
- repository CLI includes the existing `serve` command
- `serve` delegates to `Server.listen(opts)`

## Meaning

The failure was not absence of the backend runtime. It was an ownership/reuse mistake: the operation selected the repository development toolchain instead of the already-installed native OpenCode runtime that owns the service on this Android/Termux environment.

## Safety

Do not install or upgrade Bun merely to recover the ClosedCode backend. Do not mutate GPT-Termux-Relay. Prefer the existing native `opencode` executable when it is present and version-proven.