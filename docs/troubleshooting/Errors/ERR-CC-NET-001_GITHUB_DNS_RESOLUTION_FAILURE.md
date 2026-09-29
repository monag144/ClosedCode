# ERR-CC-NET-001 — GitHub raw-content DNS resolution failure

**Tag:** `CC-NET-GITHUB-DNS`

## Signature

Observed while ClosedCode/Heavy Engineer attempted a Python `urllib.request.urlopen()` read from `raw.githubusercontent.com`:

`URLError(gaierror(-3, 'Temporary failure in name resolution'))`

## Classification

Network/name-resolution failure before HTTP.

The failure occurs below the GitHub authentication/API layer. No HTTP status was received, so this signature by itself is **not evidence of**:

- invalid token;
- missing repository permission;
- branch protection;
- 404 path error;
- GitHub API rate limiting;
- GitHub HTTP 5xx.

## Known context

The failure appeared during the ClosedCode clean-room Android work alongside other screenshots showing successful GitHub/source inspection. This makes an intermittent resolver/network problem more plausible than a permanently invalid GitHub configuration.

A separate local Relay failure (`127.0.0.1:8765` connection refusal) also occurred in the same broader period and must not be conflated with this error.

## Evidence

See:

- `docs/incidents/CLOSEDCODE_GITHUB_NETWORK_AND_RELAY_CONNECTIVITY_INCIDENT_2026-09-17.md`
- `docs/incidents/HEAVY_ENGINEER6_OP149_150_CHECKPOINT_INTERRUPTION_2026-09-17.md`

## Diagnostic requirements on recurrence

Before retrying the substantive operation, capture:

1. UTC timestamp;
2. `socket.getaddrinfo()` results for `github.com`, `api.github.com`, `raw.githubusercontent.com`;
3. HTTPS status/reachability for those hosts;
4. read-only `git ls-remote` against the relevant remote;
5. whether other unrelated public hosts resolve;
6. exact exception class/text;
7. no credentials or Authorization headers.

## Related solution

`docs/troubleshooting/Solutions/SOL-CC-NET-001_GITHUB_DNS_DIAGNOSTIC_AND_RECOVERY.md`

## Historical rule

Do not relabel a failed operation GREEN merely because a later retry succeeds. Preserve the original DNS failure and record recovery separately.