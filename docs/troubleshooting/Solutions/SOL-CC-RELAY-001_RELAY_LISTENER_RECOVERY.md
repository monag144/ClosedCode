# SOL-CC-RELAY-001 — Recover local GPT-Termux-Relay listener availability

**Tag:** `CC-RELAY-LOCAL-CONNECT`

Use this when Android/Relay reports `ConnectException` or a refused connection to `127.0.0.1:8765`.

## Recovery sequence

1. Preserve the failed operation exactly as failed. Do not reuse its operation number.
2. Do not modify Relay source as part of routine recovery.
3. Check whether the expected listener/watchdog process exists and whether TCP port 8765 is bound.
4. If the Director has authorized normal watchdog/listener restart behavior, restart/recover the listener using the existing operational mechanism rather than editing code or configuration.
5. Issue one minimal heartbeat as the next Relay operation. The heartbeat should do no project mutation.
6. If the heartbeat succeeds, separately inspect the target project state before resuming any interrupted mutation. Do not assume the failed operation made zero partial changes unless direct evidence proves it.
7. Resume substantive work only under normal governance with the next sequential operation number.

## Distinguish from external network errors

A local listener failure can coexist with external GitHub/DNS failure. Diagnose them separately:

- `127.0.0.1:8765` refused → local Relay layer.
- `gaierror(...Temporary failure in name resolution...)` for `raw.githubusercontent.com` → DNS/network layer.
- HTTP 401/403/404/429/5xx from GitHub → GitHub HTTP/API layer.

## Evidence to record

- listener port state before/after recovery;
- process/watchdog state;
- heartbeat result;
- project branch/HEAD/worktree after recovery;
- exact mutation uncertainty for the interrupted operation;
- no protected Relay source mutation unless separately authorized.

## Related error

`docs/troubleshooting/Errors/ERR-CC-RELAY-001_LOCAL_RELAY_CONNECTION_REFUSED.md`

## Full diagnostic playbook

`docs/diagnostics/CLOSEDCODE_NETWORK_FAILURE_CAPTURE_PLAYBOOK.md`