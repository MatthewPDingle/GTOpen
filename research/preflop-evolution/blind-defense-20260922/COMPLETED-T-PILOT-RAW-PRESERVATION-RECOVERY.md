# Resume lossless preservation after the activity-check failure

The six-copy version-1 compression control and its independent readback passed.
The original-file attempt then rejected its own `compact.exe` children as
active historical owners because their command lines contained the admitted
paths. It stopped and retained the evidence; no successful batch journal or
final result was published. Some files may have completed compression before
the stop. Do not assume that the failed attempt changed no physical allocation.

Version 2 exempts only a direct child of the current controller whose executable
is the exact Windows System32 `compact.exe` and whose command starts `/C /Q`.
Other processes, including another compact process with those paths, remain
subject to the owner-liveness rejection. Verify this distinction explicitly.

Preserve version 1's source, manifest, registration and interrupted status.
Before mutation, rehash all 3,744 original files against that pre-operation
manifest and check their original lengths and modification times. Reject a live
owner, existing preservation lock, changed source binding or successful prior
completion. Record each file's current allocation and compressed flag so savings
from the interrupted attempt remain visible. Version 2 keeps all original
scope, resource limits and exclusions in
`COMPLETED-T-PILOT-RAW-PRESERVATION-AMENDMENT.md`.

Use new output names and a new six-copy control plus independent readback.
Then complete compression of the same original manifest, preserving already
compressed bytes. Final savings are cumulative against the original version-1
allocation; they are not all attributed to the retry. Separately reopen and hash
every original file before reporting success. No original evidence is deleted,
relocated or renamed. No solver configuration or live evaluation is changed.
