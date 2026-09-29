# HE8 Operation Resilience — Op199

Status: YELLOW / partial mutation
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP199.apply-proven-nonsplit-build-fix
Relay status: OK
Exit code: 0
Branch: closedcode/android-cleanroom-opencode-mobile-20260916

Purpose:
Apply the historically proven non-splitting runtime-build fix, commit/push it, and inventory surviving runtime artifacts without replacing the live runtime unless a verified artifact exists.

Pre/reconciliation:
- Local checkout fast-forwarded from cefdd5a47be570a07884858940c4deda8de32ccd to c361a73130cef1a05d18261ba628fbd19e70feae, incorporating governance/docs only.
- Worktree was clean before mutation.

Mutation:
- packages/opencode/script/build.ts was edited.
- Commit created and pushed:
  0a1331f6b0560663df57cdbbe0420a38153b3b8b
  fix(opencode): disable compiled code splitting
- Final worktree was clean.
- Protected GPT-Termux-Relay implementation was not mutated.
- Live /data/data/com.termux/files/usr/bin/opencode runtime was not replaced.

Critical verification defect:
A post-operation GitHub read proved the committed source contains literal backslash-n sequences inside the inserted // comment:

    // ClosedCode Android/Bionic qualification: Bun 1.4.1 with splitting:true reproduced\n    // the internal reference/agent failure; the same source with splitting:false passed.\n    splitting: false,

Because this is one physical source line beginning with //, the intended splitting:false token is inside the comment and is not an active object property. Therefore Op199 did not correctly establish the intended explicit non-splitting build configuration and must not be classified GREEN.

The resulting Bun.build call appears to omit the splitting property rather than explicitly set it false. No assumption is made here about the runtime default; explicit qualification remains required.

Compiler state:
- bun and bunx were not available on PATH.

Surviving runtime artifacts discovered:
- /data/data/com.termux/files/usr/tmp/he-opencode-op22/build/packages/opencode/dist/opencode-android-arm64/bin/opencode
- /data/data/com.termux/files/usr/tmp/he-opencode-op22/build/packages/opencode/dist/opencode-android-arm64-he-op41-nominify/bin/opencode
- /data/data/com.termux/files/usr/tmp/he-opencode-op22/build/packages/opencode/dist/opencode-android-arm64-he-op43-nosplit/bin/opencode
- /data/data/com.termux/files/usr/tmp/he-opencode-op22/build/packages/opencode/dist/opencode-android-arm64-he-op45-control-split/bin/opencode
- /data/data/com.termux/files/usr/tmp/he-opencode-op22/candidates/opencode-1.18.31-bun140
- /data/data/com.termux/files/usr/tmp/he-opencode-op22/candidates/opencode-1.18.31-bun141
- /data/data/com.termux/files/usr/tmp/he-opencode-op22/candidates/opencode-bun141-nosplit-repair-op47

Installed live runtime remained:
- /data/data/com.termux/files/usr/bin/opencode
- version 1.18.31
- SHA256 3d082b4a3e75346de3a516d63a2e84cb812761478c9d97da65bedbac13c14b32

Disposition:
- Preserve Op199 as YELLOW/PARTIAL.
- Do not rewrite the history of the malformed source edit.
- Op200 is the terminal campaign checkpoint and Director-designated information point.
- Do not consume Op200 until the Director supplies the promised information.
- At Op200, first re-read Relay procedure, Heavy Engineer Control Harness, and ClosedCode Stabilization Roadmap, then reconcile/fix the malformed explicit setting as appropriate and evaluate the surviving no-split artifact evidence under checkpoint rules.
