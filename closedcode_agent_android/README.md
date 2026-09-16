# ClosedCode Agent Android

Purpose-built Android control surface for the ClosedCode MCP/Termux architecture.

## Protection boundary

This project is intentionally separate from `GPT-Termux-Relay`.

- Android package: `com.monag.closedcode.agent`
- No Relay accessibility services
- No `com.termux.permission.RUN_COMMAND`
- No install/update logic targeting the Relay package
- No source dependency on the Relay repository
- Network client targets a separate ClosedCode-owned localhost bridge protocol

## Build

From Termux:

```sh
cd closedcode_agent_android
./build_termux.sh
```

The build script uses Android SDK 34 and a Termux-compatible `aapt2`, builds a debug APK without installing it, and copies the result to unique timestamped output paths so existing APKs are not overwritten.

## Current functional shell

The development APK provides:

- localhost bridge connection state;
- pairing token + port settings;
- provider/model fields;
- mission/prompt input;
- submit action;
- session output;
- command/tool activity log;
- visible request IDs and latency.

The localhost bridge itself is intentionally not bundled into this APK. It will live in ClosedCode/Termux as a separate execution-plane component.