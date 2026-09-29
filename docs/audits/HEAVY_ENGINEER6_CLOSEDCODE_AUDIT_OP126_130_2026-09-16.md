# Heavy Engineer 6 — ClosedCode Audit Ops126–130

**Date:** 2026-09-16  
**Mission:** Clean-room ClosedCode Android rebuild / package-install vertical slice  
**Anchor:** Op125  
**Audit window:** Ops126–130  
**Canonical repo/path:** `monag144/ClosedCode` / `/data/data/com.termux/files/home/ClosedCode`  
**Branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`  
**Phone source HEAD throughout window:** `33f550555c88757b4bb13fbfbc9e940ba2a43216`  
**Phone worktree at Op130:** one untracked path: `apps/closedcode-android/build/`  
**Next audit:** Op135  
**Next twenty-operation review:** Op145  
**Next hard checkpoint:** Op150

## Operation record

### Op126 — COMMAND_FAILED / RED
Objective: finish APK packaging without installing the missing `zip` package by using the JDK `jar` tool to inject dex files, then align/sign/hash the APK.

Actual action/evidence: identity guards passed and one dex file was found, but the selected Android SDK `zipalign` was an x86_64 binary. Execution failed with `EM_X86_64 (62) instead of EM_AARCH64 (183)` before signing or shared-storage output.

Mutation: generated non-source build intermediates inside `apps/closedcode-android/build/` only; no source, package, installed-app, shared-storage APK, or Relay source mutation.

### Op127 — OK / GREEN
Objective: inventory native APK packaging paths on the phone and validate the existing unsigned APK.

Actual action/evidence: proved host `aarch64` / `arm64-v8a`; found native ARM64 `/data/data/com.termux/files/usr/bin/zipalign`, native `aapt`/`aapt2`, JDK `jar`/`keytool`, and x86_64 SDK zipaligns. SDK `apksigner` entries were shell scripts. The existing unsigned APK contained `AndroidManifest.xml`, `resources.arsc`, and `classes.dex`; `aapt2 dump badging` proved package `com.monag.closedcode.mobile`, versionCode 2, versionName `0.1.0-cleanroom`, minSdk 26, targetSdk 34, and launchable `MainActivity`.

Mutation: read-only.

### Op128 — OK / GREEN
Objective: package, align, sign, verify, and hash the clean-room APK using the native ARM64 packaging route.

Actual action/evidence: Termux ARM64 `zipalign` succeeded. SDK `apksigner` invoked through the working shell/Java environment signed the APK; verification passed using APK Signature Scheme v2 and v3. Badging again proved the expected package/launcher identity. Created `/sdcard/Download/ClosedCode-cleanroom-op128-debug.apk`, 37,629 bytes, SHA-256 `07bbd7dcdd11382ff00724b94df69349e05fab663574f8d75ae49004544896cf`; local and shared-storage hashes matched.

Mutation: generated build/signing artifacts under `apps/closedcode-android/build/`; created the clean-room APK in shared storage. No source, installed package, or Relay source mutation.

### Op129 — OK / GREEN
Objective: hand the exact verified APK to Android's package installer through the previously proven safe Termux route.

Actual action/evidence: APK hash re-verified exactly; `termux-open` launched the installer handoff. Package `com.monag.closedcode.mobile` was not installed before the handoff and remained pending user approval immediately after it.

Mutation: Android installer UI handoff only; no silent package install, no source mutation, no shared-storage mutation, no Relay source mutation.

### Op130 — OK / GREEN
Objective: audit-boundary read-only capture of installation state and source/protected-resource state.

Actual action/evidence: branch and HEAD remained exact at `33f550555c88757b4bb13fbfbc9e940ba2a43216`; worktree remained with one untracked build path only. The clean-room APK remained present, 37,629 bytes, with SHA-256 `07bbd7dcdd11382ff00724b94df69349e05fab663574f8d75ae49004544896cf` and hash match YES. `com.monag.closedcode.mobile` was still not installed, recorded as `INSTALLER_STATE=PENDING_OR_NOT_APPROVED`. Protected Relay state was not mutated; local Relay path was absent or different.

Mutation: none.

## Window mutation ledger

- **Source:** none during Ops126–130.
- **Git refs/metadata:** none on phone during this window.
- **Build output:** additional generated APK/intermediate/signing artifacts under the already-untracked `apps/closedcode-android/build/` tree.
- **Shared storage:** Op128 created `/sdcard/Download/ClosedCode-cleanroom-op128-debug.apk` with verified SHA-256 `07bbd7dcdd11382ff00724b94df69349e05fab663574f8d75ae49004544896cf`.
- **Package state:** no installation completed by Op130.
- **Runtime/UI:** Op129 opened Android's installer UI; user approval remained pending or had not completed by Op130.
- **GPT-Termux-Relay protected infrastructure:** no source/config/package mutation.

## Preserved failures

- Op126 remains **COMMAND_FAILED / RED** due Android SDK build-tools architecture mismatch (`zipalign` x86_64 on ARM64 host). Later successful native packaging does not rewrite Op126.
- Earlier historical RED/TIMEOUT/PACKET_REJECTED/YELLOW statuses from prior windows remain preserved unchanged.

## Current blocker

The clean-room APK is successfully built, signed, hash-verified, and present in shared storage, but Android installation has not yet completed because the installer requires user approval. Once approved, next work is to prove installed package/version/launcher state, launch the app, connect to the real local ClosedCode/OpenCode backend, prove session/provider/event streaming plus at least one real file/tool operation, and continue toward the full provenance gate.

## Protected-state and governance status

Mission remains on the Director-authorized clean-room ClosedCode path. No Relay implementation or protected Relay source was used as scaffolding or mutated. Audit 126–130 is complete. Governance is restored for substantive Op131 work once the installer approval state is resolved.
