# Heavy Engineer 10 — ClosedCode Audit Ops436–440

Timestamp UTC: `2026-09-20T21:00:39Z`
Window: **Ops436–440 exactly**
Director target: integrated Android/backend/provider/tools regression, repairing only defects actually exposed before the Op440 audit boundary.

## Operation ledger

### Op436 — RED — false-positive Marathon guard
The transcript repair stopped before mutation because its runner check counted the checker process itself: the harness path appeared as an argument to `python -`, not as the executed Marathon script. No repository or runtime mutation occurred.

### Op437 — GREEN — transcript repair and first integrated smoke
Corrected the process predicate and deliberately completed the Android transcript repair. The optimistic first user message is protected from destructive asynchronous reloads during passthrough startup/streaming, and the assistant response card is now created lazily on the first actual content delta so preceding tool events retain causal visual order. In-band error/cancel semantics were also tightened.

Added `apps/closedcode-android/tools/check-transcript-regression.py`; source regression and real Termux Android build passed. A live NVIDIA `/agent` mission completed one `workspace_read` with zero permissions/errors, final marker `INTEGRATED_SMOKE_GREEN`, and exact provider token accounting: 3250 prompt + 91 completion = 3341 total across 2/2 reported rounds. Commit `9ac977975b19b4aac195311226d2edd0b1c96ce8` was pushed and the worktree ended clean.

### Op438 — GREEN — integrated persistence/Android behavior regression
A second live NVIDIA mission proved tool completion precedes final assistant prose and that passthrough text history persists exactly one user and one assistant message in order with no duplicates. Android transcript regression and build stayed GREEN.

The regression exposed four concrete defects:

1. **Completion alerts unwired** — the existing `notifyCompleted` setting has no Notification/Ringtone implementation path.
2. **Android 13+ notification permission missing** — manifest lacks `POST_NOTIFICATIONS`.
3. **Reopen loses tool cards** — backend history persists only user/assistant text, so live structured tool events cannot be reconstructed after reopening.
4. **Progress presentation raw-only** — tool cards expose raw tool/status/detail without a local human-readable projection.

No speculative repair was performed in Op438. Exact token usage was 3247 prompt + 105 completion = 3352 total across 2/2 reported rounds.

### Op439 — PACKET_REJECTED — Relay command-size violation
The intended bounded repair packet was rejected by the GPT-Termux Relay before execution because the command exceeded 20,000 characters. No Termux shell command ran; therefore no repository, backend, Android, or protected Relay mutation occurred. The four Op438 defects remain open. This operation is consumed and remains historically PACKET_REJECTED.

### Op440 — GREEN — mandatory audit
Revalidated the committed transcript regression checker, rebuilt the actual Android client, confirmed the repository remained clean, and confirmed ClosedCode backend 0.8.14 plus protected GPT-Termux-Relay remain healthy. This audit itself introduces no product change.

## Audit assessment

The transcript race/chronology repair is accepted at source-regression/build/live-backend-smoke level. Op438 then successfully shifted the mission from speculative Android work to evidence-driven integration findings.

The four exposed Op438 defects are the only authorized immediate repair set. Op439 failed operationally before execution, so none of those defects may be represented as fixed yet.

Schedule recovery target after this audit:

- **Op441:** compact repair of the four exposed integration defects, with packet size held below Relay limits.
- **Ops442–444:** real coding-agent acceptance followed by RC Android build/package/hash, combining checks where safe.
- **Op445:** mandatory five-operation audit plus Director-requested formal review.
- **Op450:** universal hard checkpoint.

Protected GPT-Termux-Relay source/config remains untouched. No APK installation occurred.
