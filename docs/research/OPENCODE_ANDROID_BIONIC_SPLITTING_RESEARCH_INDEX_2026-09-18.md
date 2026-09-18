# OpenCode Android/Bionic `a.name` / Bun Splitting Research Index

**Date assembled:** 2026-09-18 UTC  
**Purpose:** Pre-Op200 research handoff for Heavy Engineer 8.  
**Repository:** `monag144/ClosedCode`  
**Current engineering branch:** `closedcode/android-cleanroom-opencode-mobile-20260916`

This index consolidates the earlier Agent-17-era/OpenCode repair research, the first ClosedCode Android-port handoff, the current HE8 rediscovery, and upstream issue evidence around the recurring:

`TypeError: undefined is not an object (evaluating 'a.name')`

failure.

This document is research/navigation only. It does not authorize Op200, runtime replacement, source mutation, or post-Op200 continuation.

## Executive finding

The prior Android/Bionic A/B work established a strong, repeatable build boundary:

- OpenCode 1.18.31 direct source under Bun 1.4.0: PASS.
- OpenCode 1.18.31 direct source under Bun 1.4.1: PASS.
- Bun 1.4.0 compiled Android/Bionic candidate: PASS.
- Bun 1.4.1 compiled with `minify:true, splitting:true`: FAIL.
- Bun 1.4.1 compiled with `minify:false, splitting:true`: FAIL.
- Bun 1.4.1 compiled with `minify:true, splitting:false`: PASS.
- Fresh Bun 1.4.1 normal-splitting control reproduced the failure.

Known-good no-split artifact:
- SHA256: `02367cb9fa073ab37acadd6d4ca35db590f7fd4c775147541104ec604fee6e4e`
- Size: 188,614,920 bytes.

Bun 1.4.0 compiled control:
- SHA256: `26c7610ef19d4982dbd72ed3db7663813543bfcaf4d99834665df1f365bb9905`.

The Android/Bionic no-split result is therefore historical A/B evidence, not a new HE8 hypothesis.

However, upstream OpenCode reports add an important nuance: essentially the same `resolve -> a.name` / `SystemPrompt.environment` failure also appeared on macOS and NixOS/Linux compiled CLI builds around OpenCode 1.18.30. The strongest upstream analysis points to an undefined dependency inside the compiled location-service/LayerNode graph, plausibly created by Bun bundle/chunk module-initialization behavior. Therefore the Android no-split workaround is strongly demonstrated, but the underlying failure class should not be described as proven Android-only.

## Primary internal historical documents

These files live on the archived branch:

`closedcode/android-foundation-20260915`

### 1. Original ClosedCode handoff carrying the prior A/B result

`docs/closedcode/HEAVY_ENGINEER_HANDOFF_2026-09-15.md`

Why read it:
- concise authoritative carry-forward of the prior OpenCode 1.18.31 investigation;
- records the complete Bun 1.4.0 / 1.4.1 split/no-split matrix;
- records the known-good no-split artifact hash and size;
- explicitly states that no OpenCode source patch was required for the successful no-split repair.

### 2. ClosedCode project charter

`docs/closedcode/CLOSEDCODE_PROJECT_CHARTER_2026-09-15.md`

Why read it:
- preserves the original Android/Bionic build baseline;
- states that `splitting:true` reproduced the internal reference/agent failure;
- states that the same source with `splitting:false` passed;
- establishes that direct source execution under both Bun versions passed;
- warns not to assume upstream build defaults are safe on Android/Bionic.

### 3. Original Android roadmap

`docs/closedcode/CLOSEDCODE_ANDROID_ROADMAP_2026-09-15.md`

Why read it:
- defines the exact A/B controls originally intended for reproduction;
- names `/api/config`, `/api/reference`, and `/api/agent` as the qualification gates;
- requires build recipe and artifact hashes to be retained.

### 4. Usable-shell mission

