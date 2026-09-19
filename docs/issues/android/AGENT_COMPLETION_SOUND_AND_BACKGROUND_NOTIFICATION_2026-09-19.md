# Android Feature Request — Agent Completion Sound + Background Notification — 2026-09-19

**Status:** OPEN PRODUCT REQUEST  
**Surface:** ClosedCode Android client  
**Requested by:** Director

## Product intent

When a ClosedCode agent operation finishes, the app should give the user an unmistakable completion cue.

Two behaviors are required:

### 1. Foreground completion sound

When the user is actively in ClosedCode and an agent run reaches a terminal completed state, play a short completion chime/chirp.

The sound should:

- be brief;
- be recognizably "done";
- not resemble an error/alarm;
- not loop;
- not require bundling a custom audio asset if Android already exposes an appropriate system sound;
- respect the device's sound/notification policy.

Preferred implementation direction:

- use Android's system ringtone/notification sound infrastructure;
- default to a short system notification/completion tone;
- allow the user to choose a different available system tone from Settings where practical;
- if a "Ta-da" style tone exists on the device, it may be selected through the system sound picker, but do not assume a specific named sound exists on every Android/OEM build.

### 2. Background notification

If the app is not foreground/visible when the agent finishes, post a standard Android notification to the notification tray.

The notification should include enough context to identify the completed task, for example:

- app name: ClosedCode;
- completion state;
- session/thread title when available;
- provider/model when useful;
- short final status/summary when available.

Tapping the notification should return the user to the relevant ClosedCode session/thread.

A completion notification should use the normal Android notification channel and may use the same completion sound, subject to the user's system notification settings.

## Settings

Put these controls in Settings rather than the main coding UI.

Suggested location:

`Settings → Notifications`

Suggested controls:

- `Agent completion sound` — on/off
- `Completion sound` — choose from available Android system tones where supported
- `Background completion notifications` — on/off

The notification channel must remain user-configurable through normal Android notification settings.

## State semantics

Do not emit the success chime for every tool event.

Emit it only when the overall agent run reaches a terminal completion state.

Different terminal conditions should be distinguishable:

- successful completion → completion chime / normal notification;
- cancelled by user → no success chime; optional quiet cancellation notification only if useful;
- provider/tool failure → do not play the success chime; use an error/failure notification behavior if implemented;
- permission wait / steering wait / intermediate tool completion → no completion chime.

Avoid duplicate alerts if Android lifecycle callbacks or session reloads observe the same completed run more than once.

## Foreground/background behavior

Preferred UX:

- app foreground at completion → play completion sound, no redundant tray notification required by default;
- app background/not visible at completion → post Android notification with completion sound;
- if Android/OEM lifecycle visibility is ambiguous, prefer one deduplicated completion alert rather than both repeatedly.

## Android implementation notes

Use standard Android APIs rather than custom background polling where possible:

- `NotificationChannel` / `NotificationManager` for background completion notifications;
- Android system/default notification sound URI or a user-selected system sound;
- `RingtoneManager` / platform sound picker where appropriate;
- a PendingIntent/deep-link back to the relevant ClosedCode session.

The implementation must respect modern Android notification-permission requirements where applicable.

## Acceptance conditions

### Foreground

1. Start an agent operation.
2. Keep ClosedCode visible.
3. Let the operation complete successfully.
4. Exactly one short completion chime plays.
5. Tool-card completions do not trigger the chime.

### Background

1. Start an agent operation.
2. Leave ClosedCode before completion.
3. Let the operation complete successfully.
4. A single ClosedCode completion notification appears in the Android notification tray.
5. The notification uses the configured completion sound unless system settings silence it.
6. Tapping the notification returns to the correct ClosedCode session.
7. Returning to the app must not produce a duplicate completion alert.

### Failure/cancel

1. Cancel one run and force one provider/tool failure.
2. Neither case may emit the normal success-completion chime.
