# Heavy Engineer 8 ClosedCode Audit — Ops188-192

Mission: ClosedCode stabilization
Anchor: Op175 hard checkpoint
Repository: /data/data/com.termux/files/home/ClosedCode
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
Closing local HEAD: 6452767b80d69223a6f64fd633ffae7adf735cd2
Closing worktree: clean
Protected infrastructure: no GPT-Termux-Relay implementation mutation established

## Operations

Op188 — GREEN / read-only. Traced Reference.Service materialization. Normal materialization always constructs Reference.Info with a name from the string map key. This weakened the theory that an ordinary reference naturally lacks name.

Op189 — YELLOW / partial read-only. Proved canonical Reference.Info.name is required Schema.String and config aliases are validated. Broad LocationServiceMap output truncated before complete implementation capture. Stronger hypotheses became location-scoped service/provisioning mismatch or alternate graph path.

Op190 — GREEN / read-only. Bounded LocationServiceMap trace showed locationServices includes Reference.node and builds a fresh location-scoped graph with Location.boundNode(ref). Agent and SystemPrompt use the same locations.get(Location.Ref(...)) path. Agent additionally waits for core/config-reference; SystemPrompt does not. That asymmetry can explain stale/empty references but not an undefined name by itself.

Op191 — GREEN / read-only. LayerNode source contains many .name dereferences in replacement, hoist, compile, walk-cycle reporting, and resolution. Therefore the minified a.name failure is not uniquely attributable to reference sorting. Shared graph resolution became a credible root-cause area.

Op192 — YELLOW / partial read-only. Runtime log correlation found repeated TypeError undefined is not an object (evaluating 'a.name') with common first frame resolve in chunk-cc8ps5vb.js:2:1659. The same resolver stack occurs under SystemPrompt.environment, Agent.state, and Server.listen, strongly indicating a shared lower-level graph resolver failure rather than caller-specific reference sorting. Broad filesystem output truncated the tail.

## Window conclusion

Window mutations: none.
Protected state: no protected Relay implementation mutation.
Historical failures preserved: Op189 and Op192 remain partial due output truncation; no earlier RED is rewritten.
Current blocker: identify the source provenance of chunk-cc8ps5vb.js / resolve or directly reproduce the shared LayerNode resolver failure against the current graph.
Invalidated assumption: the working assumption that session/system.ts reference sorting was the likely direct crash site is no longer favored by evidence.
Roadmap: still within stabilization; no feature expansion.
Governance: required five-operation audit completed. Director-mandated review gate remains Operation 195. Operation Resilience per-operation GitHub logging remains active.
