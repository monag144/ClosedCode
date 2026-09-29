# ClosedCode Agent Execution Model — Director Amendment — 2026-09-18

**Status:** DIRECTOR-RATIFIED PRODUCT DIRECTION  
**Project:** ClosedCode  
**Branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`

## Core correction

ClosedCode is not primarily a manual file-manager/editor application.

The core product is the **coding agent itself**.

The Director's intended interaction model is:

> Give ClosedCode a software-development task in natural language. ClosedCode inspects the project, determines what must change, edits the relevant files, creates/removes/moves project files when appropriate, runs commands/builds/tests, diagnoses failures, iterates until the task is complete, and then reports what it changed.

The acceptance standard is therefore closer to Codex-style delegated software engineering than to a human-operated Android file browser.

Existing manual file browsing/editing UI may remain as a convenience if it is already useful, but:
- it is not the product objective;
- it is not a completion gate;
- no remaining Heavy Engineer budget should be spent expanding it unless needed to support the agent workflow;
- future product qualification should measure agent autonomy and software-development effectiveness first.

## Agent capability target

ClosedCode should be able to autonomously perform, where relevant to the user's task:

- inspect repository/project structure;
- list/read/search files;
- understand existing code before editing;
- make targeted edits rather than unnecessarily rewriting whole files;
- create files and directories;
- rename/move files and directories;
- delete project files/directories when the task genuinely requires it;
- inspect Git status/diff/history;
- produce and apply multi-file changes;
- run project commands;
- run tests, linters, formatters, builds, compilers, package/project tooling, and Git commands;
- inspect failures and logs;
- repair its own failed implementation attempts;
- repeat the edit/test/repair loop without waiting for the Director between ordinary steps;
- preserve session/task continuity;
- stop/cancel promptly when requested;
- report the final result and meaningful remaining failures honestly.

Dedicated agent tools should be added where they materially improve reliability over raw shell use, including patch/edit, delete, move/rename, and Git diff/status.

The shell remains an important general-purpose escape hatch for legitimate project tooling.

## Permission model

The current model of asking for approval for each ordinary write/mkdir/shell action is not the intended default experience.

ClosedCode must support an explicit user-selectable autonomy setting.

Recommended modes:

### ASK / GUARDED

- mutation/tool approvals may be shown;
- useful for cautious or unfamiliar work;
- existing approval behavior may serve this mode.

### YOLO / FULL DANGER ACCESS

When explicitly enabled by the user:

- ordinary project file writes are auto-approved;
- create/mkdir is auto-approved;
- rename/move/delete inside the selected project is auto-approved;
- shell commands needed for the assigned development task are auto-approved;
- builds/tests/linters/formatters/Git/project tooling run without per-command prompts;
- the agent may autonomously iterate through multiple tool rounds until the assigned task is complete or it reaches a real blocker;
- ClosedCode should not pester the user for routine confirmations.

This is an autonomy setting, not permission to behave irrationally or destructively.

## YOLO does not mean "interpret vaguely, destroy broadly"

A broad task such as:

> Fix this problem.

does **not** authorize unrelated destructive actions.

Even in YOLO / FULL DANGER ACCESS mode, the agent must preserve the user's task intent and operate proportionally.

### Required behavioral invariant

**Do what is reasonably necessary to accomplish the user's stated development task; do not broaden destructive scope merely because approval prompts are disabled.**

Examples:

- "Fix the build" may authorize editing project files, changing project configuration, running build tools, and removing generated project artifacts when relevant.
- It does not authorize deleting Termux, Android system files, unrelated repositories, user photos, credentials, home-directory contents, or other unrelated data.
- "Clean the project" may justify deleting generated/cache/build artifacts inside the selected project.
- It does not mean "wipe the device."
- "Remove this dependency" may justify deleting dependency-specific project files/configuration.
- It does not authorize mass deletion outside the task's project context.

## Safety boundary for autonomous mode

YOLO / FULL DANGER ACCESS removes repetitive approval friction. It does **not** remove scope reasoning.

The default autonomous boundary is the selected project/workspace plus ordinary tooling needed to work on that project.

The agent must not perform clearly unrelated destructive operations against:

- Android/system paths;
- Termux installation/runtime internals;
- unrelated repositories/projects;
- user personal files;
- credentials/secrets;
- protected GPT-Termux-Relay infrastructure;

unless the Director explicitly assigns a task whose scope genuinely includes that target.

If a requested task explicitly concerns one of those targets, handle it under the applicable project/governance rules rather than silently treating YOLO as blanket authority.

## Codex-like operating behavior

The desired experience is:

1. User assigns a task.
2. Agent inspects what it needs.
3. Agent forms its own bounded working plan.
4. Agent edits/runs/tests/diagnoses autonomously.
5. Agent retries and repairs ordinary failures.
6. Agent stops only when:
   - the task is completed;
   - it reaches a blocker it genuinely cannot resolve;
   - it needs information only the user can supply;
   - the user stops/cancels the task.
7. Agent reports the finished work clearly.

Routine intermediate writes/commands should not require Director interaction when YOLO mode is enabled.

## Product acceptance implication

A final ClosedCode APK should not be considered complete merely because:

- files can be manually opened in the Android UI;
- individual write/read calls succeed;
- a single tool loop works;
- the app can display a file browser.

Completion should be judged by whether a real provider/model can accept a meaningful coding task and independently perform a multi-step inspect → edit → build/test → diagnose → repair → finish workflow on-device.

The best final acceptance test is a genuine coding task against a real project, performed primarily through agent autonomy rather than manual file manipulation.

## Relationship to current Op250 hard stop

This document records Director product direction only.

It does **not** release the Op250 hard checkpoint and does not authorize Op251 or any Relay operation.

The universal 25-operation STOP ruling remains active until the Director separately and explicitly releases Op250.
