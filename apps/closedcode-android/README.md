# ClosedCode Android — clean-room mobile client

This directory is the independent Android client for ClosedCode. It is intentionally built with Android platform APIs only and does not depend on GPT-Termux-Relay source, package structure, activities, socket clients, manifests, build scripts, configuration UI, or runtime assumptions.

The first vertical slice targets the native ClosedCode/OpenCode HTTP control surface on localhost:

- `GET /global/health`
- `GET/POST /session`
- `GET /session/:id/message`
- `POST /session/:id/prompt_async`
- `GET /event` (SSE)
- `GET /provider`
- `GET /file`, `GET /file/content`
- `GET /session/:id/diff`

The mobile UI follows the Director-supplied OpenCode mobile screenshots: Sessions, Connections, Settings, and a dark session/chat workspace with model/tool status, file browsing, diffs, and a composer.

Build on Termux with:

```sh
cd apps/closedcode-android
./build-termux.sh
```

The script discovers the local Android SDK/build-tools and produces `/sdcard/Download/ClosedCode-cleanroom-debug.apk`.
