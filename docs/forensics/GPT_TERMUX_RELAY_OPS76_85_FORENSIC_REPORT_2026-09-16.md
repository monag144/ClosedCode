# GPT-Termux-Relay Operations 76–85 Forensic Report

Date: 2026-09-16  
Mission: read-only forensic investigation of GPT-Termux-Relay Operations 76–85  
Canonical report repository: `monag144/ClosedCode`  
Forensic branch: `forensics/gpt-termux-relay-ops76-85-20260916`

## Executive verdict

**BLAST RADIUS: RED.**

The protected Relay source checkout currently points to the experimental branch `development/mcp-apk-control-plane-20260916` at `735c5e44f0fc98daf81e08e7fc51d861d86a64c1`, rather than the proven pre-Operation-76 baseline `development/runtime-capability-engine` at `85c90cc067b51c221720034f8374c3c4648174a9`. The current working-tree `socket_relay.py` blob equals the experimental blob and differs from baseline. The core `relay.py` blob remains identical to baseline.

This proves **Relay source contamination** in the protected checkout. It does **not** by itself prove that experimental code was executing live at the time of capture.

## Evidence consulted

- Ops 76–80 audit from Relay Git object `735c5e44...`
- Ops 81–85 audit from Relay Git object `735c5e44...`
- Op92 Git/audit evidence, SHA256 `bc265b6eac9a2cbfffce02c8cb0b64b0ad12e5564d64275a9c3d96f84644359c`
- Op98 APK/package/runtime evidence, SHA256 `073a11278025187a34ae2c896506dd20edb152aa971b8cc8de33bb3dfe4b6617`
- Heavy Engineer 6 audit for Ops 86–95 at ClosedCode commit `d8ee375fdd658cc8455855655a6997c8023d2c54`

## Pre-Operation-76 baseline

**PROVEN**

- branch: `development/runtime-capability-engine`
- HEAD: `85c90cc067b51c221720034f8374c3c4648174a9`
- `relay.py` baseline blob: `35a5a589d79ddf93a2d51dbf24d88571b88df916`
- `socket_relay.py` baseline blob: `db68a58f1d5885f73c2eb94c19a10f5dbcaaecaa`

## Current Relay state

**PROVEN**

- path: `/data/data/com.termux/files/home/GPT-Termux-Relay-standalone`
- branch: `development/mcp-apk-control-plane-20260916`
- HEAD: `735c5e44f0fc98daf81e08e7fc51d861d86a64c1`
- current `relay.py` blob: `35a5a589d79ddf93a2d51dbf24d88571b88df916` — identical to baseline
- current `socket_relay.py` blob: `2b92fa5fb42d2ac6776bf4a5e71bb9b7ffad2fd8` — identical to experimental, different from baseline

## Operations 76–85 mutation ledger

- **Op76 — SAFE ISOLATED CHANGE / reconnaissance only.** No source mutation.
- **Op77 — SAFE ISOLATED CHANGE / reconnaissance only.** No source mutation.
- **Op78 — RELAY SOURCE CONTAMINATION precursor.** Experimental branch created; architecture document added.
- **Op79 — RELAY SOURCE CONTAMINATION.** Added MCP adapter/selftest and modified `socket_relay.py`; canonical execution still routes through `relay.process_text(...)`.
- **Op80 — RUNTIME / CONFIG CONTAMINATION, isolated disposable runtime only.** Historical RED harness failure; disposable mission-branch socket relay launched in isolated state.
- **Op81 — RUNTIME / CONFIG CONTAMINATION, isolated disposable runtime only.** Corrected harness proved real loopback MCP behavior against mission-branch code.
- **Op82 — SAFE ISOLATED CHANGE / reconnaissance only.**
- **Op83 — RELAY SOURCE CONTAMINATION.** `BridgeClient.java` modified for protocol-v3 MCP.
- **Op84 — RELAY SOURCE CONTAMINATION + PACKAGE / APK IDENTITY RISK.** Added AgentActivity, changed launcher, versionCode 8→9, versionName to `0.5.0-mcp-shell`, built development APK.
- **Op85 — PACKAGE / APK IDENTITY RISK.** Install was not attempted because no authorized ADB device; historical YELLOW remains YELLOW.

## Source contamination

**SOURCE CHANGED: YES.**

The protected checkout is presently on the experimental branch. `socket_relay.py` is the experimental blob. New experimental files include `mcp_adapter.py`, `mcp_adapter_selftest.py`, and Android AgentActivity changes. The core `relay.py` remains baseline-identical.

## Runtime / config contamination

- **LIVE CONFIG CHANGED: UNKNOWN.**
- **RUNTIME SCRIPTS CHANGED: UNKNOWN outside source checkout.**
- **SOCKET / PORT BEHAVIOR CHANGED: SOURCE CAPABILITY YES; live execution at capture NOT PROVEN.**
- **AUTHENTICATION CHANGED: UNKNOWN live; experimental socket source adds protocol-v3 MCP while retaining authenticated loopback design.**
- **BACKGROUND SERVICES CHANGED: UNKNOWN.**
- **MATCHING LIVE RELAY PROCESS AT OP98 CAPTURE:** `NO_MATCHING_RELAY_PROCESS_OBSERVED`.

