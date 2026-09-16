# Heavy Engineer 6 — Forensic Audit, Operations 86–95

Date: 2026-09-16  
Mission: GPT-Termux-Relay Ops 76–85 damage assessment  
Canonical report repository: `monag144/ClosedCode`  
Forensic branch: `forensics/gpt-termux-relay-ops76-85-20260916`

## Operations covered

- **86 — UNPROVED / consumed by Director accounting.** Initial ClosedCode workspace command was not captured by the relay. No shell mutation proved.
- **87 — UNPROVED / consumed by Director accounting.** Reissue still did not yield the intended forensic result. No shell mutation proved.
- **88 — RED.** ClosedCode fetch succeeded, then the command failed because it assumed `refs/remotes/origin/dev` existed locally. Original staged `packages/opencode/script/build-termux.ts` remained preserved. Relay mutation: none.
- **89 — GREEN.** Verified remote `dev` and forensic branch at `f1a1bbd8d58b4c1cd738211d967a63d80764d74c`; created clean isolated worktree `~/ClosedCode-forensics-ops76-85` on the authorized forensic branch. Original staged file remained preserved. Relay mutation: none.
- **90 — RED / PACKET_REJECTED.** `command_b64 is not valid base64`; command never reached shell. No mutation.
- **91 — RED.** Packet executed but shell exited code 1 immediately after begin marker; exact failing shell step was not proven. No Relay mutation proved.
- **92 — RED with substantive evidence captured.** Read-only Relay Git/audit capture succeeded, then ClosedCode commit failed because Git author identity was unset. Evidence file SHA256 `bc265b6eac9a2cbfffce02c8cb0b64b0ad12e5564d64275a9c3d96f84644359c`. Relay mutation: none.
- **93 — RED / PACKET_REJECTED.** Invalid Base64; nothing executed. No mutation.
- **94 — GREEN.** Verified the Op92 evidence was the only staged path and committed it in ClosedCode with one-shot Git identity only. Commit `64b5cdbebce8035dd491a8332c84eb1294c9f4ba`. Persistent Git identity change: none. Relay mutation: none.
- **95 — RED / PACKET_REJECTED.** Invalid Base64; nothing executed. No mutation.

## Actual mutations

Authorized mutations were limited to ClosedCode:
- creation of the forensic worktree/branch,
- creation and commit of `docs/forensics/evidence/OP92_RELAY_GIT_DIAGNOSTIC_AND_AUDIT_EVIDENCE_2026-09-16.txt`.

No forensic operation 86–95 intentionally edited, committed, switched, reset, fetched, rebuilt, installed, restarted, repaired, or cleaned the GPT-Termux-Relay repository/runtime.

## Relay evidence established by Operation 92

Relay checkout observed:
- path: `/data/data/com.termux/files/home/GPT-Termux-Relay-standalone`
- branch: `development/mcp-apk-control-plane-20260916`
- HEAD: `735c5e44f0fc98daf81e08e7fc51d861d86a64c1`

Known pre-Op76 baseline object:
`85c90cc067b51c221720034f8374c3c4648174a9`

Reflog evidence showed the experimental branch was created from the baseline on 2026-09-16.

Five experimental commits were independently present:
`4a272c2d3634189c4c13968ccd689da52b5445bb`
`2c25f8b57ee4f3f0ab072aefa813b610a7e3ada9`
`772521bf3b996c15e7deac496e9c749854b33dbb`
`f8c6c4c622a44a7e5dac2d62a207aa9f224762fc`
`735c5e44f0fc98daf81e08e7fc51d861d86a64c1`

Baseline→experimental source map proved:
- `termux_relay/relay.py` blob unchanged.
- `termux_relay/socket_relay.py` modified.
- `termux_relay/mcp_adapter.py` added.
- `termux_relay/mcp_adapter_selftest.py` added.
- Android Gradle, manifest, BridgeClient, strings modified.
- `AgentActivity.java` added.
- Ops 76–80 and Ops 81–85 audit documents added.

## Failures and governance

Historical REDs and rejected packets remain RED and are not rewritten by later recovery.

Known failure classes:
- invalid `command_b64`: already documented in the Relay Error/Solution dictionary.
- ClosedCode commit with unset author identity: documented as a separate correlated Error/Solution pair; recovery uses one-shot `git -c user.name=... -c user.email=... commit` only.

Director accounting rule in this mission: a retry consumes the next operation number. That rule governs 86–100 even where older troubleshooting documentation describes retrying under the same operation number.

## Audit-vs-forensic discrepancies

No contradiction has yet been proven between the Ops 76–85 audit documents and independent Git-object evidence. Live installed-package/runtime claims remain unverified and must not be promoted from audit-only to proven until device package/runtime evidence is collected.

## Unresolved unknowns

- exact installed Android package versionCode/versionName and APK hash,
- signing-certificate relationship between installed package and experimental APK,
- whether the experimental APK was ever installed,
- current listeners/socket behavior and authentication/config hashes,
- provenance of any live Relay process,
- whether experimental MCP code entered live execution outside the disposable Ops 80–81 tests.

## Next bounded target

Perform read-only APK/package/runtime provenance capture, then produce the contamination map and final forensic report before mandatory Operation 100 checkpoint.
