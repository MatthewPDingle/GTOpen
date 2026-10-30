# BB learning-target ingestion control

The separate BB root target adapter passed control v4. It is not wired into
production, the running broader evaluation, or a new training trial.

For each sampled BB starting decision, the adapter reconstructs the original
action values using the native root value. It substitutes the exact conditional
all-in value against the current played BTN policy, then recenters all four
advantages. The fold, ordinary call and ordinary raise action values stay the
same; their advantages change consistently with the new policy-weighted value.
The complete current initial policy is frozen once per generation.

Raw native updates and their cashflow-verification records remain unchanged.
The derived targets have a separate method identifier and audit witnesses.
All other BB decisions and all sampled BTN targets remain unchanged. The
separately controlled exact BTN accumulator is not updated by this adapter.

## What passed

- 32 immutable historical native batches: 512 physical deals at each of played
  generations 0, 25, 51 and 77; 2,048 corrected BB roots.
- Independent scalar integration and action-value reconstruction agreed within
  2.85e-14 bb. The oracle does not use the adapter's correction formula or
  matrix-evaluation method.
- 40,625 BB and 7,788 BTN insertion events retained their counts and ordering.
  A deliberately small 97-row reservoir forced repeated replacement, checking
  identical RNG state, keys, features, action counts and iteration metadata.
  Retained corrected values matched the independent oracle; unaffected values
  were exactly unchanged.
- Seven malformed-input cases were rejected. The six ingestion rejection
  cases left already populated reservoirs and their RNGs untouched; the
  seventh rejected an incorrect matrix identity at target construction.
- All admitted source artifacts remained byte-identical. CPU only; about
  50 seconds. No CUDA execution or new poker-strength result.

## Preserved failed controls

The first control used the complete cache identity to ingest old traces that
explicitly name their original smaller cache. The adapter correctly refused
that mismatch. Control v2 uses the original audited cache for raw ingestion
and verifies that every historical cache row agrees with the complete cache.

Control v2 then exposed an adapter compatibility error: older raw query
transports omit the optional own-history field. Adapter v2 accepts its absence
at these structurally verified first-action nodes, while still rejecting an
explicit nonempty own history. Adapter v1 is not qualified.

Control v3's opponent-policy rejection test accidentally replaced an already
uniform policy with the same uniform policy. Control v4 deliberately changes
the distribution and passes. These are test/integration failures, not evidence
about a candidate's poker performance. All original registrations, source
versions and failure results are retained.

## Next gate

Use `exact_initial_training_ingest_v2.py`, whose passing test is
`hu_exact_initial_training_ingest_control_20260923_v4.py`. After the current
evaluation releases the GPU, test exact-policy CUDA parity, then a small joint
training run and checkpoint restart. Only after those gates should a fresh,
prospectively declared training comparison begin. This work does not yet
qualify ordinary calling decisions or other positions and stack sizes.
