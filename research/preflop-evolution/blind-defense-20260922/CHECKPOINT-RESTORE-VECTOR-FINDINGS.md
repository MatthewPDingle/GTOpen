# Faster checkpoint readback: isolated CPU checks

The separate bulk-validation loader reproduced all eight archived parent-80
reservoirs and all four complete checkpoint states exactly. In four single paired
checks, total restore time fell from 49.063 to 21.795 seconds, a 55.6% reduction
for this component. This is not a measured whole-training speedup or evidence of
better poker play. The registered continuation still uses its original loader.

## Why this was investigated

The training runner restores and compares every newly written checkpoint after
the pipeline's own timer has stopped. A CPU profile of archived A-baseline
checkpoint 80 took 20.219 seconds. Two reservoir loads accounted for 13.17 seconds;
model-bank validation and other checkpoint checks took additional time. Function
totals overlap. cProfile overhead and concurrent work make these diagnostic
measurements, not isolated throughput measurements.

The existing reservoir loader validates one row at a time. The isolated candidate
keeps the same archive fields, dtype/shape checks, metadata/context checks and RNG
restoration. It validates feature bounds/uniqueness, arity, finite legal targets,
positive bounded weights and iteration labels in batches of 8,192 rows. Integer
key bounds follow from the unchanged uint64 dtype check. It returns the original
reservoir type and preserves every allocated array byte, including unsorted
feature rows and signed-zero padding accepted by the original loader.

The separate complete checkpoint wrapper differs from the original restore
function only in its reservoir-load call. An AST comparison enforces that rule.
All original object hashes, historical model validation, table reconstruction,
sampler, accumulator and configuration checks remain in the restore path.

## Completed evidence

- Eight original reservoirs: **1,657,939 rows**, identical complete arrays,
  metadata summaries and random-number state.
- Four complete checkpoint restores: identical saved model references, sampler,
  action RNG, both accumulators and complete reservoir states.
- Three valid synthetic archives, including empty and full reservoirs, unsorted
  features, integer limits and weight boundaries: exact restored bytes/state.
- Thirty-six malformed archives: rejected by both loaders. Cases cover fields,
  dtypes/shapes, features, arity, nonfinite/nonlegal targets, weights, iteration,
  context, metadata and RNG state. This is focused coverage, not an exhaustive
  proof for every possible damaged archive.

| Archived checkpoint | Original restore (s) | Candidate restore (s) | First run |
| --- | ---: | ---: | --- |
| A-baseline 80 | 11.797 | 5.031 | Original |
| A-river 80 | 12.656 | 5.718 | Candidate |
| B-baseline 80 | 12.719 | 5.859 | Original |
| B-river 80 | 11.891 | 5.187 | Candidate |

These are single pairs under concurrent study/desktop load, with alternating
order for full checkpoints. Standalone reservoir pairs ran original first for
player 0 and candidate first for player 1, so order is confounded with player in
those component timings. No GPU, fitting, new deals or live-source changes were
used. The profile (exec 50466) and comparison (exec 92362) both exited 0; the
comparison took 105.516 seconds. Exact overlap timestamps are in their outputs.

## Adoption

Keep the current registered study and its reviewer unchanged. This isolated
candidate can be considered for a later runner after its integration preserves
the same guards and is qualified. The already prepared feature-fit and full-update
controls remain queued after the scientific continuation and independent review.
Do not add these component speed ratios or assume they multiply into whole-run
gains. No production deployment or new GitHub push is part of these checks.

Evidence: `checkpoint-readback-cpu-profile-v1-result.json`,
`checkpoint-restore-vector-control-v1-registration.json` and its result.
The comparison registration SHA256 is
`23f066326dfdf8ab69a8ad8a8886ce877529be5d3caf7ccd9c169942800454b3`.
The inputs and source identities are recorded in those artifacts.
