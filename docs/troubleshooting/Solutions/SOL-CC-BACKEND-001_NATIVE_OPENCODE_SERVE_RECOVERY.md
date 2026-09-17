# SOL-CC-BACKEND-001 — Recover localhost backend with native OpenCode serve

**Tag:** `CC-BACKEND-NATIVE-OPENCODE-OWNER-MISSED`  
**Status:** ACTIVE RECOVERY PROCEDURE  
**Date:** 2026-09-17

## Use when

ClosedCode cannot reach `127.0.0.1:4096`, the repository package manager expects Bun, but the Termux host already has a native `opencode` executable.

## Procedure

1. Prove the native executable path and version with `command -v opencode` and `opencode --version`.
2. Confirm no existing healthy backend already owns `127.0.0.1:4096`.
3. Start the existing native runtime with the existing CLI surface:
   `opencode serve --hostname 127.0.0.1 --port 4096`
4. Redirect stdout/stderr to a project-scoped runtime log and retain a PID file.
5. Poll `http://127.0.0.1:4096/global/health`.
6. Treat the backend as GREEN only after the health endpoint responds successfully.
7. Do not install Bun, alter Relay, or create a parallel server architecture merely to recover the service.

## Acceptance

Recovery is GREEN when the native OpenCode process remains alive and `/global/health` on `127.0.0.1:4096` responds successfully.