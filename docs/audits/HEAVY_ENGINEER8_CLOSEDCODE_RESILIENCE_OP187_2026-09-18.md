# HE8 Operation Resilience — Op187

Status: YELLOW / partial read-only diagnostic
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP187.direct-session-system-trace
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
HEAD before/after: 6452767b80d69223a6f64fd633ffae7adf735cd2
Worktree before/after: clean
Mutation: none

Purpose: inspect SystemPrompt.environment directly and trace the undefined .name failure.

Findings:
- packages/opencode/src/session/system.ts was successfully printed.
- SystemPrompt.environment is implemented at lines 69-105.
- Project references are loaded at line 72 and filtered only on description != undefined.
- The strongest current crash candidate is line 92:
  .toSorted((a, b) => a.name.localeCompare(b.name))
- If any returned reference lacks name, this directly matches the observed TypeError involving a.name.
- Additional intended searches did not execute because rg is not installed in the Termux environment.
- Therefore the exact producer/schema/caller chain is not yet proven.

Classification:
- Partial success because the likely dereference was found, but the complete trace was not completed.
- No product, runtime, Relay, APK, Git, or shared-storage mutation occurred.

Next:
- Use available grep/find tools, not rg.
- Inspect Reference.Service list implementation/schema and actual reference objects.
- Confirm whether nameless references are possible and whether the correct ClosedCode fix belongs at reference normalization or SystemPrompt.environment.
