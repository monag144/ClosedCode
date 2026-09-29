# ERR-CC-RELAY-001 — Local GPT-Termux-Relay connection refused

**Tag:** `CC-RELAY-LOCAL-CONNECT`

## Signature

Observed in the GPT Relay diagnostic overlay as:

`TERMUX • ConnectException`

The reconstructed late-cycle failure also identified refusal to local endpoint:

`127.0.0.1:8765`

## Classification

Local localhost listener/transport failure between the Android relay client and the Termux-side Relay listener.

This is a separate failure class from GitHub DNS/HTTP/API errors.

## Known recovery evidence

After one such failure, the Director manually restarted the Relay watchdog/listener. A subsequent reduced heartbeat operation succeeded and returned a GREEN Relay heartbeat. That sequence supports listener availability as the immediate failure layer.

## Possible causes

Without stronger runtime evidence, preserve these as hypotheses only:

- Relay listener process exited;
- Android/Termux process was killed or suspended;
- watchdog restart lag;
- port was temporarily not bound;
- local process/resource pressure;
- listener startup race.

## Required evidence on recurrence

Capture, without mutating protected Relay source:

- UTC timestamp;
- whether TCP port 8765 is listening;
- relevant Relay/watchdog process presence;
- recent listener/watchdog logs if safely available;
- one tiny heartbeat after recovery;
- whether ClosedCode source/Git state changed before the failure.

## Related incident

`docs/incidents/CLOSEDCODE_GITHUB_NETWORK_AND_RELAY_CONNECTIVITY_INCIDENT_2026-09-17.md`

## Related solution

`docs/troubleshooting/Solutions/SOL-CC-RELAY-001_RELAY_LISTENER_RECOVERY.md`

## Historical rule

A failed operation remains RED/ACTION_FAILED even if the listener is restarted and the next heartbeat succeeds.