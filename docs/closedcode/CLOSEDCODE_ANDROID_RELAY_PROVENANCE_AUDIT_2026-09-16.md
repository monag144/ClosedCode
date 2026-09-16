# ClosedCode Android / GPT-Termux-Relay provenance audit — 2026-09-16

**Status:** RED — ClosedCode Android is not a wholesale copy of GPT-Termux-Relay, but it is not clean-room. Multiple Android scaffold/transport/build files were clearly copied or adapted from Relay-era code and must be replaced before treating the APK as provenance-clean.

**Audited branch:** `closedcode/mcp-apk-implementation-20260916`

**ClosedCode branch head at audit start:** `b9a1e3a49c2a882907c59a77b4bddf5976ea76d6`

**Relay comparison branch:** `development/runtime-control`

**Relay comparison head:** `b7889be0490a48e1ce0b5bc4ad246547986633e0`

## What is NOT copied wholesale

The ClosedCode Android source tree contains only:

- `MainActivity.java`
- `BridgeClient.java`
- one manifest
- one strings resource
- Gradle/build scaffolding

It does **not** contain the Relay Android source tree or the Relay-only components seen in `android_relay`, including:

- `RelayAccessibilityService`
- `RelayDiagnosticAccessibilityService`
- `RelayDiagnosticHud`
- `RelayRuntimeConfig`
- `TermuxRecovery`
- `PacketExtractor`
- `PacketObservation`
- Relay accessibility XML resources
- package path `com/monag/gpttermuxrelay`

The ClosedCode manifest does not declare `com.termux.permission.RUN_COMMAND`, Relay accessibility services, or Relay package queries. The ClosedCode application ID is `com.monag.closedcode.agent`, not `com.monag.gpttermuxrelay`.

## Provenance contamination found

### 1. Exact file reuse

`closedcode_agent_android/build.gradle` is byte-for-byte identical to `GPT-Termux-Relay/android_relay/build.gradle`.

Both have Git blob SHA:

`5b7ccba7c566afb5057eaea1b10b99b083851fe4`

This is direct source reuse, not merely similar Android boilerplate.

### 2. `settings.gradle` is clearly adapted from Relay

The repository/plugin-management block is the same structure and ordering as Relay. The ClosedCode version primarily changes the project name and include syntax.

### 3. `app/build.gradle` is clearly adapted from Relay

The Android application structure, SDK levels, release block, and Java 17 compile-options layout mirror the Relay application Gradle file. ClosedCode changes namespace/application ID/versioning and removes Relay-specific `buildConfig` enablement.

### 4. `build_termux.sh` is strongly derived from Relay

The ClosedCode build script preserves the Relay build script's distinctive structure:

- Gradle 8.9
- the exact Gradle distribution SHA256
- isolated tool-root / Gradle ZIP / Gradle home pattern
- the same Python `urllib.request` Gradle downloader shape
- the same Python `zipfile` extraction shape
- SDK 34 check
- Termux `aapt2` override
- Gradle debug build
- APK existence/hash/copy flow

ClosedCode adds safer no-overwrite behavior and ClosedCode-specific paths, but provenance is still Relay-derived.

### 5. `BridgeClient.java` contains substantial Relay-derived transport scaffolding

Both clients use the same class name and substantially the same transport implementation shape:

- `JSONObject` request/response framing
- identical Java I/O/network import family
- `CONNECT_TIMEOUT_MS = 3000`
- long read timeout around 310000 ms
- loopback `127.0.0.1`
- `Socket`
- `BufferedWriter` / `OutputStreamWriter`
- newline-delimited JSON request
- `BufferedReader` / `InputStreamReader`
- single-line JSON response
- `ok` boolean response validation

ClosedCode has a different request protocol (`closedcode.bridge.v1`, `system.ping`, `mission.submit`) and different error strings, but the transport implementation was plainly adapted rather than independently designed.

### 6. `MainActivity.java` contains Relay-derived UI/settings scaffolding

The ClosedCode UI is not the Relay UI in full, but it carries recognizable Relay patterns:

- programmatic Android `Activity` UI rather than a distinct app architecture
- `SharedPreferences` token/port pairing
- password token field
- numeric localhost port field
- token minimum-length validation at 32 characters
- port range validation 1024..65535
- save-to-SharedPreferences flow
- Toast-based validation/status feedback
- programmatic `LinearLayout`/`TextView`/`EditText`/`Button` composition

ClosedCode adds provider/model/mission/session controls and removes Relay automation/accessibility controls, but this is still adapted scaffolding.

## Documentation finding

`closedcode_agent_android/README.md` says the project has "No source dependency on the Relay repository." That is true in the narrow build/dependency sense, but it is insufficient as a provenance statement because source/scaffold reuse exists. Until the contaminated Android files are replaced, the README must not be interpreted as meaning clean-room independence.

## UI finding

The installed APK is also visually wrong for the intended product. It is a simple light-theme engineering shell. The Director-provided OpenCode references establish the intended mobile language:

- dark interface
- persistent bottom navigation: Sessions / Connections / Settings
- connection/server cards and health state
- grouped workspace/session browsing
- chat/session screen with model/provider chips
- permission/question/error/connection settings
- compact mobile hierarchy rather than exposing raw pairing/debug controls as the main screen

## Required remediation

Treat the current `closedcode_agent_android` implementation as a disposable prototype only.

Before the next APK is considered acceptable:

1. Replace the Relay-derived Android files with a clean-room ClosedCode mobile implementation.
2. Do not copy or adapt Relay Android source, classes, build script, or UI implementation.
3. Use the Director-provided OpenCode screenshots and ClosedCode's own product requirements as the design source.
4. Preserve package identity `com.monag.closedcode.agent`.
5. Preserve the protection boundary: no Relay accessibility service, no `RUN_COMMAND`, no Relay package identity, no Relay update/install logic.
6. Re-audit the new Android subtree against `GPT-Termux-Relay/android_relay` before building/installing the replacement APK.
7. Historical/audit documents may continue to mention Relay; the prohibition concerns Relay application source/runtime code inside the ClosedCode product implementation.

## Verdict

**Not a wholesale Relay copy:** confirmed.

**Clean-room / no pre-existing Relay app code:** **not confirmed; currently false.**

The current Android implementation must be replaced before that assurance can honestly be given.
