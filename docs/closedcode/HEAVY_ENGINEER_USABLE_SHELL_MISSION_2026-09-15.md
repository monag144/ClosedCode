# ClosedCode Heavy Engineer Mission — Usable Android Shell

Date: 2026-09-15
Authority: Director
Target repository: `monag144/ClosedCode`
Engineering branch: `closedcode/android-foundation-20260915`

## Governance status

The prior OpenCode Heavy Engineer sequence hit the hard checkpoint at Operation 50. Operations 51–52 remain historically unauthorized and must not be reclassified. The Director now explicitly authorizes continuation beginning with Operation 53. The next hard checkpoint is Operation 75; stop after Op75 and require fresh Director approval before Op76.

Audit approximately every five operations. Preserve historical RED/unauthorized events. Do not delete files or data without explicit authorization. No force pushes, destructive resets, or upstream mutation.

## Mission objective

Repurpose the OpenCode fork into a genuinely usable Android/Termux coding-agent shell called **ClosedCode**. This mission stops before APK packaging. Produce a runnable `closedcode` shell/runtime that can operate alongside the existing OpenCode installation without replacing it.

The product should be Android-first, diagnosable, provider-tolerant, and safe to evolve. Reuse useful OpenCode machinery rather than rewriting the whole agent engine unnecessarily.

## Required starting evidence

Read and treat as current mission context:
- `docs/closedcode/CLOSEDCODE_PROJECT_CHARTER_2026-09-15.md`
- `docs/closedcode/CLOSEDCODE_ANDROID_ROADMAP_2026-09-15.md`
- `docs/closedcode/HEAVY_ENGINEER_HANDOFF_2026-09-15.md`
- this mission document

Also preserve the established finding from the prior reconstruction:
- OpenCode 1.18.31 + Bun 1.4.1 + `splitting:true` on the Android/Bionic compiled path reproduces the internal `a.name` failure.
- Same source under Bun 1.4.1 with `splitting:false` passes the affected server endpoints.
- Direct source execution under Bun 1.4.1 passes.
- Bun 1.4.0 compiled control passes.
- Minification is not required for the defect.
- No OpenCode source patch was required for the known-good no-split candidate.

## Phase A — establish the ClosedCode build

1. Work from the ClosedCode fork and engineering branch, not the upstream OpenCode repository.
2. Reproduce/verify the Android/Bionic build path in the fork.
3. Make the Android build rule explicitly use Bun 1.4.1 with `splitting:false` where required. Keep the workaround target-scoped; do not disable splitting globally unless evidence proves that is necessary.
4. Preserve the MIT license and upstream attribution.
5. Produce a disposable ClosedCode Android/Bionic candidate.
6. Prove `/api/config`, `/api/reference`, and `/api/agent` return HTTP 200 and the original `a.name` exception is absent.

## Phase B — make it a separate usable shell

Create a ClosedCode identity and runtime that can coexist with OpenCode.

Requirements:
- runnable command/binary named `closedcode` if technically practical;
- do not replace `/data/data/com.termux/files/usr/bin/opencode`;
- separate ClosedCode config/data/cache paths from OpenCode wherever practical, e.g. ClosedCode-specific config/data directories or explicit environment overrides;
- separate local server port during qualification so OpenCode and ClosedCode cannot collide;
- startup/version output must clearly identify ClosedCode and its upstream base/version;
- preserve compatibility with existing OpenCode concepts only where useful.

Do not perform broad cosmetic renaming if it risks destabilizing the runtime. Functional identity/isolation matters more than exhaustive string replacement.

## Phase C — provider layer

Qualify NVIDIA first, then GLM/Z.AI.

### NVIDIA gate

Using the existing authorized NVIDIA credential without printing or exposing its value:
- prove provider discovery/configuration;
- prove `nvidia/nemotron-3-super-120b-a12b` receives a real model-backed request through ClosedCode;
- prove selected provider/model equals the actual provider/model used;
- distinguish transient NVIDIA 429/500/502/503/504 overloads from ClosedCode internal failures;
- implement/verify bounded retry with exponential backoff and jitter for transient provider failures;
- no silent paid fallback and no provider substitution.

### GLM gate

