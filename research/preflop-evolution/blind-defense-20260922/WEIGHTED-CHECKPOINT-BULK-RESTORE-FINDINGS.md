# Faster complete checkpoint recovery

The qualified candidate recovers exactly the same completed training state while
checking saved reservoir rows in bounded NumPy batches. It retains the complete
checkpoint identity checks, object hashes, all 79 historical/current models,
reconstruction of current weighted tables, sampler state, both learning
accumulators, and random-number states. No historical-model cache or skipped
validation was introduced.

This is an execution improvement. It changes no poker policy, training target,
sampling distribution or checkpoint format, and has not changed the live study.

## Finding the cost

A read-only profile of the completed first arm identified 464,509 calls to
the scalar row validator, including both saved reservoir rows and model-table
validation. Restoring the two reservoirs accounted for 19.37 seconds of the
30.14-second profiled restore. Profiling adds substantial overhead; these are
diagnostic timings, not ordinary execution measurements.

The reservoir candidate validates the same properties in batches of at most
16,384 rows: array types/shapes, distinct in-range features, legal action counts,
finite values, zero illegal-action targets, positive bounded importance weights,
nonzero iteration labels, context and metadata. Unsigned key storage retains
the original key bounds. Feature sorting is a private validation copy; stored
feature order remains unchanged.

## Controls and measured timings

The completed reservoirs contain 262,144 BB rows and 147,926 BTN rows. Original
and candidate loaders matched every allocated array, summary, and RNG state.
After 32 further in-memory insertions per player, they still matched exactly.
No resumed insertion was written into the research checkpoint.

Eighteen small fixtures matched the original loader: three valid cases (ordinary,
unsorted features, empty) and fifteen malformed cases. The failures covered
duplicate/out-of-range features, invalid action counts, nonfinite/illegal targets,
invalid weights and iteration labels, shape/type mismatches, metadata and context.

| Operation | Original | Candidate |
| --- | ---: | ---: |
| BB reservoir load | 6.063 s | 0.078 s |
| BTN reservoir load | 4.125 s | 0.062 s |
| Complete checkpoint restore | 18.578 s before; 19.422 s after | 8.203 s |

The full restore comparison was original / candidate / original on the same
completed 78-update checkpoint. Every recovered state component matched. Both
readers rejected changed configuration, object hash, matrix identity and context.
The full restore retains expensive model/history validation, so its improvement
is about 2.3x here, not the much larger isolated reservoir-loader ratio.

Timings were measured during other live research, with more than 48 GB RAM
available and CPU admission below 60%. They are not an isolated system benchmark
or an end-to-end training speedup. All controls were CPU-only. The new helpers
are candidates for the next qualified execution version; no running process was
patched or restarted.

## Evidence and implementation

- `weighted-checkpoint-restore-profile-v1.json`: profiling observations.
- `weighted-reservoir-bulk-load-control-v1-result.json`: full arrays, continued
  insertions, malformed fixture parity, source hashes and component timings.
- `weighted-checkpoint-bulk-restore-control-v1-result.json`: complete recovered
  state equality, retained validation, negative identity tests and restore timings.
- `tools/research/weighted_reservoir_bulk_load_v1.py` and
  `tools/research/weighted_checkpoint_bulk_restore_v1.py`: separately versioned
  implementations; original readers remain unchanged.

Together with the faster storage scan, this identifies concrete CPU overhead
that can be reduced before another substantial training run. Measure combined
whole-update timing and exact resumed output before claiming an integrated gain.
