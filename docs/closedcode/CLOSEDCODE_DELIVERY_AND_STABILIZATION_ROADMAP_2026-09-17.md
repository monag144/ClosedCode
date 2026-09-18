# ClosedCode Delivery and Stabilization Roadmap — 2026-09-17

**Timestamp:** 2026-09-17

## Architecture

ClosedCode Android APK → localhost ClosedCode/OpenCode backend/control layer in Termux → providers/models + filesystem/tools.

GPT-Termux-Relay is protected infrastructure. It must not be used as ClosedCode source scaffolding or modified merely to simplify ClosedCode development.

## Governance precedence

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

## Operation 200 — TERMINAL CAMPAIGN CHECKPOINT

This engineering campaign is expected to finish by Op200.

Intended progression:
- Op150 — recover governance;
- Ops151–175 — make ClosedCode work;
- Ops176–200 — make ClosedCode reliable;
- Op200 — final campaign checkpoint.

There should be an extremely high bar for continuing this campaign beyond Op200. Work not required for a functional, reliable ClosedCode product should be deferred rather than allowing the mission to sprawl indefinitely.

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

By Op175, produce a real ClosedCode coding-agent application.

By Op200, make it stable enough that the Director should not need another Heavy Engineer campaign merely to finish the basic product.
