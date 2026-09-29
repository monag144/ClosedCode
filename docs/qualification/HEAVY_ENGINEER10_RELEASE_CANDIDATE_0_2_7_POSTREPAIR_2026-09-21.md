# Heavy Engineer 10 — ClosedCode 0.2.7 Post-Repair Release Candidate

Timestamp UTC: `2026-09-21T03:28:31Z`

## Candidate identity

- RC file: `/sdcard/Download/ClosedCode-RC-0.2.7-postrepair-op466.apk`
- Bytes: **124856**
- SHA-256: `090c13240c5b80e3677907e14e4e6e956558a2b430da5d580bc050bcdf2b946e`
- SHA file: `/sdcard/Download/ClosedCode-RC-0.2.7-postrepair-op466.apk.sha256`
- Android package: `com.monag.closedcode.mobile`
- Version name: `0.2.7-cleanroom`
- Last product-code commit: `9dfaad6258fb004327172055567e3055577686e0`
- Mandatory integrated audit commit immediately before packaging: `665e9a0f768916431f319ea65c6b163cbf35327e`
- Historical Op454 RC remains preserved and is superseded only for further device testing, not erased from provenance.

## Audited runtime state

- OpenCode service 4096: `{"healthy":true,"version":"1.18.31"}`
- ClosedCode passthrough 4097: `{"healthy":true,"service":"closedcode-passthrough","version":"0.8.16","bind":"loopback-only","providers":{"nvidia":true,"zai":true}}`
- NVIDIA provider: **connected**
- ZAI provider: **connected**

## Repairs included since the original device-test RC

1. Agent permissions now support **Allow once**, **Approve all for this task**, and persistent **Always allow this exact action**.
2. Permission replies report expiration truthfully and the backend wait window is 600 seconds.
3. Completion sound has **mute/unmute**, **Choose**, and **Test** controls in Settings.
4. Background completion notifications use unique per-request IDs instead of overwriting same-session notifications.
5. Agent errors have a dedicated notification channel and do not masquerade as successful completion.
6. Settings now expose **Dark**, **Light**, and **Chocolate Mint** themes with persisted selection.
7. Session Context/shared sheet handles are functional: drag up expands, drag down dismisses, short drag snaps back.
8. Prior conversation chronology, tool timeline, and persistence repairs remain in the candidate.

## Automated qualification inherited from Op465

- Permission-policy regression: **GREEN**
- Completion sound/notification regression: **GREEN**
- Theme regression: **GREEN**
- Sheet-drag regression: **GREEN**
- Transcript regression: **GREEN**
- Integrated UI regression: **GREEN**
- Termux Android build: **GREEN**
- Exact APK bytes/hash reverified during packaging: **GREEN**
- `FoxyApp/` disposable live-agent fixture preserved unchanged; tree SHA-256 `386c69ceb5a2c893bb4273f2567e75c4189e3d98af0fd03a2c6a2927f54c3b3c`.

## Required Director device retest

Install this exact RC manually. Verify:

1. connection and provider/model picker remain healthy;
2. normal conversation ordering remains correct;
3. run a coding task and exercise **Allow once**, then another permission with **Approve all for this task**;
4. optionally exercise **Always allow this exact action**, then confirm the same exact action auto-approves later while a materially different action still asks;
5. use Settings → Completion sound → **Test**, then verify mute/unmute and Choose;
6. keep the app foregrounded and verify successful completion chime when enabled;
7. background the app and verify multiple successful tasks can each produce completion notifications rather than one replacing all later ones;
8. produce a disposable failure and verify an **error** notification appears and no success notification is falsely emitted for that run;
9. switch among **Dark / Light / Chocolate Mint**, including leaving and reopening the app, and confirm selection persists;
10. open Session Context and verify drag-up expand, short-drag snap-back, and drag-down full dismissal;
11. cold-close/relaunch the app and reopen the prior conversation to verify user message, assistant final, and tool timeline persist in order without duplication.

Device acceptance remains unclaimed until those observations are supplied by the Director.
