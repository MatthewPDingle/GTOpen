# Recovery scheduling amendment, before continuation

The original replication stopped at the T: free-volume floor during update 53,
with update 52 durable. Its supervisor also terminated the first trial's
independent audit after 69 updates. Preserve these interrupted attempts.

After the fixed pilot GPU relocation replay passes, the S: continuation may
overlap the CPU audit of the immutable original 52-update prefix. This replaces
step 4's serial prefix-audit prerequisite in
`LATER-ACTION-VOLUME-RECOVERY-OPERATIONS.md`. It follows the same scheduling
principle already used for the first audit and second GPU training trial.

Before continuation starts, the prefix reader must have registered its complete
file-hash snapshot, original configuration, last durable checkpoint, and charged
runtime. The continuation verifies those immutable files and must observe either
that exact live reader process (including creation time) or its successful,
identity-matching review. If the review fails or the process disappears without
a passing result, stop the continuation. The controller cannot report successful
completion until the prefix audit passes.

The complete 78-update independent audit still runs afterward across both
volumes and remains mandatory before heldout evaluation. This overlap does not
accept an unaudited final model, change seeds or mathematical targets, replace
the complete audit with a prefix audit, or permit score-dependent stopping.
The original remaining training time allowance continues to include resumed
controller time, including any final wait for prefix verification.

This avoids leaving the GPU idle for an hour while an independent CPU-only
reader examines immutable evidence. The separate recovery of the first audit
can run on another CPU core. No production solve is changed.
