# Heavy Engineer 7 — ClosedCode Audit Operations 161–165

Date: 2026-09-18

## Scope

This audit closes the five-operation window from Operation 161 through Operation 165.

## Results

- **Op161 — GREEN.** Recovered the ClosedCode backend with the already-installed native OpenCode executable at `/data/data/com.termux/files/usr/bin/opencode` version `1.18.31`. `/global/health` returned healthy and the v0.1.4 installer handoff succeeded.
- **Op162 — GREEN.** Rewired the Director-provided artwork as a proper Android adaptive launcher icon using `@mipmap/ic_launcher` / `@mipmap/ic_launcher_round`, built `0.1.5-cleanroom`, verified adaptive-icon resources in the APK, kept the backend healthy, and presented the installer.
- **Op163 — RED/PARTIAL.** The OpenCode composer interaction-map documentation fast-forward succeeded and backend health was GREEN, but the first live composer contract capture failed because `GET /agent?directory=<ClosedCode>` returned HTTP 500.
- **Op164 attempt 1 — PACKET_REJECTED.** Invalid `command_b64`; shell did not run.
- **Op164 attempt 2 — PACKET_REJECTED.** Invalid `command_b64`; shell did not run.
- **Op164 attempt 3 — GREEN / read-only.** Proved `/agent` returns HTTP 500 only for the ClosedCode workspace while the same backend returns HTTP 200 for `$HOME`. `/provider`, `/session`, and `/config` all return HTTP 200 for ClosedCode. Backend logs show `TypeError: undefined is not an object (evaluating 'a.name')` inside `Agent.state`.
- **Op165 — PARTIAL despite wrapper exit 0.** Disposable isolation proved the repo agent markdown alone returns HTTP 200, the repo TUI plugin alone returns HTTP 200, the original project `.opencode/opencode.jsonc` alone returns HTTP 500, and full workspace copies still fail when either the plugin or agent directory is removed. Two intended subfixtures (`config_norefs` and `refs_only`) were generated with Python `json.load` against JSONC containing trailing commas and therefore failed with `JSONDecodeError`; their subsequent HTTP results are not admissible evidence.

## Current accepted fault boundary

The failure is in the **workspace project-config path**, not in the checked-in custom agent markdown and not in the checked-in TUI plugin by themselves.

Trusted evidence:

- empty disposable workspace: `/agent` 200
- checked-in agents only: `/agent` 200
- checked-in TUI plugin only: `/agent` 200
- original `.opencode/opencode.jsonc` only: `/agent` 500
- full workspace without plugin: `/agent` 500
- full workspace without agents: `/agent` 500

The exact project-config key responsible is not yet proved.

## Governance

- Production ClosedCode workspace mutation during Op165: **NONE**
- Op165 mutations were confined to disposable temporary directories removed at exit.
- GPT-Termux-Relay mutation during Ops161–165: **NONE**
- Historical RED/PARTIAL events remain RED/PARTIAL.

## Next bounded work

Bisect the project config using literal valid JSON fixtures rather than attempting to parse JSONC with Python's standard JSON parser. Test `references`, `tools`, `provider`, `permission`, and `mcp` independently and in the combinations present in the checked-in config. Only after the exact failing feature is proved should the smallest compatible repair be selected.
