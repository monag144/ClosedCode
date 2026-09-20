# ClosedCode Delivery and Stabilization Roadmap — 2026-09-17

**Timestamp:** 2026-09-17

## Objective Checklist — 2026-09-20

This checklist supplements the historical operation-range sections below. The historical ranges remain provenance; this checklist is the compact product-objective view for later Heavy Engineer reviews.

Legend:

- `[x]` — implemented and supported by durable evidence.
- `[~]` — implemented in substantial part; one or more explicit acceptance gates remain.
- `[ ]` — not yet accepted.
- `[-]` — optional/deferred and not a release blocker unless separately promoted by the Director.

### Core objectives

- [x] ClosedCode Android APK communicates with a localhost ClosedCode backend/control layer in Termux.
- [x] ClosedCode owns the provider compatibility boundary; OpenCode is optional compatibility/reference infrastructure rather than mandatory transit for every provider.
- [x] Exact NVIDIA target `nvidia/nemotron-3-ultra-550b-a55b` is supported through the ClosedCode-native path.
- [x] Exact Z.AI target `glm-4.7-flash` is supported through the ClosedCode-native path.
- [x] Provider/model selection, authenticated requests, durable sessions, streaming/event delivery, file/tool execution, steering, and cancellation primitives exist.
- [x] Agent-native project manipulation exists: list/read/search, targeted write/patch, create directory, move/rename, delete, shell, Git status/diff/history.
- [x] Long-horizon execution no longer depends on a small normal round ceiling.
- [x] Repeated context compaction preserves mission instructions, negative constraints, steering, and recent continuity through deterministic regression.
- [x] Progress/stagnation guardrails distinguish productive long runs from repeated no-progress loops.
- [x] Terminal outcomes are machine-visible as completed, cancelled, blocked_stagnation, resource_limit, or error.
- [x] Marathon Harness exists as qualification infrastructure and has demonstrated 100+ real tool-call execution.
- [~] Bounded finalization exists through opt-in `finalizeAfterTools`; real-provider acceptance of the bounded-finalization contract remains to be closed.
- [ ] One real long-horizon qualification must finish with trustworthy `termination=completed`, non-empty final prose, preserved mission/steering constraints, and the required final-report contract.
- [ ] Deep cancellation regression must prove cancellation remains responsive after substantial tool activity/compaction and leaves no orphaned provider, permission, retry, observer, or runtime state.
- [ ] ASK / GUARDED regression must prove approval, rejection, mission preservation while waiting, and cancellation during a permission wait.
- [ ] YOLO / FULL DANGER ACCESS regression must prove routine project-scoped autonomy without routine prompts while preserving workspace/task boundaries.
- [ ] Final regression must prove the finished Android client + backend + provider/tool path as one integrated coding-agent product.
- [ ] Produce a release-candidate APK, hash/verify it, copy it to an accessible device path, and stop before installation so the Director can install it through Android.

### Primary objectives

- [ ] Repair the first-message-history defect in which a new thread can lose the first visible user prompt.
- [ ] Repair transcript chronology so tool events cannot appear after final assistant prose unless they genuinely occurred later.
- [ ] Preserve request/session/event ordering through reload, reconnect, and Copy Session/export.
- [ ] Add completion sound behavior for successful terminal completion.
- [ ] Add Android notification-tray completion notification when ClosedCode is not foreground-visible.
- [ ] Add transcript snap-to-top / snap-to-bottom navigation controls without cluttering the primary agent surface.
- [ ] Reorganize top controls so growth in functionality does not cause permanent primary-screen sprawl.
- [ ] Add theme controls in Settings rather than on the primary agent screen.
- [ ] Provide Light and Dark themes.
- [ ] Provide Chocolate Mint as an additional theme.
- [ ] Complete Android lifecycle/reconnect regression after transcript/session repairs.
- [ ] Preserve visible provider/model/session/workspace/autonomy identity without expanding the top-level UI unnecessarily.

### Secondary objectives