`docs/closedcode/HEAVY_ENGINEER_USABLE_SHELL_MISSION_2026-09-15.md`

Why read it:
- repeats the established pre-mission finding that Bun 1.4.1 + `splitting:true` reproduces the failure and `splitting:false` passes;
- records that minification is not required for the defect;
- states that no OpenCode source patch was required for the known-good no-split candidate;
- describes the intended direct Android/Bionic qualification procedure.

### 5. Heavy Engineer audit log Ops53-75

`docs/closedcode/HEAVY_ENGINEER_AUDIT_LOG_OPS53_75_2026-09-16.md`

Why read it:
- records the first ClosedCode attempt to turn the earlier ad-hoc repair into a reproducible Android build;
- shows the custom Android helper explicitly used `splitting:false`;
- records Bun 1.4.0 and 1.4.1 toolchain discovery;
- records Android/Bionic platform handling;
- documents the later unrelated `@ff-labs/fff-bun` build blocker;
- confirms the earlier split/no-split result was treated as established evidence before HE8.

### 6. Native-port archive disposition

`docs/closedcode/CLOSEDCODE_ANDROID_PORT_ARCHIVE_DISPOSITION_2026-09-16.md`

Why read it:
- explains why the direct ClosedCode Android-native port was archived;
- explicitly says all prior OpenCode/Bun A/B evidence must be preserved;
- prevents confusing the old `fff-bun` native-port blocker with the currently installed OpenCode runtime failure.

## Current HE8 rediscovery documents

On `closedcode/android-cleanroom-opencode-mobile-20260916`:

### 7. Op176-195 mandatory review

`docs/audits/HEAVY_ENGINEER8_CLOSEDCODE_REVIEW_OP176_195_2026-09-18.md`

Key value:
- shows how the current investigation independently moved from a reference-sort theory toward the shared LayerNode/location-service resolver;
- records the recurring minified `resolve -> a.name` stack;
- captures the pre-Op198 state before the historical A/B material was recovered.

### 8. Op198 resilience record

`docs/audits/HEAVY_ENGINEER8_CLOSEDCODE_RESILIENCE_OP198_2026-09-18.md`

Key value:
- explicitly rediscovers that the no-splitting remedy had already been historically proven;
- directs recovery of the exact earlier build procedure instead of rediscovering the fault.

### 9. Op199 resilience record

`docs/audits/HEAVY_ENGINEER8_CLOSEDCODE_RESILIENCE_OP199_2026-09-18.md`

Key value:
- inventories surviving historical qualification binaries;
- preserves the malformed Op199 source edit;
- confirms the live runtime was not replaced.

Important surviving artifact paths recorded there include:

`/data/data/com.termux/files/usr/tmp/he-opencode-op22/build/packages/opencode/dist/opencode-android-arm64-he-op41-nominify/bin/opencode`

`/data/data/com.termux/files/usr/tmp/he-opencode-op22/build/packages/opencode/dist/opencode-android-arm64-he-op43-nosplit/bin/opencode`

`/data/data/com.termux/files/usr/tmp/he-opencode-op22/build/packages/opencode/dist/opencode-android-arm64-he-op45-control-split/bin/opencode`

`/data/data/com.termux/files/usr/tmp/he-opencode-op22/candidates/opencode-1.18.31-bun140`

`/data/data/com.termux/files/usr/tmp/he-opencode-op22/candidates/opencode-1.18.31-bun141`

`/data/data/com.termux/files/usr/tmp/he-opencode-op22/candidates/opencode-bun141-nosplit-repair-op47`

## Primary external reports from this investigation

### 10. Bun issue #42837

`oven-sh/bun#42837` — **Possible Bun 1.4.1 Android/Bionic compile regression with splitting:true**

URL:
https://github.com/oven-sh/bun/issues/42837

