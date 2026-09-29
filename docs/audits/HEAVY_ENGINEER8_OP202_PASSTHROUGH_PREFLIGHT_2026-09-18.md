# HE8 Op202 Passthrough Preflight

Date: 2026-09-18 UTC
Operation consumed by this GitHub callback: none
Checkpoint state: Op200 checkpoint explicitly released by Director
Next Relay operation: Op202

Mandatory reads completed this turn:
1. GPT-Termux Relay Recovery Guide
2. Heavy Engineer Baseline Control Harness
3. ClosedCode Delivery and Stabilization Roadmap

Director mission:
Implement a ClosedCode-owned passthrough mode for NVIDIA and GLM, prioritizing solution/integration over further deep reverse engineering of OpenCode's compiled LayerNode graph. Target officially usable passthrough by Op225.

Source findings:
- Android localhost networking is centralized in apps/closedcode-android/.../ClosedCodeApi.java.
- MainActivity.dispatchPrompt() is the single prompt-send choke point.
- MainActivity.loadMessages() is the message-render refresh path.
- MainActivity.startEventStream() is the live-update/reconnect choke point.
- MainActivity.abortPrompt() is isolated.
- ComposerUiController already owns provider/model/agent/variant selection and persistence.
- OpenCode auth data is backend-owned in Global.Path.data/auth.json; API auth records contain provider-keyed keys and are written mode 0600.
- Therefore passthrough can keep provider secrets in Termux and expose only a loopback ClosedCode protocol to Android.
- Existing OpenCode service remains useful for sessions/files/diffs and other working surfaces; passthrough can be introduced narrowly for NVIDIA/GLM prompt execution.

Planned Op202:
Create the minimal loopback-only Termux passthrough sidecar foundation using Python standard library, read provider credentials from the existing backend-owned auth store without exposing them, support NVIDIA/Z.AI OpenAI-compatible chat-completion proxying with streaming transport, add health/capability introspection without secrets, self-test locally, commit/push. Do not modify GPT-Termux-Relay.
