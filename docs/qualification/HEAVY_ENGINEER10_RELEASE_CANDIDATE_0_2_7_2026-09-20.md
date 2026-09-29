# Heavy Engineer 10 — ClosedCode 0.2.7 Release Candidate Certificate

Date: 2026-09-20

## Certified source

- Product implementation commit: `0d575ec144638a534019b16811d8990599668626`
- Certification/documentation base before this certificate: `654620c46986f35b2cb9343dd5ef1a442a993107`
- Android-facing OpenCode service: **1.18.31 GREEN on 4096**
- ClosedCode passthrough/agent backend: **0.8.15 GREEN on 4097**

## Agent/provider acceptance

- NVIDIA real coding-agent acceptance: **GREEN at Op442**.
  - ClosedCode inspected a failing disposable coding task, modified its implementation through workspace tools, executed tests, and independently re-ran all five tests GREEN.
  - 7 completed tool actions across 6 provider rounds.
  - Exact token usage: 19,458 prompt + 1,569 completion = 21,027 total.
- ZAI cross-provider acceptance: **GREEN at Op453** using `glm-4.7-flash`.
  - Terminal marker: `ZAI_CROSS_PROVIDER_GREEN`.
  - Exact token usage: 1,201 prompt + 42 completion = 1,243 total, 1/1 reported/provider rounds.
- OpenCode provider catalog acceptance at Op453: **GREEN**.
  - HTTP 200.
  - 222 providers, 3 connected providers.
  - NVIDIA connected with 103 models.
  - ZAI connected with 17 models.
  - Full catalog size: 6,104,423 bytes.
  - Full catalog transfer time: 0.415067 seconds.

## Android acceptance

- Transcript regression checker: **GREEN**.
- Integrated UI regression checker: **GREEN**.
- Termux Android build: **GREEN**.
- RC APK: `/sdcard/Download/ClosedCode-RC-0.2.7-op454.apk`
- RC APK bytes: **111957**
- RC SHA-256: `aac5b6a6ff4d8d66622d37901bafbd1dcd3396db0629d6f1b0b78a4c32b0e4fd`
- SHA-256 file: `/sdcard/Download/ClosedCode-RC-0.2.7-op454.apk.sha256`
- APK installation: **NOT PERFORMED**. Installation remains Director-controlled.

## Remaining manual observation

Automated certification covers source integrity, backend/provider connectivity, real agent execution, persistence/regression checks, and Android build integrity. Device-visible completion sound/notification behavior still requires observation after the Director manually installs the RC; this workflow intentionally does not install APKs.