- [ ] Reduce unnecessary API calls, redundant reloads, and avoidable latency discovered during regression.
- [ ] Improve diagnostics so provider business codes/messages, termination reasons, and actionable runtime failures remain visible without leaking secrets.
- [ ] Continue hardening packet/control-plane helpers so process ownership, JSON validation, and evidence collection use structural methods instead of fragile text matching.
- [ ] Keep qualification artifacts, checkpoint evidence, and five-/twenty-operation reviews split into navigable documents rather than allowing checkpoint files to become the only source of truth.
- [ ] Retire dead code, obsolete temporary scaffolding, and superseded qualification machinery once replacement paths are proven.
- [ ] Keep build/package/version/hash evidence deterministic and reproducible.
- [ ] Keep real-device testing as a required part of Android defect and release validation.

### Optional objectives

- [-] Additional theme packs beyond Light, Dark, and Chocolate Mint.
- [-] System-theme following as a third appearance mode.
- [-] Manual file-browser/editor expansion beyond what is necessary to support the coding-agent workflow.
- [-] Additional transcript convenience actions beyond top/bottom navigation and Copy Session.
- [-] Additional provider adapters after the release candidate unless separately promoted by the Director.
- [-] Cosmetic animation, decorative UI, or branding work that does not improve agent usability, correctness, or accessibility.

## Completion semantics — 2026-09-20

ClosedCode completion is mission-driven rather than universally tool-count-driven.

The `finalizeAfterTools` mechanism is an opt-in qualification/bounded-task control. It must not become a universal production rule such as "all missions stop at 120 tools."

Normal agent execution should continue while meaningful progress is being made and should end when:

- the assigned definition of done is satisfied;
- a genuine blocker remains;
- the agent needs information only the user can supply;
- the user cancels;
- or a real safety/resource condition requires termination.

High tool count alone is not failure. Low tool count alone is not success. The accepted result is the completed mission with trustworthy evidence and preserved constraints.

## Qualification infrastructure boundary — 2026-09-20

The Marathon Harness is test/qualification infrastructure, not a second coding agent.

It may:

- launch one intended ClosedCode agent qualification request;
- observe event/status evidence;
- count tool calls, unique signatures, compactions, permissions, errors, guardrails, steering, and terminal state;
- post predetermined steering at predetermined thresholds;
- issue cancellation when cancellation itself is the test;
- capture final evidence and classify the run.

It must not:

- make repository/coding decisions on behalf of the provider model;
- inspect the repository independently and feed answers to the provider model;
- patch ClosedCode as part of the qualification run;
- silently change the definition of done;
- restart failed missions until one happens to pass;
- bypass ASK/YOLO semantics;
- become required production transit between Android and the ClosedCode agent.

## UI stability principle — 2026-09-20

ClosedCode should prefer adding capability behind stable interaction surfaces rather than continually expanding the primary agent screen.

Preferred placement order for new functionality:

1. backend/runtime behavior when no new direct control is required;
2. existing interaction surface;
3. Settings;
4. contextual menu, sheet, or dialog;
5. permanent primary-screen control only when the action is frequent enough to justify persistent space.

Once the release UI is accepted, preserve stable placement and behavior of the core interaction surfaces unless a demonstrated usability/correctness problem requires change.

In particular:

- theme selection belongs in Settings;
- completion-sound and notification controls belong in Settings / Android notification channels;
- infrequent actions should prefer contextual surfaces;
- the composer, transcript, Send/Steer/Stop behavior, session access, and provider/model access should not be repeatedly rearranged merely because new backend capability is added;
- feature growth should not automatically imply primary-screen growth.

## Architecture

ClosedCode Android APK → localhost ClosedCode backend/control layer in Termux → supported provider/runtime adapters + filesystem/tools.

OpenCode remains an important compatibility/reference backend where its runtime path is functional, but it is no longer a mandatory transit layer for every provider.

GPT-Termux-Relay is protected infrastructure. It must not be used as ClosedCode source scaffolding or modified merely to simplify ClosedCode development.

### Soft architecture amendment — 2026-09-18

The roadmap is amended to recognize the provider-compatibility pivot as a first-class ClosedCode architecture, not a temporary workaround.

Earlier work assumed that NVIDIA and Z.AI/GLM should traverse OpenCode's compiled agent/runtime graph on Android/Bionic. Repeated A/B qualification and source archaeology showed that this assumption was not reliable:

