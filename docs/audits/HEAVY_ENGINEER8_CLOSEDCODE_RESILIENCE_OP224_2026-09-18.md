# HE8 Operation Resilience — Op224

Status: GREEN / startup usability
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP224.add-and-prove-passthrough-startup-helper
Relay status: OK
Exit code: 0

Repository:
- branch: closedcode/android-cleanroom-opencode-mobile-20260916
- reconciled docs-only remote to 770a3eb5afe42fa72b316f4181083b3a05a5dc84
- implementation commit: 5c8da0b99bf7decb84b24863722742316475c816
- push: GREEN
- final worktree: clean

Implemented:
- added scripts/closedcode/ensure-passthrough.sh
- ClosedCode-owned state directory defaults to ~/.local/state/closedcode
- helper checks /health first and reuses an already healthy sidecar
- helper refuses to trample an occupied but unhealthy port
- helper starts run-passthrough.sh detached with nohup
- helper writes PID and log state with restrictive permissions
- helper waits boundedly for /health and reports explicit success/failure

Live proof:
- first call: PASSTHROUGH_STATUS=STARTED
- PID: 7364
- /health: healthy=true, service=closedcode-passthrough, version=0.2.1, bind=loopback-only, nvidia=true, zai=true
- second call: PASSTHROUGH_STATUS=ALREADY_HEALTHY
- process: passthrough_server.py --host 127.0.0.1 --port 4097
- state dir mode: 0700
- PID file mode: 0600
- log file mode: 0600

Protected/live state:
- GPT-Termux-Relay mutation: none
- live OpenCode runtime replacement: none

Governance:
Op225 is the mandatory 25-operation hard checkpoint from the recovered Op200 anchor. No substantive Op226 work may be planned/prepared after Op225 is consumed without fresh Director authorization.
