# GPT-Termux-Relay Protection Incident — Operations 76–85

Date: 2026-09-16
Project: ClosedCode MCP/APK pivot

## Director ruling

GPT-Termux-Relay is protected infrastructure.

Effective immediately:

- No edits to GPT-Termux-Relay source, branches, configs, state, auth, socket behavior, background services, or Android relay app.
- No installing the new coding-agent APK over anything relay-related.
- No cleanup/revert inside GPT-Termux-Relay unless the Director explicitly authorizes it later.
- Future coding-agent APK work must live in a completely separate project/repository/app identity.
- The relay remains isolated and protected.

## What happened

During Operations 76–85, Heavy Engineer used a separate mission branch inside GPT-Termux-Relay as the development home for MCP/APK work. The live relay runtime/config was not replaced, but development still touched the relay codebase.

At Operation 85, a debug APK was built and copied to `/sdcard/Download/GPT-Terminal-Relay-debug.apk`. Heavy Engineer proposed installing it and, if Android treated it as an update, installing it over the existing app. That is explicitly not authorized under the Director’s protection ruling.

Operation 86 is not authorized.

## Governance assessment

The original Operation 76 mission instructed Heavy Engineer to inspect existing Termux execution/relay infrastructure and identify reusable command execution, process control, mission/job scheduling, persistence/session handling, and localhost/MCP experiments. It did not explicitly state that GPT-Termux-Relay itself was a protected no-touch dependency.

Therefore, the boundary was underspecified at mission start. The relay protection rule must now be treated as an explicit hard constraint for all future work.

## Historical preservation

Do not rewrite Operations 76–85 as if this boundary had been explicit from the start. Preserve the historical record exactly as it occurred.

Any future continuation must begin from a separate repository/app identity and must not modify or overwrite GPT-Termux-Relay.