- OpenCode/Bun compiled graph behavior reproduced the internal `a.name`/LayerNode failure on the affected path;
- equivalent source/runtime controls passed when compile-time splitting was removed;
- upstream Android/Termux compatibility records independently confirm that OpenCode's v1/Bun-era runtime has real platform-specific compatibility constraints, while newer upstream work is moving away from that architecture;
- continuing to force every ClosedCode provider through that graph would make ClosedCode dependent on an upstream incompatibility it does not own.

The adopted re-approach is therefore:

**ClosedCode owns the provider compatibility boundary.**

For providers such as NVIDIA and Z.AI/GLM, ClosedCode may communicate through its own Termux-side provider adapter/session layer and present that capability to the Android app through the ClosedCode protocol.

This architecture is considered a supported product path when it meets the same quality bar as any other backend path:

- exact provider/model identity;
- authenticated requests;
- streaming where supported;
- durable session continuity;
- cancellation/stop behavior;
- explicit errors;
- secure credential handling;
- tool/file capability where supported;
- Android reconnect/lifecycle behavior;
- diagnostics and qualification evidence.

The implementation developed during Ops201–225 has already proved substantial parts of this path, including NVIDIA provider reachability, Android routing, persisted multi-turn context, Z.AI/GLM reachability/streaming, and persistent startup ownership.

Accordingly, roadmap language should no longer treat this approach as an awkward bypass, emergency sidecar, or second-class fallback merely because it does not traverse OpenCode's compiled graph.

It is a deliberate ClosedCode-native provider compatibility architecture chosen after evidence invalidated the earlier architectural assumption.

OpenCode-backed operation remains supported where useful and functional. This amendment does not require removing OpenCode; it removes the requirement that OpenCode's compiled runtime graph sit in the critical path for every provider.

The detailed pivot/provenance record remains:

`docs/closedcode/CLOSEDCODE_PROVIDER_PASSTHROUGH_PIVOT_2026-09-18.md`

## Governance precedence

### Universal Director 25-operation STOP ruling

At every operation number divisible by 25 — Op25, Op50, Op75, Op100, Op125, Op150, Op175, Op200, Op225, Op250, and every later equivalent — **STOP. S-T-O-P.**

The checkpoint is consumed whether its Relay packet succeeds, fails, times out, is rejected, is malformed, or yields no usable checkpoint artifact.

A failed checkpoint Relay operation does **not** authorize the next Relay operation as checkpoint recovery.

No Relay operation after the checkpoint may be issued for evidence recovery, documentation, Git reconciliation, read-only inspection, retry, repair, or mission continuation until the Director explicitly and purposefully releases the named checkpoint.

Checkpoint review/evidence presentation must use permitted non-Relay mechanisms while the gate is closed.

This is the ultimate universal Director ruling for this roadmap. It supersedes conflicting phase ranges, recovery language, mission plans, audits, retry rules, or agent interpretations. Only a later explicit Director ruling may intentionally alter it.

This roadmap defines product phases and bounded scope; it does **not** authorize crossing Heavy Engineer governance gates. The authoritative Heavy Engineer control harness governs operation accounting, five-operation audits, twenty-operation reviews, and twenty-five-operation hard checkpoints.

A range such as `Ops176–200` becomes available only after any intervening mandatory checkpoint has been completed and freshly released by the Director. Roadmap wording, phase transitions, audit notes, or agent-authored statements cannot self-authorize continuation. When a checkpoint is active, no next-operation planning, script/patch authoring, packet preparation, or substantive mission work may begin until the Director explicitly releases that checkpoint.

## Immediate governance recovery — Operation 150

Heavy Engineer 7 begins by closing the interrupted Heavy Engineer 6 governance cycle.

Reconstructed state at 2026-09-17:
- Op146 — RED / Relay connection refused.
- Op147 — GREEN / heartbeat.
- Op148 — GREEN / read-only inspection.
- Op149 — reached, but terminal result unavailable; possible partial mutation remains unproven.
- Op150 — not trustworthily completed.

Op150 is governance recovery only. It must be read-only and reconstruct:
- canonical repo/path;
- branch and HEAD;
- remote HEAD;
- staged, unstaged, and untracked state;
- relevant diffs and source hashes;
- build/version metadata;
- generated APKs and hashes;
- running build/process state;
- ClosedCode backend state;
- Relay state;
- protected-infrastructure state;
- evidence of any partial mutation attributable to Op149.

