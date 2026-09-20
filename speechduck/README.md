# Speech Duck

Android utility that lowers the shared media stream while speech-to-text recording is active, then restores the previous volume.

## Privacy
- Does not record audio.
- Does not use Accessibility Service.
- Does not read dictated text.
- Uses Android's anonymized active recording-configuration callback.

## Detection
Default mode ducks only recordings reported as `MediaRecorder.AudioSource.VOICE_RECOGNITION`.
Compatibility mode ducks for any active microphone recording, for keyboards/devices that do not classify dictation as `VOICE_RECOGNITION`.

## Permissions
- `MODIFY_AUDIO_SETTINGS`: adjust media volume.
- `FOREGROUND_SERVICE` / `FOREGROUND_SERVICE_SPECIAL_USE`: remain active while monitoring.
- `POST_NOTIFICATIONS`: show foreground-service notification on Android 13+.
- `RECEIVE_BOOT_COMPLETED`: restart monitoring after reboot if the user left it enabled.

## Build
This source is intentionally dependency-free and can be built with standard Android SDK platform/build tools.
