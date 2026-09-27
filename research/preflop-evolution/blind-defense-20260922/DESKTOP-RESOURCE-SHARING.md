# Research scheduling: light desktop use is allowed

On 2026-09-28 the user selected: "Share with light desktop use (Recommended)".
Research may share the GPU with light browser/video activity while active
GTOpen solves and heavier user workloads retain priority. Future study starts
should assess available compute and VRAM instead of requiring the entire GPU
to be almost idle simply because a browser is playing video. Any change to a
registered study's admission implementation must be explicit and qualified;
never alter reported measurements to make an old guard pass.

For the currently registered board-root evaluation, the second admission
attempt passed the original start check at approximately 08:25 Adelaide while
the scheduling change was being prepared. The existing run was preserved.
Its source code, random sequence, stopping rule and numerical calculation were
not changed to broaden admission. The live run permits concurrent desktop use
under its existing memory, production-activity and storage guards. This note
does not claim that the old 10% startup threshold was changed.

The attempted handoff was conservative: the first inspection resumed both
identified workers when their console-helper process was not in the initial
allowlist. A second inspection detected that scientific admission had begun
and also resumed the workers without terminating them. The saved 17,408-deal
checkpoint and original attempt evidence remain intact.

The current worker is PID 79620 (creation time 1790548221.8679416), launched by
queue PID 64588. Its admitted attempt is
`board-evaluation-resource-wrapper-v1-status-recovery2-02-registration.json`.
These are historical identities; verify live processes and new committed
checkpoints before reporting that evaluation is progressing.