Op149 remains UNKNOWN/RED-UNPROVEN unless stronger direct evidence proves otherwise.

Produce Audit 146–150 and the Op150 hard checkpoint, then HARD STOP pending fresh Director authorization for Op151+.

Related evidence:
- `docs/incidents/HEAVY_ENGINEER6_OP149_150_CHECKPOINT_INTERRUPTION_2026-09-17.md`
- `docs/diagnostics/CLOSEDCODE_NETWORK_FAILURE_CAPTURE_PLAYBOOK.md`

## Operations 151–175 — DELIVERY

This block exists to make ClosedCode genuinely usable as a coding-agent APK.

By Op175, prove the real end-to-end product path, prioritizing implementation and device proof over speculative architecture.

Required delivery targets:
- real provider discovery;
- real provider connection/authentication;
- exact NVIDIA model `nvidia/nemotron-3-ultra-550b-a55b` working;
- Z.AI `zai/glm-4.7-flash` working if the live provider contract permits;
- exact model/provider selection reflected in actual prompt requests;
- real prompt submission;
- streamed model output;
- session create/open/resume/delete;
- real file reads;
- real file writes/edits;
- diffs/change review;
- real tool/command execution through Termux;
- permission/question/approval handling;
- visible tool and error events;
- cancellation/stop behavior;
- persistent settings;
- Android lifecycle/reconnect behavior;
- UI consistent with the Director-supplied OpenCode screenshots;
- ClosedCode branding and identity throughout;
- no GPT-Termux-Relay implementation reuse.

The Op175 target is a usable APK the Director can actually run as a coding agent.

If a blocker threatens that target, diagnose it early rather than spending the entire delivery block before proving viability.

## Operations 176–200 — STABILIZATION

After Op175, broad feature expansion stops unless a missing capability is required for the core product to function.

This block is for:
- debugging and regression repair;
- crash handling;
- reconnect/recovery behavior;
- Android lifecycle failures;
- provider/API edge cases;
- session-state consistency;
- filesystem/tool error handling;
- UI polish and defects;
- performance and latency;
- unnecessary API-call reduction;
- context/token behavior;
- build/install reliability;
- stale-state handling;
- permission/question correctness;
- diagnostics quality;
- security and secret-handling verification;
- provenance audit against GPT-Termux-Relay;
- removal of dead code and temporary scaffolding;
- final documentation.

Use real-device testing aggressively.

## Operation 200 — ORIGINAL TERMINAL CAMPAIGN CHECKPOINT

The original roadmap expected this engineering campaign to finish by Op200.

Original intended progression:
- Op150 — recover governance;
- Ops151–175 — make ClosedCode work;
- Ops176–200 — make ClosedCode reliable;
- Op200 — final campaign checkpoint.

That expectation remains useful historical scope evidence, but it was superseded in practice by explicit Director-authorized continuation after the OpenCode/Bionic incompatibility forced a bounded architecture re-approach.

Continuation beyond Op200 is therefore not classified as roadmap drift by itself. It is justified only to complete and stabilize the Director-approved provider compatibility architecture and the remaining core-product gaps.

The high bar against mission sprawl still applies: unrelated feature expansion should be deferred.

## Final completion sprint — Ops226–250

The Director explicitly released the Op225 hard checkpoint on 2026-09-18.

**Op226 is authorized.**

This is the final intended Heavy Engineer sprint for the current ClosedCode campaign.

Target:

- finish before Op250 if possible;
- finish by Op250 at the latest;
- deliver a genuinely usable Android coding-agent APK for on-device development;
- prioritize full file/project manipulation, shell/tool execution, durable sessions, provider correctness, streaming/cancellation, lifecycle recovery, and practical coding workflows over low-value cosmetic expansion.

The practical ambition is an on-device development experience approaching the effectiveness of a serious coding agent such as Codex, within the limits of the device/provider architecture.

Before every Relay operation in this sprint, freshly read/verify the current Big Three:

1. Heavy Engineer control harness;
2. Relay recovery guide;
3. this ClosedCode delivery/stabilization roadmap.

Do not rely on remembered copies.

The Director authorization record is:

