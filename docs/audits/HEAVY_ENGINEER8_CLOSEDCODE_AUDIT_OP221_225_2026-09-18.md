# Heavy Engineer 8 ClosedCode Audit — Ops221-225

Mission: ClosedCode NVIDIA/GLM passthrough delivery
Anchor: recovered Op200 checkpoint
Audit window: Ops221-225
Repository: /data/data/com.termux/files/home/ClosedCode
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Boundary/checkpoint operation: Op225

## Op221 — GREEN / governance recovery only
Recovered the failed Op220 audit + twenty-operation review boundary.
Evidence included:
- governance artifacts reconciled
- sidecar 0.2.1 persistence/context source present
- Android passthrough/history source present
- APK SHA256 2c4dd24cafe4de76cd0e19bcb15ffb536ef0553ba550a513ab1d8eb0430696fd
- live OpenCode healthy 1.18.31
- protected Relay watchdog/socket relay alive
- final worktree clean
- no protected Relay mutation
- no live OpenCode replacement

## Op222 — RED / PACKET_REJECTED
Intended Z.AI/GLM + provider-catalog qualification. Invalid command_b64 was rejected before execution.
No provider/catalog/process/source/APK/runtime mutation.

## Op223 — GREEN / Z.AI qualification + picker catalog proof
Catalog:
- nvidia connected=true with nvidia/nemotron-3-ultra-550b-a55b
- zai connected=true with glm-4.7-flash and glm-4.7-flashx
- existing Android picker consumes the OpenCode connected provider/model catalog

Z.AI glm-4.7-flash:
- non-stream: HTTP 429, upstream code 1305, temporary-overload message
- stream: HTTP 200, SSE chunks received, reasoning_content observed, [DONE] observed
- response model matched glm-4.7-flash
- finish_reason=length at deliberately small token limit

Conclusion:
Z.AI endpoint/auth/model routing is live and streaming-qualified; non-stream remains intermittently provider-capacity-limited.

## Op224 — GREEN / startup usability
Added and pushed scripts/closedcode/ensure-passthrough.sh.
Implementation commit:
5c8da0b99bf7decb84b24863722742316475c816

Proved:
- PASSTHROUGH_STATUS=STARTED
- sidecar healthy on 127.0.0.1:4097
- version 0.2.1
- nvidia=true, zai=true
- second helper invocation returned ALREADY_HEALTHY
- state dir mode 0700
- PID file 0600
- log file 0600
- final worktree clean
- no protected Relay mutation
- no live OpenCode replacement

## Op225 — RED / PACKET_REJECTED
Mandatory hard-checkpoint state-capture packet was rejected because command_b64 was invalid.
No shell execution and no mutation occurred.

Because Op225 was consumed, the hard stop activated immediately.

## Window mutation summary

Source:
- Op224 added only scripts/closedcode/ensure-passthrough.sh.
- No other product source mutation in Ops221-225.

Git:
- Op224 implementation commit 5c8da0b99bf7decb84b24863722742316475c816 pushed GREEN.
- Direct GitHub audit/resilience documentation commits advanced remote docs state.
- Op225 did not execute and made no Git mutation.

Runtime/process:
- Op224 intentionally started the ClosedCode-owned sidecar persistently on loopback port 4097.
- No OpenCode runtime replacement.
- No GPT-Termux-Relay runtime/config/source mutation.

Package/APK:
- No new APK build in Ops221-225.
- Last proven APK remains ClosedCode 0.1.8-cleanroom, 95,572 bytes, SHA256 2c4dd24cafe4de76cd0e19bcb15ffb536ef0553ba550a513ab1d8eb0430696fd from Op219.

Shared storage:
- No new shared-storage mutation in Ops221-225.

## Preserved failures
- Op222 RED / PACKET_REJECTED.
- Op223 Z.AI non-stream HTTP 429 / provider overload; streaming GREEN.
- Op225 RED / PACKET_REJECTED hard-checkpoint capture.

## Protected state
No established GPT-Termux-Relay source/config mutation in this window.
ClosedCode remains a separate project/package path.

## Governance
HARD STOP ACTIVE because Op225 was consumed.
Checkpoint evidence recovery is allowed; substantive mission continuation is not.

## Current checkpoint recovery need
Positively recapture:
- local branch/HEAD/worktree
- remote relationship
- sidecar 4097 health/process
- OpenCode 4096 health
- APK identity
- protected Relay repo/process state
- authoritative Ops221-225 ledger slice

No product advancement may be mixed into that recovery.
