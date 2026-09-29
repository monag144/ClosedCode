# ClosedCode Network Failure Capture Playbook

**Purpose:** Capture enough evidence in one bounded diagnostic pass to distinguish GitHub/DNS problems, generic internet failures, local GPT-Termux-Relay listener failures, and ClosedCode/OpenCode backend failures.

This playbook is diagnostic only. It does not authorize protected-infrastructure mutation, credential changes, package installation, or feature work.

## Trigger

Use when any of the following occurs during ClosedCode work:

- `gaierror` / temporary name-resolution failure;
- GitHub/raw-content read unexpectedly fails;
- GitHub connector/source reads repeatedly stall or error;
- `TERMUX • ConnectException`;
- `127.0.0.1:8765` connection refusal;
- repeated retries create uncertainty about whether a mutation landed.

## First principle

Do **not** immediately rerun the original mutating command.

Preserve the failure, identify the layer, inspect project state, then retry under a new operation number if governance allows.

## Capture set

### 1. Identity and time

Capture:

- UTC timestamp;
- local repository path;
- branch;
- HEAD;
- short worktree status;
- intended operation number and governance boundary.

### 2. DNS layer

Resolve independently:

- `github.com`
- `api.github.com`
- `raw.githubusercontent.com`
- one unrelated public hostname as a control.

Prefer a small Python `socket.getaddrinfo()` probe because it works without relying on optional DNS command-line packages.

Record only success/failure and resolved addresses. Do not expose credentials.

### 3. HTTPS layer

With short bounded timeouts, test:

- `https://github.com/`
- `https://api.github.com/`
- a known public raw-content URL if available;
- one unrelated public HTTPS control host.

Record:

- DNS success/failure;
- connect/TLS success/failure;
- HTTP status when received;
- exact exception class/text.

Interpretation:

- DNS failure means no HTTP/API conclusion can be drawn.
- 401/403 indicates auth/permission semantics.
- 404 indicates resolved HTTP path/repository semantics.
- 429 indicates rate limiting.
- 5xx indicates server/gateway failure.

### 4. Git transport layer

Run a read-only remote probe such as:

`git ls-remote origin HEAD`

Do not fetch, merge, checkout, reset, clean, or push during this diagnostic unless separately authorized.

Record command exit code and whether a remote ref was returned.

### 5. Local Relay layer

Check localhost listener availability for the expected Relay endpoint:

- TCP `127.0.0.1:8765` listening/not listening;
- relevant Relay/watchdog process present/absent;
- recent existing logs if available through normal read-only operational paths.

Do not edit Relay source/config to diagnose ordinary listener loss.

### 6. ClosedCode/OpenCode backend layer

Check the expected local backend health endpoint separately from Relay.

Record:

- socket/listener state where safely visible;
- health HTTP status;
- whether a session/provider endpoint can be read without mutation, if needed.

This distinguishes "Relay is down" from "backend is down."

### 7. Interrupted-mutation state

If the failure occurred during a command that might mutate ClosedCode, capture before any retry:

- `git status --short`;
- staged diff names;
- unstaged diff names;
- untracked paths;
- HEAD and remote HEAD if safely reachable;
- relevant source-file hashes;
- build metadata/version;
- generated APK names/hashes if applicable;
- running build/process state.

Do not use `git clean`, reset, checkout-overwrite, or deletion merely to make the tree look clean.

### 8. Screenshot/error preservation

Record the exact visible error text and device clock time if a screenshot exists. Treat UI progress labels like `Fetching GitHub...` or `Searching the web` as activity evidence, not errors, unless an actual failure/result accompanies them.

If a screenshot includes personal/location information, do not commit the image to a public repository without explicit Director authorization. Transcribe only the engineering-relevant text.

## Compact diagnostic result format

Use a compact record such as:

- `TIME_UTC=`
- `REPO=`
- `BRANCH=`
- `HEAD=`
- `WORKTREE=`
- `DNS_GITHUB=`
- `DNS_API_GITHUB=`
- `DNS_RAW_GITHUB=`
- `DNS_CONTROL=`
- `HTTPS_GITHUB=`
- `HTTPS_API_GITHUB=`
- `HTTPS_RAW_GITHUB=`
- `HTTPS_CONTROL=`
- `GIT_LS_REMOTE=`
- `RELAY_8765=`
- `RELAY_PROCESS=`
- `BACKEND_HEALTH=`
- `INTERRUPTED_MUTATION=`
- `ERROR_SIGNATURE=`
- `SECRET_OUTPUT=NONE`

## Decision tree

### DNS fails broadly

Classify as resolver/network-environment failure. Do not diagnose GitHub auth/API from that result.

### DNS succeeds, GitHub HTTPS fails before HTTP

Classify as routing/TLS/egress failure pending additional evidence.

### GitHub returns explicit HTTP status

Classify based on that status; preserve the response and treat auth/rate-limit/server failure as a separate error class.

### GitHub is GREEN, Relay 8765 is refused

Classify as local Relay listener failure. Recover listener/watchdog through existing authorized operations, then issue a tiny heartbeat before project work.

### Relay is GREEN, backend health fails

Classify as ClosedCode/OpenCode backend failure.

### All layers GREEN after a transient failure

Record recovery, but do not rewrite the original failure. Reinspect the interrupted project state before retrying.

## Known 2026-09-16/17 precedent

The ClosedCode incident set established both:

- `raw.githubusercontent.com` temporary DNS/name-resolution failure;
- local Relay `ConnectException` / `127.0.0.1:8765` refusal.

See:

- `docs/incidents/CLOSEDCODE_GITHUB_NETWORK_AND_RELAY_CONNECTIVITY_INCIDENT_2026-09-17.md`
- `docs/troubleshooting/Errors/ERR-CC-NET-001_GITHUB_DNS_RESOLUTION_FAILURE.md`
- `docs/troubleshooting/Errors/ERR-CC-RELAY-001_LOCAL_RELAY_CONNECTION_REFUSED.md`

## Security

Never include in diagnostic output:

- GitHub tokens;
- provider API keys;
- Authorization headers;
- signing private keys;
- passwords;
- private connector credentials.

Hashes, HTTP statuses, hostnames, branch/commit identities, process/listener state, and non-secret error text are appropriate evidence.