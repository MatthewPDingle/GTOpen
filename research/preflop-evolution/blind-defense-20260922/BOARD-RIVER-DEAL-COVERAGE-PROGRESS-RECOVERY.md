# Coverage study: recover a transient Windows progress-file lock

The first collection reached 114 published progress cases, then terminated
with Windows access denied while replacing its mutable progress JSON. Archive
workers finished their already queued work; the exact retained case count is
independently enumerated and checked in the recovery registration. Collection
session 32008 and pipeline session 83018 both returned exit code 1. Their
failure records and partial files remain preserved. They are not live jobs.

Windows readers can deny replacement while holding a file handle without
delete sharing. Progress updates must tolerate this. The new helper retries
only PermissionError at final progress replacement, retaining the already
flushed temporary file on persistent denial. After bounded retries it reports
deferred progress and lets scientific work continue. Serialization, flush,
disk-full, unrelated IO errors and durable completion failures remain fatal.
The helper refuses paths that are not progress-status JSON files.

The new recovery launcher first verifies every completed archive against its
manifest and original selected case/registration. It then calls the unchanged
registered v2 collector in its existing resume mode, replacing only status().
No deals, targets, sources, original registrations, archived cases, model
settings, resource guards or scientific gates are changed. The execution
adapter and all completed-case hashes receive a separate registration.

Independent controls inject both transient/persistent replacement failure and
disk-full errors, reject completion filenames, and exercise real Windows
read handles that block replacement. Previous progress and unpublished pending
progress are both preserved during a persistent lock; releasing a real handle
permits the same atomic write to finish. See the control result.

Pipeline v2 waits for the recovery process, requires its successful proof, and
uses a new registration/status/log directory. The original pipeline evidence
is retained. It performs the same fixed readback, merge, 48 fits, evaluation
and independent reporting sequence; only progress publication is tolerant.

No production state, historical archive or experiment design was changed.
