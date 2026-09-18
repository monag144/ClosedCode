# HE8 Operation Resilience — Op180

Status: GREEN / read-only diagnostic
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP180.systemprompt-name-deref-archaeology
Branch: closedcode/android-cleanroom-opencode-mobile-20260916
HEAD: 6452767b80d69223a6f64fd633ffae7adf735cd2
Worktree before/after: clean
Mutation: none

Findings:
- No literal SystemPrompt.environment(...) call site was found by the initial grep strategy.
- The environment hook declaration exists at packages/opencode/src/session/system.ts:54.
- Broad project/workspace/location .name searches were noisy and did not isolate the failing dereference.
- The next correct diagnostic is a direct bounded inspection of session/system.ts and its actual callers, after governance recovery is complete.
