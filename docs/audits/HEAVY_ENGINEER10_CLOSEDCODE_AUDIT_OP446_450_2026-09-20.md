# Heavy Engineer 10 — ClosedCode Audit Ops446–450 + Checkpoint Recovery

Timestamp UTC: `2026-09-20T22:12:58Z`
Audit window: **Ops446–450 exactly**
Checkpoint 450: **reached; initial checkpoint operation failed; Director explicitly released checkpoint before Op451 recovery**

## Operation ledger

### Op446 — RED — OpenCode 4096 startup failure
The installed Android ARM64 `opencode 1.18.31` executable exited from `serve --hostname 127.0.0.1 --port 4096` with `ServeError`. No repository mutation occurred.

### Op447 — RED — pure mode did not cure ServeError
Normal and `--pure` startup both loaded configuration and then failed with `ServeError`. External plugins were therefore not supported as the root cause. No repository mutation occurred.

### Op448 — RED — ambiguous EADDRINUSE probe
Launcher discovery confirmed an Android ARM64 OpenCode ELF plus the repository Node launcher. A Python bind probe then returned `EADDRINUSE` before alternate startup testing. Op449 subsequently found no LISTEN inode on 4096, so Op448 did not prove a stable service. No repository mutation occurred.

### Op449 — TIMEOUT / UNKNOWN-RED-UNPROVEN
The operation reported `PORT4096_LISTEN_INODES=NONE`, then attempted alternate-port startup, loopback proxy recovery, ZAI acceptance, Android regressions, RC packaging, and certification. The Relay timed out at 295 seconds before additional evidence returned. Historical status remains **TIMEOUT / UNKNOWN-RED-UNPROVEN**.

Op451 reconstruction found remote HEAD still `d49f17b6cb76954f0a7a5fb3e7d979516ab57f3f`. A late local certificate commit was found/uncommitted: **NO**. Late certificate state: **ABSENT**, SHA-256 `NONE`. Late RC state: **ABSENT**, bytes **0**, SHA-256 `NONE`. Late SHA-file state: **ABSENT**. These artifacts are preserved only as evidence and are not accepted as Op449 success. Current 4096 catalog state: **OFFLINE**. Backend 4097 remains **0.8.15 GREEN**. Transcript and integrated-UI regression checkers remain GREEN.

### Op450 — RED — checkpoint recovery guard self-terminated
Op450 attempted to freeze an exact Op449 shell by matching strings embedded in process argv. Because the current Op450 shell itself contained those historical strings as script data, the guard selected and SIGTERM'd its own PID. Exit status was **-15**. Reconstruction, audit creation, commit, and checkpoint certification therefore never ran. This is a harness/process-identification defect, not product evidence.

## Checkpoint assessment

Accepted product source remains `0d575ec144638a534019b16811d8990599668626`; the pre-recovery documentation baseline is `d49f17b6cb76954f0a7a5fb3e7d979516ab57f3f`. NVIDIA real coding-agent acceptance from Op442 remains GREEN. Backend 4097, transcript regression, persisted activity/readable progress source checks, and integrated Android UI regression remain GREEN.

The unresolved release gate is the Android-facing 4096/OpenCode runtime path plus fresh ZAI/RC certification. Repeated blind 4096 restarts are not justified. Future process recovery must use structural process identity or concrete artifact paths, never historical strings embedded in a shell command.

Checkpoint 450 was reached and stopped further work. The Director explicitly released it before Op451. This audit repairs the missing governance record; it does not retroactively convert Op450 to GREEN.
