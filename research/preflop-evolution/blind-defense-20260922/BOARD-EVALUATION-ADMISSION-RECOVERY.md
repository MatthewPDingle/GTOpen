# Preserving evaluation through pre-start GPU admission changes

The first status-recovery queue reached its child at 07:53:50 Adelaide on
2026-09-28. The frozen evaluation driver then rejected GPU admission at line
110 (`utilization < 10 and free > 6000`). GPU activity had changed between the
queue's resource check and the driver's check. This attempt performed zero
inventory scans and stopped before research-lock acquisition, bank loading,
archive creation or drawing test deals. Its registration, failure and traceback
remain preserved. The original 17,408-deal checkpoint was reverified unchanged.

Version 2 retains every original resource threshold and the qualified bounded
status-publication fix. Before each admission attempt it waits for four
successive resource checks to pass. It may defer only an AssertionError whose
deepest traceback is the exact pre-lock GPU assertion in the unchanged driver.
Deferral additionally requires a hash-bound wrapper failure with zero inventory
scans, restored status dependency, no research locks, unchanged checkpoint and
archive-directory sets, and no completed scientific result. Each attempt has a
distinct registration and failure record. Eight admission attempts and the
existing bounded invocation times limit retries. Other errors remain terminal.

Synthetic controls accepted that exact pre-lock rejection, rejected six other
error cases, verified a single successful invocation after deferral, and checked
the retry limit. These are operational tests, not new poker observations.

The version-2 queue was launched hidden as PID 64588 at 07:59:02 Adelaide.
This is a historical launch identity, not a continuing liveness claim. It will
run the fixed evaluation, the existing all-batch readback, and the prepared
report. Interpretation and visual review remain outstanding. No production
build or model was changed, and no partial scientific outcomes were inspected.

The final report already labels its evaluation duration as the final invocation
only. Report interpretation must also account for the interrupted initial
2,206.812-second wrapper and resource-wait/recovery time; these are not improved
training throughput and should not disappear into a speed claim.

Evidence: `board-admission-deferral-control-v1-result.json`,
`board-status-recovery-v2-registration.json`, the preserved
`board-evaluation-resource-wrapper-v1-status-recovery1-failure.json`, and
`board-status-recovery-v1-evaluation.log`. Successful admission will retain its
own resource-wrapper evidence and the encompassing
`board-admission-status-recovery-v1-result.json`.