`docs/closedcode/HEAVY_ENGINEER8_OP225_RELEASE_FINAL_SPRINT_2026-09-18.md`

Op250 remains a mandatory universal hard stop.

## Device-specific APK installation rule

The current device uses the **Google Play distribution of Termux**.

Heavy Engineer / GPT-Termux-Relay must **not attempt to invoke APK installation through Termux or Relay on this device**.

Allowed:
- build the APK;
- hash/verify it;
- copy it to an accessible location;
- report exact path/version/hash;
- verify package/version/launch after the Director manually installs it.

Prohibited unless the Director explicitly overrides this rule:
- `pm install`;
- `cmd package install*`;
- package-session / PackageInstallerService tricks;
- shell-streamed APK installation;
- `termux-open` or equivalent commands whose purpose is to initiate installation;
- repeated alternative install mechanisms after one fails.

The normal Android package installer is the installation owner. Stop at a verified APK and ask the Director to install it manually.

Do not burn Relay operation budget attempting installation workarounds.

## Protected Relay boundary

Do not:
- use Relay Android code as scaffolding;
- copy Relay implementation into ClosedCode;
- develop ClosedCode inside the Relay repository;
- alter Relay source/config merely to make ClosedCode easier;
- install a ClosedCode build over the Relay package;
- blur package/project identities.

If Relay fails operationally, use the established Relay recovery procedure rather than changing Relay architecture.

## Interrupted-operation fail-safe

If a Relay operation may have mutated state but its terminal result is lost because of connection failure, session crash, message limit, timeout, or other transport interruption:

1. Preserve that operation as `UNKNOWN/RED-UNPROVEN`.
2. Stop substantive mission work.
3. Do not blindly retry the mutating command.
4. The next Relay operation must be read-only state reconstruction.
5. When connectivity is uncertain, classify DNS, HTTPS, Git, Relay, and backend layers independently using the applicable diagnostic procedure.
6. Retry or continue only after actual state is known, under a different operation number.
7. If the uncertainty occurs at an audit/review/checkpoint boundary, governance recovery rules take precedence.
8. Never expose secrets while collecting diagnostics.

## Product principle

Do not produce another plumbing demo.

Do not produce another pretty shell.

The product target remains a real ClosedCode coding-agent application, not a plumbing demo or cosmetic shell.

The original Op175/Op200 dates remain historical targets rather than claims about the current operation number. Current continuation is bounded to completing and stabilizing the approved provider compatibility architecture and remaining core coding-agent capabilities.

## Agent autonomy amendment — 2026-09-18

The Director clarified the intended meaning of file manipulation and coding-agent capability.

ClosedCode is **not** being developed primarily as a manual Android file manager/editor.

The core requirement is that the **agent itself** can autonomously inspect and modify a real project in the manner of a serious coding agent such as Codex.

The ratified execution model is:

`docs/closedcode/CLOSEDCODE_AGENT_EXECUTION_MODEL_2026-09-18.md`

Accordingly:

- manual file-browser/editor capability is optional convenience, not a completion gate;
- agent autonomy and software-development effectiveness are the acceptance target;
- the agent should inspect, edit, create, move/rename, delete, run tools, test/build, diagnose, repair, and continue without requiring the user to manually operate files;
- dedicated patch/edit/delete/move/Git-diff tooling should be preferred where it improves reliability over whole-file replacement or ad-hoc shell use;
- a user-selectable **YOLO / FULL DANGER ACCESS** mode must eliminate routine per-write/per-command approval prompts;
- YOLO removes approval friction, not task-scope reasoning;
- vague instructions such as "fix this problem" do not authorize unrelated destructive action against system files, unrelated projects, user data, credentials, or protected infrastructure;
- the default autonomous scope remains the selected project/workspace plus tooling reasonably necessary to complete the assigned task;
- final acceptance should use a real multi-step coding task: inspect → edit → build/test → diagnose → repair → finish.

The existing Op250 hard stop remains active. This roadmap amendment does not authorize Op251.

## Roadmap self-check

At every formal review and hard checkpoint, answer plainly:

1. Are you drifting from the roadmap?
2. Based on the printed audits and review, do you feel like you are drifting from the roadmap?
3. Is the roadmap outdated?
4. Do we need to redesign the roadmap?
