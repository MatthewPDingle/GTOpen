# Evaluation recovery after Windows progress-file contention

On 2026-09-28 at 07:34 Adelaide, the first fixed board-root evaluation stopped
when Windows rejected replacement of its mutable progress JSON (WinError 5).
The exception handler encountered the same publication error. The original
wrapper and follow-up queue exited; both scientific research locks were absent.
The traceback identifies progress publication, not a failed numerical check.
The exact process holding the target file was not established.

The committed checkpoint contains 17,408 of the registered 65,536 deals.
Recovery verified its SHA-256, all 544 routed archives and their manifests,
receipts and owner identities, plus replay of the original seed 9281101 to
exactly the checkpoint's random-generator state. No partial payoff or
range-comparison result was inspected. The original attempt, failure logs,
unpublished status files and any uncommitted batch remain preserved.

## Operational change and qualification

`windows_progress_publication_v1.py` supplies atomic publication for mutable
status files only. Windows errors 5, 32 and 33 retry at 50 ms intervals for at
most five seconds. Other errors propagate immediately; persistent denial still
fails and retains the unpublished temporary file. The scoped override restores
the original status function on success and failure. It changes no registered
numerical code, policy, precision, chance sample, stopping rule or resource limit.

The synthetic Windows control passed a real open-handle collision, persistent
denial with a bounded timeout, unrelated-error propagation, scope restoration
and rejection of non-status destinations. Even a reader requesting delete
sharing prevented replacement on this machine until its handle closed; recovery
after that reader closed also passed. Monitoring now reads append-only logs and
immutable checkpoint filenames, avoiding live reads of mutable status JSON.

The first synthetic control attempt exposed that delete-sharing limitation and
failed before publishing qualification. The revised qualification made no
assumption that delete sharing guarantees replacement. Its successful result
binds the exact new helper, control and recovery runner files.

## Remaining stages

`board_status_recovery_v1.py` is a single explicit recovery attempt. The recovery
queue was launched hidden as PID 77652 at 07:45:15 Adelaide. This is a launch
snapshot, not continuing proof of liveness. It first waits for the existing
resource/production-idle gates, then invokes the unchanged resource wrapper
with `--resume` and the distinct attempt name `status-recovery1`, applying only
the qualified status override. The frozen scientific driver repeats source,
storage, archive and sampler checks before continuing.

The remaining sequence is evaluation, all-batch readback, then the prepared
all-outcomes report. There are no automatic retries of a failed stage. Visual
review and scientific interpretation still follow the report; no model is
promoted or deployed by this recovery.

Evidence: `windows-progress-publication-control-v1-result.json`,
`board-status-recovery-v1-registration.json`, and the preserved original
`board-evaluation-resource-wrapper-v1-initial-failure.json` /
`board-full-followup-queue-v1-failure.json` and evaluation traceback log.
