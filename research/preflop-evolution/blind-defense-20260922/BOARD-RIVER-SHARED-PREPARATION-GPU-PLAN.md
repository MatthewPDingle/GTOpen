# Full-bank qualification of shared river query preparation

Run only after the current coverage collector and queued fit/evaluation/report
have completed and released their locks. Use the ten already inspected old
training archives from the CPU profile; no new deals, final evaluation cases,
training or model edits. This is an execution-equivalence/performance test,
not the estimator-integration experiment governed by the scientific gates.

Load both complete original 78-generation banks using the current qualified
loader and unchanged weights, float64 inference, direct table overrides and
ordered own-reach accumulation. The only candidate change is to call the
CPU-qualified shared preparation once, then perform each bank's existing
prepare/upload and inference separately. Validate each bank's context/geometry;
model-dependent tables remain separate. No precision or reduction-order change.

For each fixture compare reference and candidate policies and own-reach arrays
byte-for-byte. Compare the reference with its independently read-back archived
policy/reach (tolerances 1e-12 policy and 1e-9 relative reach). Reconstruct
conditional values using both identical policies and confirm archived values.
Any mismatch fails qualification; do not loosen thresholds after seeing it.

After output controls, time the same ten cases in separate/shared/shared/separate
order, including preparation and inference. Synchronize CUDA at pass boundaries.
Retain wall time, explicitly measured guard time and wall time excluding that
guard time. Resource/production guards stay enabled. Require lower combined
candidate wall time excluding guard time and no more than a 5% inclusive-wall
regression, in addition to all output checks. Report variability and memory;
this short cached-input benchmark does not prove gains for every future batch.

Use one GPU owner, the existing 4 GB CUDA allocator cap and 2 GB external
headroom, at least 24 GB free RAM, and a ten-minute maximum. Added artifacts are
two small JSON records and a later findings note, capped at 2 MB. No new model
archives or historical modifications. No live collector source will be changed.

Passing permits considering the same verified preparation reuse in a newly
registered future collector. It does not qualify different chunk sizes,
asynchronous CPU workers, GPU graphs, alternate precision or poker-model changes.