This is the clearest external record of the Agent-17-era A/B matrix. It records:
- direct-source PASS under 1.4.0 and 1.4.1;
- 1.4.0 compiled PASS;
- 1.4.1 split compiled FAIL;
- 1.4.1 split + no-minify FAIL;
- 1.4.1 no-split compiled PASS;
- the two qualified artifact hashes above.

### 11. OpenCode issue #49262

`anomalyco/opencode#49262` — **Android/Bionic: Bun 1.4.1 splitting:true causes a.name crash**

URL:
https://github.com/anomalyco/opencode/issues/49262

This is the OpenCode-facing report of the same matrix and reproducer.

## Critical upstream corroborating research

These are not ClosedCode-owned proof, but they materially strengthen or constrain interpretation of the historical result.

### 12. OpenCode #48645

`anomalyco/opencode#48645` — regression in 1.18.30, every prompt crashes in `SystemPrompt.environment`.

URL:
https://github.com/anomalyco/opencode/issues/48645

Most important comment:
https://github.com/anomalyco/opencode/issues/48645#issuecomment-5655294526

That comment contains the deepest upstream bundle archaeology found so far:

- exact regression window 1.18.29 PASS -> 1.18.30 FAIL on macOS;
- same source in the Electron/Node bundle did not crash while the Bun single-file compiled binary did;
- every failing trace was inside `/$bunfs/root/chunk-*.js`;
- the location-service group is assembled as a module-level layer graph;
- the resolver walks `node.dependencies`;
- bundled resolver expression is effectively:

  `resolve: (a) => s.get(a.name) ?? a`

  with `a === undefined`;

- interpretation: one entry in the layer dependency graph is undefined at module-evaluation time;
- a stale/undefined binding from a circular chunk import is proposed as the mechanism;
- net effect: location runtime never boots, `SystemPrompt.environment` throws, and no prompt reaches a model.

This matches HE8 Ops191-192 unusually well and should be read before further source archaeology.

### 13. OpenCode #48803

`anomalyco/opencode#48803` — undefined Effect layer node during `SystemPrompt.environment`.

URL:
https://github.com/anomalyco/opencode/issues/48803

Important because:
- independently identifies Effect/LayerNode graph assembly rather than provider/model logic;
- explicitly interprets `a.name` as an undefined layer node;
- reproduces with plugins, MCP, config, and environment stripped away;
- supports a compiled-runtime graph problem.

### 14. OpenCode #48809

`anomalyco/opencode#48809` — non-empty `references` block crashes Agent.list with the same `a.name` resolver stack.

URL:
https://github.com/anomalyco/opencode/issues/48809

Important because:
- independently validates the references-triggered Agent.state manifestation HE7 encountered;
- empty references passes;
- any non-empty references entry crashes in the affected build;
- the stack again enters the same compiled resolver.

Treat this as a specific trigger/manifestation of the shared failure class, not necessarily the sole root cause.

### 15. OpenCode #48372

`anomalyco/opencode#48372` — clean-home/clean-directory reproduction of the same prompt crash.

URL:
https://github.com/anomalyco/opencode/issues/48372

Important because:
- reports the same resolver stack with a completely clean HOME and work directory;
- rules against assuming user config is always required.

### 16. OpenCode #48811

`anomalyco/opencode#48811` — macOS clean-config reproduction.

URL:
https://github.com/anomalyco/opencode/issues/48811

Important because:
- same `SystemPrompt.environment` failure on macOS arm64;
- further evidence that the underlying bundle failure is not Android-exclusive.

### 17. OpenCode #48965

`anomalyco/opencode#48965` — same stack on macOS 1.18.30.

URL:
https://github.com/anomalyco/opencode/issues/48965

### 18. OpenCode #49158

`anomalyco/opencode#49158` — same `a.name` failure on 1.18.30.

URL:
https://github.com/anomalyco/opencode/issues/49158

### 19. OpenCode #49189

`anomalyco/opencode#49189` — `opencode run` crash in `SystemPrompt.environment`, with isolation across pure/config modes.

