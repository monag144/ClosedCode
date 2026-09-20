# ClosedCode 0.8.14 — Token Usage Telemetry

Timestamp UTC: `2026-09-20T20:09:45Z`
Heavy Engineer: **10**

## Result

**GREEN — exact provider-reported per-request token telemetry is live-qualified.**

ClosedCode 0.8.14 accumulates provider-reported usage across agent provider rounds and emits it on the terminal `complete` event. The Marathon harness propagates the same object to status/summary and prints token totals at completion.

Live NVIDIA qualification during Op426 reported:

- prompt tokens: **3256**
- completion tokens: **89**
- total tokens: **3345**
- provider rounds: **2**
- reported rounds: **2**
- exact coverage: **YES**

The harness completion surface now prints `TOKENS_USED_PROMPT`, `TOKENS_USED_COMPLETION`, `TOKENS_USED_TOTAL`, round coverage, and `TOKEN_USAGE_EXACT`.

Historical 0.8.13 operations did not persist provider usage, so exact historical totals are intentionally reported as unavailable rather than estimated from characters.

Scope: these counters measure ClosedCode provider-model usage. They do not represent ChatGPT conversation tokens or ordinary shell execution.
