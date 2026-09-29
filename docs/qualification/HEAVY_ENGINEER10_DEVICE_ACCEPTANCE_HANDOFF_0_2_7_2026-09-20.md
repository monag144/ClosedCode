# ClosedCode 0.2.7 — Director Device-Acceptance Handoff

Prepared UTC: `2026-09-20T22:18:31Z`

## Artifact to install manually

- APK: `/sdcard/Download/ClosedCode-RC-0.2.7-op454.apk`
- Bytes: **111957**
- SHA-256: `aac5b6a6ff4d8d66622d37901bafbd1dcd3396db0629d6f1b0b78a4c32b0e4fd`
- SHA file: `/sdcard/Download/ClosedCode-RC-0.2.7-op454.apk.sha256`
- Certified product source: `0d575ec144638a534019b16811d8990599668626`
- RC certificate commit: `ab1d9e6188a16685071812416f0edeca6faf65e8`
- APK installation by Heavy Engineer: **NOT PERFORMED**

## Automated acceptance already complete

- OpenCode Android-facing service 4096: **GREEN**, version 1.18.31.
- ClosedCode backend 4097: **GREEN**, version 0.8.15.
- NVIDIA provider: **connected**.
- ZAI provider: **connected**.
- NVIDIA real coding-agent mutation/test acceptance: **GREEN**.
- ZAI `glm-4.7-flash` cross-provider acceptance: **GREEN**.
- Transcript regression: **GREEN**.
- Integrated UI regression: **GREEN**.
- Android Termux build and artifact hash verification: **GREEN**.

## Director manual device test

After manually installing the APK above:

1. Launch ClosedCode and confirm the connection UI reaches **connected/active** rather than remaining offline.
2. Open the model/provider picker. Confirm providers/models load normally and a connected model can be selected; `ZAI / glm-4.7-flash` is the already-certified cross-provider reference.
3. Send a simple prompt and verify the user message remains visible while the request runs and the assistant final appears in correct chronological order.
4. Run a small coding/tool task in a disposable workspace. Confirm human-readable tool/progress entries appear, technical evidence remains available, and the final response follows the tool activity rather than appearing ahead of it.
5. Leave and reopen the conversation/app. Confirm the user message, assistant final, and tool timeline persist without duplicate bubbles or reordered activity.
6. With ClosedCode in the **foreground**, complete a successful request and confirm the configured completion sound is actually audible on-device.
7. Grant Android notification permission if prompted. Put ClosedCode in the **background**, complete a successful request, and confirm the completion notification appears in the Android notification tray.
8. Confirm failed/cancelled work does not masquerade as a successful completion notification.

## Acceptance rule

If steps 1–8 pass, device acceptance for this RC is GREEN. If any step fails, report the exact step plus what was observed; preserve this RC and its hash unchanged so the defect can be reproduced against the certified artifact.

## Runtime note

Multiple OpenCode `serve` processes may be visible from prior qualification work. This handoff does **not** terminate them because process ownership must remain evidence-based. The release-critical proof is endpoint behavior: 4096 and 4097 are healthy at handoff time.
