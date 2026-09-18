# HE8 Operation Resilience — Op191

Status: GREEN / read-only LayerNode trace
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP191.layernode-name-dereference-trace
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Local HEAD before/after: 6452767b80d69223a6f64fd633ffae7adf735cd2
Local worktree before/after: clean
Mutation: none

Purpose: inspect LayerNode hoist/compile/replacement logic for .name dereferences that could match the observed minified TypeError.

Findings:
- LayerNode.Node requires a string name.
- make() derives name from service.key or input.name; unbound() derives name from service.key; group() uses literal "group".
- Hoist/compile/replacement processing dereferences node.name/source.name/replacementNode.name repeatedly.
- AppNodeBuilder.hasReplacement() also compares source.name with node.name.
- buildLocationServiceMap() injects Location.boundNode(ref) through replacements and hoists the complete locationServices graph before compiling it.
- Therefore the minified a.name failure is not uniquely attributable to SystemPrompt.environment reference sorting; graph-construction/replacement resolution is a credible alternative.
- No malformed LayerNode was proven in this operation.
- Exact failing dereference still requires stack/runtime evidence.

Next:
Use a tightly bounded read-only capture of the original TypeError stack/runtime evidence from prior HE8 diagnostics/runtime logs. Correlate stack frames to source before any product mutation.

No product source, runtime, Relay, APK, Git working tree, or shared storage changed.
