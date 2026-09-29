# Heavy Engineer 8 — Op225 Director Release and Final Sprint Authorization

**Date:** 2026-09-18  
**Project:** ClosedCode  
**Branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`  
**Checkpoint being released:** Op225  
**First authorized next Relay operation:** **Op226**  
**Final hard checkpoint:** **Op250**

## Explicit Director release

The Director explicitly and purposefully releases the Op225 hard checkpoint.

**Op226 is authorized.**

This release satisfies the universal multiple-of-25 hard-stop rule added to the Heavy Engineer control harness, Relay recovery guide, and ClosedCode roadmap.

No earlier packet failure, recovery rule, roadmap range, or agent interpretation authorizes this continuation. This document and the Director instruction it records do.

## Final sprint objective

Wrap the Heavy Engineer ClosedCode campaign by **Op250 at the latest**.

Finishing earlier is strongly preferred and earns extra credit.

Do not allow the campaign to roll into Op251+ except under a new explicit Director decision made at the Op250 hard checkpoint.

## Product target

Deliver an APK the Director can genuinely use for on-device software development.

The target is practical effectiveness approaching a serious coding agent such as Codex, within the capabilities of the device/provider architecture.

The APK should support, as completely as reasonably achievable before Op250:

- full project/file browsing;
- file reads;
- file creation;
- file edits/replacements;
- file deletion with appropriate confirmation/guarding;
- directory creation and navigation;
- search across project files;
- diffs/change review;
- shell/command execution through the ClosedCode-owned Termux/backend path;
- provider/model selection;
- durable sessions and context continuity;
- visible model/tool/error events;
- streaming where supported;
- Stop/cancel behavior;
- permission/question/approval handling;
- reconnect/lifecycle recovery;
- persistent settings;
- secure credential handling;
- practical coding-agent workflows from the Android app;
- clean install/build qualification on-device.

Do not spend the remaining operation budget polishing low-value cosmetics while core coding-agent capability is incomplete.

## Architecture amendment acknowledgement

The active roadmap has been soft-amended.

The provider architecture is no longer treated as an awkward workaround or temporary sidecar.

The approved architecture is a **ClosedCode-native provider compatibility architecture** in which ClosedCode owns the provider compatibility boundary and may route NVIDIA and Z.AI/GLM through its own Termux-side provider/session layer.

OpenCode remains a compatibility/reference backend where useful and functional, but its compiled graph is not required to sit in every provider's critical path.

Relevant records include:

- `docs/closedcode/CLOSEDCODE_DELIVERY_AND_STABILIZATION_ROADMAP_2026-09-17.md`
- `docs/closedcode/CLOSEDCODE_PROVIDER_PASSTHROUGH_PIVOT_2026-09-18.md`

## Mandatory Big Three read — every operation

Before **every new Relay operation** in Ops226–250, re-read or freshly verify the current authoritative versions of the Big Three:

1. **Heavy Engineer control harness**  
   Repository: `monag144/GPT-Termux-Relay`  
   Path: `termux_relay/docs/HEAVY_ENGINEER_BASELINE_CONTROL_HARNESS.md`

2. **Relay recovery guide / operation recovery procedure**  
   Repository: `monag144/GPT-Termux-Relay`  
   Path: `termux_relay/docs/RECOVERY_GUIDE.md`

3. **ClosedCode delivery and stabilization roadmap**  
   Repository: `monag144/ClosedCode`  
   Path: `docs/closedcode/CLOSEDCODE_DELIVERY_AND_STABILIZATION_ROADMAP_2026-09-17.md`

Do not rely on memory of them.

If any of the Big Three changed since the previous operation, reconcile the new text before preparing or issuing the next Relay packet.

The universal 25-operation STOP rule remains absolute.

## Governance reminders

- Continue sequentially at **Op226**.
- Preserve Op225 as historical RED / PACKET_REJECTED.
- Preserve the attempted Op226-before-release governance breach as historical evidence.
- Five-operation audits remain mandatory.
- Twenty-operation review remains mandatory.
- Op250 is a mandatory hard checkpoint.
- At Op250: **STOP. S-T-O-P.**
- A failed Op250 packet does not authorize Op251 recovery.
- No Op251 exists without a new explicit Director release.

## Roadmap discipline

At every formal review and checkpoint, answer:

1. Are you drifting from the roadmap?
2. Based on the printed audits and review, do you feel like you are drifting from the roadmap?
3. Is the roadmap outdated?
4. Do we need to redesign the roadmap?

For this final sprint, favor direct product completion over speculative archaeology unless a blocker makes archaeology necessary.

## Final qualification expectation

By or before Op250, provide Director-facing proof of:

- final branch / HEAD / clean worktree;
- APK path, version, size, SHA-256;
- installability;
- provider connectivity;
- at least one real coding workflow;
- file read/write/edit proof;
- tool/command execution proof;
- session continuity;
- Stop/cancel qualification where implemented;
- provider/model identity correctness;
- Android lifecycle/reconnect behavior;
- security/credential boundary;
- protected GPT-Termux-Relay unchanged;
- remaining defects, if any, stated plainly.

If some ambitious parity target cannot be completed safely by Op250, ship the strongest usable APK possible and state the exact remaining gap. Do not hide incomplete capability behind plumbing or documentation.

## Director message to Heavy Engineer 8

You have done a substantial amount of hard debugging and architecture recovery to get here.

The checkpoint is released.

Finish the product.

Aim to beat Op250 if you can.

Very best of luck.
