# HE8 Operation Resilience — Op217

Status: RED / PACKET_REJECTED
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP217.classify-nvidia-503-basic-vs-session
Relay status: PACKET_REJECTED
Exit code: null
Failure: command_b64 is not valid base64

Intended purpose:
Compare a plain NVIDIA passthrough request against an otherwise identical session-aware request and sanitize/classify any upstream 503 metadata.

Actual result:
The Relay rejected the packet before execution.

Mutation:
- no shell command executed
- no provider request
- no sidecar process started
- no history files created
- no source/Git mutation
- no APK mutation
- no live OpenCode runtime replacement
- no GPT-Termux-Relay mutation

Disposition:
Preserve Op217 as RED. Retry only under fresh Op218 with a smaller verified Base64 packet.
