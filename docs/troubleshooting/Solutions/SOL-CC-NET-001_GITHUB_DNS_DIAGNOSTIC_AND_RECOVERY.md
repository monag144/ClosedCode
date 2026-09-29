# SOL-CC-NET-001 — Diagnose and recover GitHub DNS/network failure

**Tag:** `CC-NET-GITHUB-DNS`

Use this when the matching error signature is a hostname/name-resolution failure such as:

`gaierror(-3, 'Temporary failure in name resolution')`

## Goal

Determine which layer failed before retrying meaningful work:

- DNS resolution;
- generic internet reachability;
- GitHub HTTPS;
- GitHub API/raw-content host;
- Git remote transport;
- local Relay listener;
- ClosedCode backend.

## Safe recovery sequence

1. **Do not immediately rerun the original mutating command.** Preserve the failed operation as failed.
2. Record UTC time and current repository/branch/HEAD if the local Relay is reachable.
3. Test DNS resolution independently for:
   - `github.com`
   - `api.github.com`
   - `raw.githubusercontent.com`
4. Test HTTPS connectivity to those hosts with short bounded timeouts. Record status/exception only; do not print credentials or auth headers.
5. Run a read-only `git ls-remote` against the intended Git remote.
6. Test a non-GitHub public hostname to distinguish GitHub-specific reachability from general DNS/network failure.
7. Separately verify localhost services:
   - GPT-Termux-Relay listener on `127.0.0.1:8765`;
   - ClosedCode/OpenCode backend health endpoint.
8. Only after the layer is identified and basic probes are GREEN should the substantive operation be reissued as a **new operation number**.

## Interpretation matrix

- All DNS lookups fail: resolver/network environment problem likely.
- Only `raw.githubusercontent.com` fails DNS: host-specific resolver/path issue likely.
- DNS succeeds but HTTPS connect fails: routing/TLS/egress problem.
- HTTPS succeeds but GitHub returns 401/403: authentication/permission problem; this is a different error class.
- HTTPS succeeds but 429: rate limiting; different error class.
- GitHub probes succeed but `127.0.0.1:8765` fails: local Relay listener problem; use the Relay recovery record instead.
- Relay is GREEN but backend health fails: ClosedCode/OpenCode backend problem, not GitHub.

## Evidence handling

Store the exact diagnostic results in the relevant audit/incident. Preserve contradictions rather than reconciling them by assumption.

Never output provider keys, GitHub tokens, Authorization headers, private signing material, or other secrets.

## Related error

`docs/troubleshooting/Errors/ERR-CC-NET-001_GITHUB_DNS_RESOLUTION_FAILURE.md`

## Full playbook

`docs/diagnostics/CLOSEDCODE_NETWORK_FAILURE_CAPTURE_PLAYBOOK.md`