No experimental protocol request, restart, service mutation, install, rebuild, or cleanup was performed during this forensic mission.

## APK / package identity

Baseline source package identity:
- applicationId `com.monag.gpttermuxrelay`
- versionCode `8`
- versionName `0.4.0-runtime-capability`

Experimental source/APK identity:
- applicationId `com.monag.gpttermuxrelay`
- versionCode `9`
- versionName `0.5.0-mcp-shell`

Therefore **package-target identity is PROVEN SAME** and the experimental APK is not side-by-side. It targets the live Relay package name as an update/replacement candidate if signing is compatible.

Op98 installed-package query state: **NO_PACKAGE_PATH_RETURNED**.

Experimental download APK:
- path: `/storage/emulated/0/Download/GPT-Terminal-Relay-debug.apk`
- SHA256: `e0fd063b90a6fc115c8f1f0f70a6dfc9fcea15010088100ee4504e71dfa328a1`

Baseline download APK:
- path: `/storage/emulated/0/Download/GPT-Termux-Relay-0.4.0-runtime-capability-debug.apk`
- SHA256: `175f36b048de3f051bbbd583a303971e9a8ca63ee1808ba4906ceef1346b1488`

Signing comparison: **CERT_COMPARISON_UNAVAILABLE**.

The Ops 81–85 audit states install state was `NOT_ATTEMPTED` at Op85. Op98 did not perform installation or package mutation.

### Installed-package evidence excerpt

```text

```

### Relay process evidence excerpt

```text

```

### Listener evidence excerpt

```text
State       Recv-Q Send-Q Local Address:Port               Peer Address:Port              
Cannot open netlink socket: Permission denied
```

## Experimental-code contamination map

- **ORIGINAL RELAY:** `termux_relay/relay.py`; unchanged baseline/experimental blob.
- **MODIFIED RELAY:** `termux_relay/socket_relay.py`; current checkout matches experimental blob.
- **NEW EXPERIMENT CODE:** `termux_relay/mcp_adapter.py`, `mcp_adapter_selftest.py`, Android `AgentActivity.java`, MCP-aware BridgeClient changes.
- **COPIED INTO EXPERIMENT:** existing Relay execution authority, localhost transport conventions, durable IDs/dedupe, Android bridge structure.
- **SHARED-AMBIGUOUS:** runtime/service/config files not conclusively tied to a running process at Op98 capture.
- **UNKNOWN:** whether experimental MCP source ever entered normal live Relay execution outside the explicitly disposable Ops 80–81 test runtime.

## Live Relay integrity

- SOURCE CHANGED: **YES**
- LIVE CONFIG CHANGED: **UNKNOWN**
- RUNTIME SCRIPTS CHANGED: **UNKNOWN**
- INSTALLED APK CHANGED: **NOT PROVEN**
- PACKAGE IDENTITY CHANGED: **NO**; package ID stayed `com.monag.gpttermuxrelay`, while experimental versionCode increased 8→9
- SOCKET / PORT BEHAVIOR CHANGED: **SOURCE CAPABILITY YES; LIVE STATE NOT PROVEN**
- AUTHENTICATION CHANGED: **UNKNOWN live**
- BACKGROUND SERVICES CHANGED: **UNKNOWN**
- LIVE RELAY CURRENTLY RUNNING ORIGINAL CODE: **NOT PROVEN**
- EXPERIMENTAL CODE ENTERED LIVE RELAY EXECUTION: **UNKNOWN outside the disposable Ops 80–81 runtime**

## Audit / forensic discrepancies

No direct contradiction was found between the Ops 76–85 audit documents and Git-object evidence. The audits correctly describe the experimental five-commit chain and the Op85 non-install state.

The important forensic escalation is that the **current protected Relay checkout is still on the experimental branch**, which means the experiment is not merely a remote/historical branch artifact.

## Governance review

Historical REDs, rejected packets, Op80 failure, Op85 YELLOW, and Heavy Engineer 6 packet failures remain preserved. No failed operation was rewritten as successful.

This forensic mission did not fetch, switch, reset, clean, rebuild, install, restart, repair, or edit the Relay repository. ClosedCode was the only documentation mutation target.

## Proposed remediation — NOT EXECUTED

1. Preserve all current evidence and hashes.
2. In a separately authorized maintenance mission, restore the protected Relay checkout to the verified production/baseline lineage without deleting the experimental branch.
3. Move future MCP APK work to a truly side-by-side package ID instead of `com.monag.gpttermuxrelay`.
4. Verify service launchers/config hashes and package-manager state before any restart.
5. If an installed Relay package exists, compare its APK certificate/hash/version against the preserved v8 baseline before any replacement.
6. Keep the experimental branch and APKs as quarantined evidence until Director disposition.

## Final blast-radius verdict

**RED — protected Relay source is presently on the experimental branch and contains the experimental socket-relay implementation.**

The evidence does not prove package replacement or normal live execution of the experimental MCP path, so those narrower claims remain unproven rather than being inferred.
