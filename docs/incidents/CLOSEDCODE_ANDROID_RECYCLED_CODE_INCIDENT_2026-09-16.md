# INCIDENT REPORT — ClosedCode Android APK built with recycled GPT-Termux-Relay code

**Date:** 2026-09-16  
**Status:** RED  
**Repository:** `monag144/ClosedCode`  
**Branch:** `closedcode/mcp-apk-implementation-20260916`  
**Affected project:** `closedcode_agent_android/`  
**Affected APK:** `com.monag.closedcode.agent` v`0.1.0-dev`

## Incident summary

The first ClosedCode Android APK was built with an overwhelming amount of recycled Android scaffolding and implementation patterns from the pre-existing `GPT-Termux-Relay` Android application instead of being implemented as a clean-room ClosedCode client matching the intended OpenCode-style mobile product.

The APK was not a byte-for-byte copy of the entire Relay application and did not include Relay's accessibility-service implementation, diagnostic HUD, packet extractor, recovery classes, Relay package identity, or Relay-specific Android service declarations. However, provenance review established that multiple parts of the new ClosedCode Android project were copied or adapted from Relay, including project/build scaffolding, the Termux build script architecture, localhost socket-client structure, and substantial MainActivity configuration/UI patterns.

This violated the intended separation between protected GPT-Termux-Relay infrastructure and the new ClosedCode product. The incident is therefore recorded as a provenance and implementation-boundary failure, not merely a visual-design miss.

## Trigger

The Director reviewed the installed ClosedCode APK and observed that its UI did not resemble the supplied OpenCode mobile design target. The APK instead presented a simple pairing/configuration form visually and structurally reminiscent of the Relay application. The Director requested an explicit audit to determine whether Relay code had been recycled into ClosedCode.

## Audit findings

### Confirmed recycled/adapted material

1. **Root Android `build.gradle`**
   - ClosedCode and Relay use a byte-for-byte identical file.
   - Both resolve to Git blob SHA `5b7ccba7c566afb5057eaea1b10b99b083851fe4`.

2. **Android project scaffolding**
   - `settings.gradle` and `app/build.gradle` use the same project structure and Gradle conventions as Relay with ClosedCode-specific names/package identity substituted.

3. **Termux build workflow**
   - `closedcode_agent_android/build_termux.sh` materially follows Relay's build script architecture.
   - Shared elements include Gradle 8.9, the same Gradle distribution SHA256, Python-based Gradle download/extraction, Android SDK 34 checks, Termux `aapt2` override, debug APK build flow, hashing, and shared-storage copy behavior.
   - ClosedCode added safer non-overwrite behavior and ClosedCode-specific output paths, but the workflow is still clearly derived from Relay.

4. **`BridgeClient.java` transport implementation**
   - Uses the same basic Relay transport architecture: Java socket to `127.0.0.1`, JSON line protocol, buffered reader/writer, 3000 ms connect timeout, long read timeout, request/response validation, and a class named `BridgeClient`.
   - ClosedCode changed request schema and operations, but the implementation scaffold was adapted from Relay.

5. **`MainActivity.java` implementation patterns**
   - Reuses the Relay-style programmatic Android UI approach using `LinearLayout` and stock widgets.
   - Reuses pairing-token and numeric-port configuration patterns, SharedPreferences storage, 32-character token validation, 1024–65535 port validation, and Toast-based validation feedback.
   - The resulting UI was a renamed/reworked engineering control form rather than the intended OpenCode-style application.

## Material that was NOT copied into ClosedCode

The audit did not find the following Relay components inside `closedcode_agent_android/`:

- package tree `com.monag.gpttermuxrelay`;
- `RelayAccessibilityService`;
- `RelayDiagnosticAccessibilityService`;
- `RelayDiagnosticHud`;
- `PacketExtractor`;
- `PacketObservation`;
- `RelayRuntimeConfig`;
- `TermuxRecovery`;
- Relay accessibility-service XML resources;
- `com.termux.permission.RUN_COMMAND` in the ClosedCode manifest;
- Relay package application ID;
- an Android source dependency importing the Relay repository.

The ClosedCode APK therefore was **not the Relay APK copied wholesale**, but it was also **not a clean-room implementation**.

## Impact

- The first ClosedCode APK failed the product-design objective.
- The visual and interaction model diverged substantially from the OpenCode mobile reference supplied by the Director.
- The protected-infrastructure boundary was weakened because Relay implementation choices were used as the starting template for a supposedly independent product.
- Claims that the project was "intentionally separate" from Relay were incomplete: package/runtime separation existed, but source provenance was not clean.
- Continued development on top of the current Android scaffold risks carrying Relay assumptions, architecture, and UI patterns deeper into ClosedCode.

## Root cause

The implementation optimized for quickly proving an Android-to-localhost-to-Termux control path and reused known-working Relay Android patterns to reduce build and runtime uncertainty. That engineering shortcut was incompatible with the requirement for a distinct ClosedCode application and with the intended OpenCode-style UI/UX.

A secondary failure was treating absence of Relay package identity/services as sufficient proof of separation. Package isolation is not the same as source/provenance isolation.

## Required corrective direction

No remediation is authorized by this incident report itself. The report records the defect and preserves evidence.

Any later remediation should begin from the following principles:

- treat the current ClosedCode Android UI/scaffold as contaminated by recycled Relay implementation patterns;
- do not use GPT-Termux-Relay source as a template for the replacement client;
- define the OpenCode screenshots supplied by the Director as the primary visual/interaction reference;
- build a clean-room ClosedCode Android architecture and UI;
- retain only ClosedCode-specific protocol requirements that are independently specified;
- perform a provenance audit before accepting a replacement APK;
- verify no Relay source files, Relay package identifiers, Relay service classes, or substantial copied implementation blocks remain.

## Historical preservation

This incident does not rewrite earlier build/install operations. The APK successfully built and installed as recorded. The defect is that the resulting application was implemented with excessive recycled Relay code and the wrong UI/product architecture.

The earlier provenance audit remains supporting evidence:

`docs/closedcode/CLOSEDCODE_ANDROID_RELAY_PROVENANCE_AUDIT_2026-09-16.md`

## Incident conclusion

**RED.** The first ClosedCode Android APK was not an acceptable clean-room ClosedCode client. Although it did not contain the full Relay application, an overwhelming amount of its Android foundation was recycled or adapted from GPT-Termux-Relay. This must remain recorded as an implementation/provenance incident before further APK development proceeds.
