# Heavy Engineer Mini-Incident — Big Three Installation-Rule Propagation Gap — 2026-09-18

**Status:** GOVERNANCE / DOCUMENTATION PROPAGATION INCIDENT  
**Product-code incident:** No  
**Protected Relay mutation:** None

## Trigger

The Director observed that Heavy Engineer had spent multiple operations attempting to invoke APK installation through Termux/Relay despite the project now having a permanent rule that APK installation on this device is manual/Android-installer-owned because the device uses the Google Play Termux distribution.

The Director initially characterized this as a failure to read the Big Three.

## Evidence correction

Direct inspection of the current authoritative documents found:

- Heavy Engineer control harness: **installation rule absent**
- Relay recovery guide: **installation rule absent**
- ClosedCode delivery/stabilization roadmap: **installation rule absent**
- Relay Operations Log: **installation rule present**

Therefore the durable evidence does **not** support claiming that Heavy Engineer ignored an installation prohibition already present in the Big Three.

The actual governance defect is:

**the new device-specific installation prohibition was added to the Relay Operations Log but was not propagated into the Big Three that Heavy Engineer is explicitly required to re-read before every operation.**

## Why this matters

A rule that is operationally important but lives outside the mandatory per-operation governance read set can be missed even when the Heavy Engineer follows the Big Three-read instruction correctly.

This creates a false expectation that "read the Big Three" is sufficient when the controlling rule is actually elsewhere.

## Remediation

Propagate the device-specific installation prohibition into all three Big Three documents.

The rule is:

- do not attempt APK installation through Relay/Termux on this device;
- the device uses Google Play Termux and the attempted programmatic install paths are not valid/reliable for this environment;
- Relay may build, hash, verify, copy, and report an APK;
- the Director/manual Android package installer owns installation;
- after Director installation confirmation, Relay may verify version/launch/state;
- do not burn operations on alternate `pm`, `cmd package`, package-session, streamed-install, or installer-invocation tricks;
- only an explicit later Director override can authorize a Termux/Relay install attempt.

## Historical treatment

Ops265–274 occurred before this rule was propagated into the Big Three.

Do not retroactively classify those operations as governance violations under a rule that was not yet in their mandatory read set.

Future attempts after Big Three propagation are different: they would violate an explicit controlling rule unless the Director specifically overrides it.

## Reusable lesson

When the Director says a Heavy Engineer must read a named governance bundle every operation, critical new operating constraints must be inserted into that bundle or explicitly added to the mandatory read list.

Do not rely on an adjacent operations log to silently carry a rule that the mission expects the agent to know every turn.
