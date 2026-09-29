# ClosedCode — Temporary Test Pause / Codex Handoff — 2026-09-28

**Status:** TEMPORARILY PAUSED FOR CODEX COMPLETION  
**Date:** 2026-09-28  
**Repository:** `monag144/ClosedCode`  
**Working branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`  
**Base branch:** `dev`

## Why this pause exists

Director testing is intentionally paused so the remaining update can be finished with Codex rather than continuing the long Heavy Engineer / GPT-Termux-Relay sequence.

This is a handoff, not a rollback. Preserve all qualified work, audits, release-candidate provenance, and device-test evidence already accumulated. Codex should continue from the current branch state, close the remaining acceptance gaps, and prepare the branch for final review/merge.

Heavy Engineer testing/Relay work is frozen after **Op491**. Do not issue Op492 while the Codex handoff is active. If the Heavy Engineer workflow is later resumed, continue from Op492; the next five-operation audit is Op495 and the next hard checkpoint is Op500.

## Current Git / PR state

As of this handoff, there is **no open GitHub pull request** for this branch. Treat the branch itself as the current PR candidate.

Compared with `dev`, this branch is:

- **348 commits ahead**
- **0 commits behind**
- **296 changed files**
- approximately **+21,815 / -11 lines**

Current branch HEAD at the pause:

`af1684dc7b4cc63389d51fca1793f1cfc9b08b06`

Last qualified product commit:

`35151242eb27c4af4cf8f431663f5d614a4d4b25`

Latest governance/certification commits:

- Ops486–490 audit + Ops471–490 review: `cffa877e0995e2167b827abcb7b296fe57e6d741`
- Full Access RC certificate: `af1684dc7b4cc63389d51fca1793f1cfc9b08b06`

## What this update has already delivered

### Android coding-agent client

ClosedCode now has a native Android client with:

- session creation/open/resume/delete;
- transcript rendering and durable reload behavior;
- provider/model/agent/effort controls;
- streaming responses;
- Stop/cancellation;
- steering while an agent run is active;
- tool-event rendering;
- connection/status UI;
- context-usage UI;
- project/session context surfaces;
- improved touch targets and Session Context drag behavior;
- Light, Dark, and Chocolate Mint themes;
- completion sounds and Android completion notifications;
- settings/persistence for autonomy and notification behavior.

### ClosedCode-native provider/runtime path

ClosedCode owns its provider compatibility boundary rather than requiring every provider to transit OpenCode's Android/Bionic runtime graph.

Qualified provider/runtime work includes:

- NVIDIA/Nemotron path;
- Z.AI/GLM path;
- authenticated provider requests;
- streaming;
- retries/backoff for retryable provider failures;
- durable session history;
- cancellation;
- provider/model identity;
- explicit backend health/state reporting.

Current live backend version at the last qualification point: **0.8.19**.

### Coding-agent tool surface

The agent can use real project tools for:

- workspace list;
- workspace read;
- workspace search;
- workspace write;
- targeted patch;
- mkdir;
- move/rename;
- delete;
- Git status/diff/log;
- shell/build/test commands.

This has been exercised on real device workflows rather than only mocked unit paths.

### Long-horizon agent behavior

The branch includes:

- durable first-user-message persistence;
- durable accepted steering;
- durable tool timeline events;
- final-assistant persistence;
- context compaction that preserves mission constraints and recent evidence;
- stagnation detection;
- long-run operation support;
- explicit terminal outcomes;
- qualification/marathon infrastructure.

### Permission/autonomy model

Three distinct modes now exist:

**ASK / Guarded**
- workspace-contained;
- mutation tools require approval unless persistently authorized;
- persistent safe workspace approvals are scoped by **workspace + tool**;
- shell persistent approval remains exact-command scoped.

**YOLO / Auto-approve**
- workspace-contained;
- routine workspace mutation tools auto-approve;
- shell remains permission-gated;
- this is explicitly **not** Full Access.

**FULL ACCESS / Danger**
- **OFF by default**;
- explicit danger confirmation required to enable;
- mutually exclusive with YOLO;
- removes ClosedCode's selected-workspace path boundary;
- absolute paths may reach any filesystem location the Termux process is legally permitted to access;
- filesystem mutation tools and shell auto-approve;
- Android/Linux permissions, SELinux, mount permissions, and root state remain hard OS limits.

### Automated regression state

At Op489/Op490, all of the following were GREEN:

- Full Access regression;
- permission-policy regression;
- theme regression;
- steering-durability regression;
- device-interaction regression;
- Session Context drag regression;
- notification/sound regression;
- transcript regression;
- integrated UI regression;
- Android build.

## Latest immutable release candidate

Full Access candidate:

`/sdcard/Download/ClosedCode-RC-0.2.7-full-access-op491.apk`

- bytes: **128,952**
- SHA-256: `0a87502c6d6f68a3faa1ffe8f3ff1f8c5e924c0ceb55e42a5f6ca64862b5c212`
- engineering installation: **not performed**
- device acceptance: **pending**

Historical RCs and their certification evidence must not be overwritten.

## Physical device evidence already accepted

GREEN on the preceding device-follow-up candidate:

- permission dialog mechanics;
- persistent workspace-write approval;
- independent persistent workspace-delete approval;
- Delete Session hitbox;
- Dark theme;
- Chocolate Mint controls;
- Session Context drag;
- YOLO contained auto-approve;
- transcript chronology;
- one true cold-reopen persistence test;
- Agent-complete notification delivery.

## What still needs to be done

The remaining work is much smaller than the work already completed.

### 1. Finish physical acceptance of the Full Access candidate

Test the exact Op491 RC for:

- Full Access starts OFF unless a legitimate existing preference says otherwise;
- enabling Full Access shows the danger confirmation;
- Full Access and YOLO are mutually exclusive;
- Full Access can read/write/delete outside the selected workspace using an absolute path that Termux is actually permitted to access;
- shell auto-approves in Full Access;
- switching back to YOLO restores shell permission prompts;
- ASK mode still preserves workspace containment and permission behavior.

### 2. Close the deferred device checks

Still YELLOW only because they were deferred, not because they failed:

- repeat true cold-reopen session/steering persistence;
- observe mid-run steering/task-continuity behavior on the latest build;
- directly verify YOLO shell gating on-device.

### 3. Repair only demonstrated blockers

If the latest physical test finds a real blocker:

- reproduce it;
- make the narrowest repair;
- extend/update the appropriate regression;
- rebuild;
- re-run the complete relevant regression suite;
- package a new immutable RC;
- preserve old RCs and hashes.

Do not begin another broad feature sprint.

### 4. Reconcile documentation before merge

The 2026-09-17 stabilization roadmap contains historical checklist items whose boxes predate later qualified work. Before final merge, reconcile the roadmap/checklist against the later audits and device evidence so the documentation does not make already-completed work look unfinished.

### 5. Final integrated acceptance

Run one final realistic coding-agent workflow that demonstrates the intended product:

inspect → edit/create/patch → run/build/test → diagnose if needed → repair → finish → report.

Acceptance should prove:

- correct provider/model identity;
- durable session/transcript;
- correct autonomy mode;
- correct tool execution;
- correct completion behavior;
- no duplicate mutations;
- no unexpected permission bypass outside the selected autonomy contract.

### 6. Open/finalize the actual GitHub PR

No open PR currently exists for this branch.

After Codex closes the remaining gates:

- review the branch against `dev`;
- ensure docs and qualification artifacts are current;
- decide whether any clearly obsolete temporary scaffolding should be removed;
- do **not** delete user-owned device test artifacts without Director authorization;
- open the PR to `dev`;
- use the final acceptance evidence in the PR description.

## Codex handoff mission

Codex should begin by reading:

1. `docs/closedcode/CLOSEDCODE_DELIVERY_AND_STABILIZATION_ROADMAP_2026-09-17.md`
2. `docs/reviews/HEAVY_ENGINEER10_CLOSEDCODE_REVIEW_OP471_490_2026-09-21.md`
3. `docs/audits/HEAVY_ENGINEER10_CLOSEDCODE_AUDIT_OP486_490_2026-09-21.md`
4. `docs/qualification/HEAVY_ENGINEER10_RELEASE_CANDIDATE_0_2_7_FULL_ACCESS_OP491_2026-09-21.md`
5. this handoff.

Primary mission:

> Finish the current ClosedCode update from the existing qualified branch, close the remaining physical/integrated acceptance gaps, repair only demonstrated blockers, reconcile stale documentation, and prepare a clean PR to `dev`.

Do not reset or recreate the implementation from scratch.

## Device-local user state

The Heavy Engineer workflow established a device-local baseline of **21 untracked user-owned files** (the FoxyApp test project plus five `vibe*.txt` files) with digest:

`86defec32e511b1e406e80ffd0b9b597be7a9fc278860cafa8180104a8a25d80`

These are not source-cleanup targets. Do not delete or mutate them merely to obtain a clean Git status unless the Director explicitly authorizes it.

## Pause disposition

**ClosedCode manual acceptance testing is temporarily paused. Codex is now the preferred execution engine for completing this update.**

Resume Director device testing after Codex produces the next qualified candidate or confirms that Op491 remains the correct candidate for final acceptance.