URL:
https://github.com/anomalyco/opencode/issues/49189

Important because:
- another exact `resolve -> a.name` stack;
- suggests some manifestations can be data/config dependent, while other reports reproduce with clean configuration.

### 20. OpenCode #49365

`anomalyco/opencode#49365` — NixOS 1.18.30 with the exact `resolve(... a.name)` stack.

URL:
https://github.com/anomalyco/opencode/issues/49365

### 21. OpenCode #49570

`anomalyco/opencode#49570` — NixOS/Linux report with the same resolver/SystemPrompt stack.

URL:
https://github.com/anomalyco/opencode/issues/49570

## Bun maintainer feedback that should not be skipped

Bun issue #42837 has a maintainer/reproduction comment:

https://github.com/oven-sh/bun/issues/42837#issuecomment-5690486924

The maintainer could not reproduce on stock OpenCode 1.18.31 + Bun 1.4.1 on Linux x64 and requested:

1. exact `Bun.build` options and source-tree changes;
2. full non-minified stack with linked/inline sourcemap;
3. the same build targeted at a Linux host target to separate Android runtime from bundler behavior;
4. ideally a small standalone reproducer around the failing module/import graph.

The comment also notes several Bun 1.4.1 import/require interop changes as potentially relevant.

This matters because it prevents overclaiming: our Android/Bionic split/no-split A/B is strong evidence for a workaround and failure boundary, but the universal root cause has not been reduced to a standalone Bun reproducer.

## Interpretation for HE8 / Op200

Heavy Engineer should keep four facts separate:

### A. Proven Android-specific A/B behavior

On the historical reconstructed Android/Bionic tree, changing compiled `splitting:true` to `splitting:false` changed the affected gates from FAIL to PASS while direct source execution remained healthy.

### B. Shared upstream failure signature

The exact `resolve -> a.name` stack and `SystemPrompt.environment` / LayerNode graph failure occurred on other platforms and package builds as well.

### C. References are a real trigger, but not sufficient as the universal explanation

A non-empty references block independently triggers the same resolver failure in affected OpenCode builds. HE7's removal of references plus workspace disposal legitimately repaired that particular Agent.list path. But other clean-config upstream reproductions prove references are not the only way the graph can fail.

### D. Compiled bundle/module graph remains the strongest common layer

The strongest combined evidence points toward a compiled Bun bundle/chunk initialization problem that can leave an undefined node in the location-service/LayerNode dependency graph. The historical Android no-split build avoids the failure. That does not yet prove the exact Bun source defect.

## Recommended pre-Op200 reading order

1. Archived `HEAVY_ENGINEER_HANDOFF_2026-09-15.md`.
2. Bun #42837.
3. OpenCode #49262.
4. OpenCode #48645 comment 5655294526.
5. OpenCode #48803.
6. OpenCode #48809.
7. Current HE8 Op176-195 review.
8. Current HE8 Op198.
9. Current HE8 Op199.
10. Archived Ops53-75 audit only if the exact historical ClosedCode build/reconstruction sequence is needed.

## What is still missing / worth proving

The prior research is already enough to avoid another blind archaeology cycle. Remaining high-value proof, if authorized after the checkpoint, would be:

- verify hashes of the surviving historical no-split and split artifacts against the documented qualified hashes;
- run the historical known-good no-split artifact only in a bounded qualification setting before replacing the live runtime;
- correct the malformed Op199 source edit separately and explicitly;
- recover or reproduce the exact historical build recipe/toolchain only if a fresh build is required;
- if investigating the upstream root cause rather than applying the known workaround, produce a non-minified/sourcemapped compiled reproducer and ideally a minimal Bun import/layer-graph case.

Do not conflate those goals. Shipping a known-good no-split ClosedCode/OpenCode runtime and proving the core coding-agent path is a different task from producing a minimal upstream Bun regression reproducer.
