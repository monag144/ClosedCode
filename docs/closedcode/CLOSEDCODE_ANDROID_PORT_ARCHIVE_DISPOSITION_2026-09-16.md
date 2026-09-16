# ClosedCode Android Native Port — Archive Disposition

Date: 2026-09-16
Status: ARCHIVED / DO NOT CONTINUE

## Director ruling

The direct OpenCode/ClosedCode Android/Bionic native-port effort is discontinued.

"Scrap" means archive, preserve, and document the work in GitHub. It does **not** mean delete the repository, branch, audit history, source, or anything on-device.

No device cleanup, package removal, binary deletion, worktree deletion, or OpenCode mutation is authorized by this disposition.

## Why this path is being retired

The mission established that the upstream OpenCode codebase does not currently provide an official Android/Termux build. The Android/Bionic port therefore became a platform-porting effort rather than a simple provider integration.

Heavy Engineer Ops 53–75 further isolated an immediate Android build blocker at `@ff-labs/fff-bun@0.9.4`, whose package metadata excludes Android. The build had not yet produced a usable ClosedCode binary, and NVIDIA/GLM provider qualification, tool-loop qualification, installation, and APK work had not been reached.

The Director has chosen not to spend additional engineering time forcing the upstream OpenCode runtime onto Android/Bionic.

## Preserved evidence

Preserve without rewriting:

- all Ops 53–75 audit history;
- historical REDs and timeouts;
- the unauthorized status of Ops 51–52;
- the Android `splitting:false` build-helper work;
- the `fff-bun` incompatibility findings;
- all previous OpenCode/Bun A/B evidence;
- the existing ClosedCode fork and engineering branch;
- the fact that installed OpenCode remained protected during the mission.

The archived branch remains useful as a forensic/reference source only unless the Director explicitly reopens native-port work.

## New product direction

The new direction is an Android APK that acts as a control/interface layer over the already-working Termux execution environment rather than embedding or recompiling the full OpenCode runtime.

Target architecture:

Android APK UI / control plane
→ MCP-bound local bridge
→ Termux execution plane
→ model/provider APIs and local filesystem/tools

The APK should expose the useful coding-agent experience while Termux continues to perform command execution, file operations, process control, and model/tool orchestration.

## Scope boundary

Archived native-port work must not silently resume.

No further `fff-bun`, Bun compile, OpenCode Android binary, or direct ClosedCode native-port engineering is authorized unless the Director explicitly reopens that path.