After NVIDIA is GREEN, qualify the current GLM/Z.AI route using current provider documentation/configuration rather than assumptions. Add only the compatibility adapter required by evidence. Provider-specific quirks must remain isolated behind a provider boundary rather than leaking into the core agent loop.

Never print API keys, tokens, auth-store contents, or secret-bearing environment values. Logs/diagnostics must sanitize secrets.

## Phase D — diagnostics

ClosedCode must make failures explainable without another archaeology expedition.

For each model request/session where technically available, surface or record safe diagnostics including:
- provider;
- model;
- effective route;
- request stage;
- HTTP/provider status;
- latency;
- retry count;
- fallback status;
- prompt/input token count;
- output/reasoning/cache token counts when returned by the provider;
- tool-call count;
- sanitized error class/message;
- clear boundary between ClosedCode internal failure, tool failure, transport failure, and provider failure.

Do not log prompt contents by default, secrets, hidden chain-of-thought, or credential material.

## Phase E — harmless tool-loop qualification

In a disposable workspace only:
1. Ask the build agent to create a small test file.
2. Read the file back through the agent/tool loop.
3. Modify it once.
4. Verify the exact contents on disk.
5. Prove there was no duplicate/replayed mutation.
6. Verify the model request, tool execution, and result return are all observable in safe diagnostics.

Do not touch `DnD-RP-Bot` production/runtime state during this qualification.

## Phase F — install alongside OpenCode

Only after Phases A–E are GREEN, install or expose ClosedCode as a separate usable Termux command/runtime. This authorization permits an **alongside installation of ClosedCode** so the Director can use it. It does **not** authorize replacing, deleting, or overwriting the existing OpenCode binary/runtime.

Prove:
- `opencode` still resolves to the existing OpenCode installation;
- `closedcode` resolves to the ClosedCode candidate;
- both can report their identities independently;
- ClosedCode can start, reach a provider, and complete the harmless tool-loop test after installation.

## Explicitly out of scope for this mission

- APK packaging or embedding the runtime into an APK;
- replacing/removing the existing OpenCode installation;
- modifying upstream `anomalyco/opencode`;
- broad UI redesign;
- DnD-RP-Bot production changes;
- force push/rebase/history rewrite;
- creating additional Python installations or venvs without a proven dependency conflict;
- Rust/native SDK installation merely as a workaround unless separately authorized.

## Git rules

- Canonical project: `monag144/ClosedCode`.
- Work on `closedcode/android-foundation-20260915` or a focused child branch if justified.
- Normal pushes to the ClosedCode fork are authorized after evidence is captured.
- Do not push to `anomalyco/opencode`.
- Keep commits focused and auditable.
- Document new difficult failure classes in the relevant troubleshooting/error-solution area, correlating error and solution records without duplicating an existing identical class.

## Acceptance criteria

GREEN only when all are true:
1. ClosedCode Android/Bionic build is reproducible from the fork.
2. Android build avoids the Bun 1.4.1 splitting regression with a narrow, documented rule.
3. ClosedCode runs as a separate shell/runtime without replacing OpenCode.
4. `/api/config`, `/api/reference`, `/api/agent` are healthy.
5. NVIDIA/Nemotron completes a real request through ClosedCode.
6. One harmless build-agent file operation completes end-to-end with no duplicate mutation.
7. Safe diagnostics clearly identify provider/model/status/retries/latency/tool boundary.
8. GLM/Z.AI is either GREEN or reduced to a precise provider-specific blocker with evidence and no corruption of the NVIDIA path.
9. Existing OpenCode remains untouched and independently runnable.
10. Worktree/branch/audit evidence is clean enough for Director review.

## Hard-stop rules

- Stop at Operation 75 after completing its audit/checkpoint. No Operation 76 without explicit Director approval.
- Stop earlier if continuing would require replacing/deleting the active OpenCode runtime, exposing credentials, destructive recovery, or materially exceeding this mission.

## Final report format

STATUS: GREEN / YELLOW / RED
OPS USED: 53–XX
CLOSEDCODE BUILD:
ANDROID SPLITTING FIX:
NVIDIA:
GLM:
TOOL LOOP:
DIAGNOSTICS:
INSTALLATION:
OPEN CODE PRESERVATION:
GIT/COMMITS:
REMAINING DEFECTS:
NEXT DIRECTOR DECISION:
