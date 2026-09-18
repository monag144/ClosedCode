# HE8 Operation Resilience — Op190

Status: GREEN / read-only location-service trace
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP190.bounded-location-service-map-trace
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Local HEAD before/after: 6452767b80d69223a6f64fd633ffae7adf735cd2
Local worktree before/after: clean
Mutation: none

Purpose: inspect LocationServiceMap construction and the exact Agent/SystemPrompt reference provisioning paths.

Findings:
- LocationServiceMap.Service wraps a LayerMap keyed by Location.Ref.
- buildLocationServiceMap() constructs a fresh location-scoped graph from locationServices and injects Location.boundNode(ref) as a replacement.
- locationServices includes Reference.node.
- Both Agent and SystemPrompt resolve references through locations.get(Location.Ref.make({ directory: AbsolutePath.make(ctx.directory) })).
- Agent has one notable extra synchronization step: it waits for PluginV2 ID core/config-reference before calling Reference.Service.list().
- SystemPrompt.environment does not wait for that plugin.
- The missing wait can plausibly cause stale or empty reference state, but it does not by itself explain an undefined reference.name because normal Reference.Info construction requires name.
- Therefore the exact minified a.name failure may come from a different .name dereference in graph construction/provisioning rather than session/system.ts line 92.

Next:
Inspect the bounded LayerNode hoist/compile/replacement path and any .name dereferences exercised while locations.get(...) builds the location graph. No product mutation until the exact failure site is proved.

No product source, runtime, Relay, APK, Git working tree, or shared storage changed.
