# ClosedCode Heavy Engineer Handoff — 2026-09-15

## Mission identity
The project has moved from repairing an installed OpenCode runtime to establishing an independent downstream fork: `monag144/ClosedCode`.

Canonical engineering branch for the first ClosedCode Android work:
`closedcode/android-foundation-20260915`

Upstream remains `anomalyco/opencode` and the fork preserves the MIT license and provenance.

## Known technical result carried forward
The prior OpenCode 1.18.31 Android/Bionic investigation established a controlled A/B boundary:
- direct source execution under Bun 1.4.0: PASS
- direct source execution under Bun 1.4.1: PASS
- Bun 1.4.0 compiled Android/Bionic candidate: PASS
- Bun 1.4.1 compiled with `splitting:true`: FAIL (`/api/reference` and `/api/agent` HTTP 500, `a.name` dereference)
- Bun 1.4.1 compiled with `minify:false, splitting:true`: FAIL
- Bun 1.4.1 compiled with `splitting:false`: PASS
- fresh Bun 1.4.1 normal splitting control reproduced failure

Known-good no-split artifact from the repair investigation:
- SHA256 `02367cb9fa073ab37acadd6d4ca35db590f7fd4c775147541104ec604fee6e4e`
- 188,614,920 bytes

Bun 1.4.0 compiled control:
- SHA256 `26c7610ef19d4982dbd72ed3db7663813543bfcaf4d99834665df1f365bb9905`

No OpenCode source patch was required for the no-split repair.

## First ClosedCode mission
Reproduce the Android/Bionic baseline directly from the fork branch and turn the previous ad-hoc repair into a reproducible ClosedCode build rule.

### Required sequence
1. Clone/fetch `monag144/ClosedCode` without modifying the installed OpenCode runtime.
2. Checkout `closedcode/android-foundation-20260915`.
3. Identify the current upstream build flags responsible for Bun compile splitting.
4. Add the narrowest Android-specific build control necessary to produce a Bun 1.4.1 `splitting:false` candidate while preserving non-Android behavior unless evidence requires otherwise.
5. Build a disposable ClosedCode candidate.
6. Prove `/api/config`, `/api/reference`, and `/api/agent` HTTP 200.
7. Preserve artifact hash, size, Bun version, source HEAD, dependency identity, and build command.
8. Do not install or replace the active OpenCode runtime.

## Second mission after baseline GREEN
Qualify NVIDIA / Nemotron through ClosedCode:
- discover/load credential without printing the value
- provider/model discovery
- `build` agent request to `nvidia/nemotron-3-super-120b-a12b`
- real response
- one harmless tool operation
- separate internal-runtime failures from provider 429/5xx overload behavior

Then begin Z.AI / GLM qualification.

## Diagnostics requirement
ClosedCode should make failures attributable to a layer. Prefer adding instrumentation that can safely identify:
- client/UI
- local runtime/server
- provider adapter
- remote provider HTTP
- model parse/stream
- tool dispatch
- local execution

Never log credentials.

## Governance
- Hard checkpoint every 25 Heavy Engineer operations.
- No operation after a hard checkpoint without explicit Director continuation approval.
- Historical unauthorized operations remain historically unauthorized.
- No destructive Git operations.
- No active-runtime replacement/install/restart without explicit Director approval.
- No secret values in output, Git, telemetry, docs, or logs.
- Use timestamped audits; do not create mutable CURRENT/LIVE authority documents.

## Relevant ClosedCode docs
- `docs/closedcode/CLOSEDCODE_PROJECT_CHARTER_2026-09-15.md`
- `docs/closedcode/CLOSEDCODE_ANDROID_ROADMAP_2026-09-15.md`

## Definition of first GREEN
A reproducible ClosedCode Android/Bionic build from the fork succeeds under Bun 1.4.1 with the splitting regression contained, passes config/reference/agent endpoints, and does so without touching the active installed OpenCode runtime.
