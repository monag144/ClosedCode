# Heavy Engineer Mission — MCP-Bound Android APK Pivot

Date: 2026-09-16
Authorization window: Operations 76–100
Hard checkpoint: Operation 100

## Director authorization

Fresh authorization is granted beginning with Operation 76.

Operation 75 remains the previous completed hard checkpoint. Operations 51–52 remain historically unauthorized and must not be rewritten.

At Operation 100, complete the mandatory audit/checkpoint and STOP. No Operation 101 without fresh Director authorization.

## Phase 0 — archive the retired native-port path

Treat `CLOSEDCODE_ANDROID_PORT_ARCHIVE_DISPOSITION_2026-09-16.md` as binding.

The direct OpenCode/ClosedCode Android/Bionic native-port effort is retired.

Do not continue fixing `fff-bun`, compiling the OpenCode runtime for Android, or replacing the installed OpenCode binary.

Do not delete anything on-device as part of the archive. Preserve the fork, branch, audits, findings, and historical failures in GitHub.

## New objective

Begin implementation of a purpose-built Android APK that provides a coding-agent control surface over the already-working Termux execution environment.

The new architecture is:

Android APK UI/control plane
→ MCP-bound localhost bridge
→ Termux execution plane
→ model/provider APIs + filesystem/process/tool operations

The app is not a wrapper around an Android-compiled OpenCode runtime. Termux remains the execution engine.

## Product intent

Recreate the useful experience of an agent client without inheriting OpenCode's Android/Bionic build problems.

The APK should ultimately support:

- submitting a mission/prompt;
- selecting provider/model;
- session/history display;
- streamed model output;
- visible tool calls and tool results;
- command/process status;
- file reads/writes/edits;
- diffs and mutation review;
- approval/deny controls for sensitive mutations;
- retry/error diagnostics;
- token/latency/provider/model telemetry where available;
- clear separation between UI/control and Termux execution.

The Director will provide screenshots/reference images for the desired interface. Do not invent a final visual design before those references arrive. Build the functional shell and architecture so the UI can be shaped afterward without rewriting the execution layer.

## Reuse existing proven infrastructure

Prefer reusing the existing GPT↔Termux relay / JobScheduler / Termux execution machinery rather than creating a second competing execution engine.

MCP is an adapter/control boundary, not a replacement for the canonical Termux execution path.

Where practical, expose typed MCP-style operations such as:

- exec command;
- read file;
- write/edit file;
- process status;
- start/stop process;
- submit agent mission;
- read mission/session state;
- retrieve structured tool events;
- retrieve diff/mutation evidence.

Names are implementation details; preserve the architecture rather than blindly copying these labels.

## Phase A — architecture reconnaissance

Before mutation:

1. Locate the existing Termux relay/execution infrastructure.
2. Identify reusable execution, scheduling, persistence, and process-control components.
3. Identify any existing MCP/local-server experiments that can be reused safely.
4. Determine the narrowest localhost protocol for the APK↔Termux boundary.
5. Record the architecture and trust boundary in GitHub.

No secrets may be printed or committed.

## Phase B — local bridge

Create a small localhost-only bridge that can expose a limited typed interface to the APK.

Requirements:

- bind to localhost only unless separately authorized;
- explicit request/response schema;
- stable request IDs;
- structured success/error responses;
- bounded command execution;
- operation status and completion evidence;
- no arbitrary secret dumping;
- preserve Termux as the authority for execution;
- do not duplicate the entire relay stack if an adapter can reuse it.

Authentication can be lightweight for localhost-only development, but the boundary must be designed so stronger authentication can be added later.

## Phase C — Android APK functional shell

Build an installable development APK with a minimal functional UI.

Initial functional screens/components should be sufficient to prove:

- connection state to local bridge;
- prompt/mission input;
- submit action;
- session/output view;
- tool/command activity view;
- basic provider/model indicator or selector;
- visible errors/status.

Visual fidelity is secondary until Director screenshots arrive.

## Phase D — end-to-end proof

From the APK:

1. submit a harmless mission;
2. deliver it through the MCP/local bridge;
3. execute through the existing Termux execution machinery;
4. return streamed or incremental output to the APK;
5. perform a harmless disposable file create/read/edit/read sequence;
6. display the tool activity and final result in the APK;
7. prove exact disk contents;
8. prove no duplicate/replayed mutation occurred.

Use a disposable workspace only.

## Phase E — Nemotron path

Once the APK↔Termux control path is healthy, wire the existing working NVIDIA/Nemotron Termux path through it.

Do not re-solve NVIDIA connectivity from scratch if the existing direct Termux path is healthy.

Prove selected provider/model equals the actual route used.

No silent paid fallback or provider substitution.

## Screenshots / UI reference

Director-provided screenshots are expected during this mission or a follow-on mission.

When supplied:

- treat them as interface references;
- identify reusable interaction patterns;
- do not copy branding/assets in a way that creates unnecessary licensing/trademark problems;
- preserve our own product identity;
- adapt layout and controls around our architecture rather than reproducing incompatible internals.

## Audit and governance

Audit approximately every five operations.

Each audit must contain enough evidence to independently review:

- operations consumed;
- GREEN/YELLOW/RED status per operation;
- failures/timeouts preserved historically;
- exact mutations;
- branch/HEAD/worktree state where relevant;
- roadmap/mission review;
- governance review;
- next bounded target.

Do not merely state that an audit was appended; surface the audit evidence at checkpoints.

## Prohibited

- deleting the archived ClosedCode/OpenCode Android-port work;
- deleting or replacing installed OpenCode;
- continuing the `fff-bun` native-port rabbit hole;
- force push/reset/rebase without separate authorization;
- touching DnD-RP-Bot production state;
- exposing API keys/tokens;
- APK visual-polish rabbit holes before the functional bridge works;
- creating a second execution engine when the existing Termux machinery can be adapted.

## Operation 100 hard stop

At Operation 100:

- complete the scheduled audit;
- produce checkpoint evidence;
- report APK build/install state;
- report bridge state;
- report end-to-end mission/tool-loop state;
- report Nemotron integration state;
- report remaining blockers;
- STOP.

No Operation 101 without explicit Director approval.
