# ERR-CC-BACKEND-002 — OpenCode references config crashes Agent.state on native 1.18.31

**Tag:** `CC-OPENCODE-REFERENCES-AGENT-STATE-CRASH`  
**Status:** CONFIRMED  
**Date:** 2026-09-18  
**First isolated by:** HEAVY ENGINEER 7, Operations 164–166

## Signature

The ClosedCode workspace returned HTTP 500 from:

`GET /agent?directory=/data/data/com.termux/files/home/ClosedCode`

while the same native OpenCode 1.18.31 backend returned HTTP 200 for `$HOME`.

Backend logs repeatedly reported:

`TypeError: undefined is not an object (evaluating 'a.name')`

inside `Agent.state`.

## Isolation

Disposable literal-valid-JSON cases proved:

- baseline config: 200
- empty provider: 200
- empty permission: 200
- empty mcp: 200
- existing tools block: 200
- local-path reference alone: 500
- git repository reference alone: 500
- both references: 500
- full project config with references removed: 200
- full project config with references retained but tools removed: 500
- real ClosedCode workspace: 500

Therefore the failing feature is the non-empty `references` config block itself on this native Android/Termux OpenCode 1.18.31 runtime.

## Impact

Because `Agent.state` fails, both live agent discovery and prompt creation can fail for the ClosedCode workspace even though provider, session, config, and global health endpoints remain operational.

## Safety

Do not disable or rewrite unrelated provider, permission, mcp, tools, plugin, or custom-agent configuration to recover this failure. Do not mutate GPT-Termux-Relay.