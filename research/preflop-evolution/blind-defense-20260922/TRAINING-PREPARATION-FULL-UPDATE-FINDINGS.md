# Preparation optimizations: complete-update qualification

The four-case control completed successfully in session 79637 (exit 0).
Both original and optimized implementations reproduced the original archived
update-79 oracle for baseline and river training, starting from A-seed boundary
78. The comparison checked complete restored state, checkpoint/model identities,
physical subbatch artifacts, exact BTN updates, ordered reservoirs and every
non-timing numerical fit metric.

An additional readback checked the result/registration binding, all four metric
and checkpoint digests, completion markers, all physical subbatch artifact hashes
and the timing arithmetic. The earlier eight fitted-network checks separately
cover both training seeds and both players at boundary 80.

## Measured pipeline time

| Method | Original (s) | Optimized (s) | Time reduction |
| --- | ---: | ---: | ---: |
| Baseline | 59.500 | 49.625 | 16.60% |
| River | 181.312 | 171.250 | 5.55% |

These are one pair per method, with original first for baseline and optimized
first for river. They are descriptive timings under the current desktop load.
They include the training pipeline, but exclude the surrounding admission,
source copying, oracle restoration/comparison and final verification. The entire
control took 928.437 seconds. Do not present these pipeline sums as that whole
invocation or claim a universal speedup.

The baseline fit component fell from 25.875 to 16.578 seconds. The optimized river
pipeline still spent 136.907 seconds in its physical-target stage, versus 18.656
seconds fitting. Its eight worker records sum to 850.125 seconds of river-target
work; that overlapping CPU total must not be added to wall-clock time. This
explains why faster fitting delivers a much smaller overall river saving.

The optimized river update recorded eight distinct physical-worker PIDs. Their
reported resident memory summed to 3.300 GB, with a largest individual record of
0.427 GB. These are samples at worker reporting times, not a simultaneous or
complete process-tree peak. There is room to investigate bounded concurrent
training arms, subject to fresh resource admission and exact output checks.

## Decision and scope

The versioned preparation pipelines may be used in a future registered research
run within this tested scope. Keep the original registered pipelines and evidence
unchanged. The baseline candidate changes fit-feature preparation; the river
candidate additionally changes CPU query preparation. Neither changes the
learning objective, seeds, fitting budget or sampled training data.

The separate bulk checkpoint loader was not included here. Its historical
readback qualification is separate; the above percentages do not include it.
No production behavior, live game, learning bank, or evaluation dataset changed.
No new accuracy claim, deployment or push follows from this control.

The next throughput experiment should compare a serial pair of independent
training arms with the same pair running concurrently, retaining the GPU and
production-priority limits. More expensive river training remains only a research
candidate: the completed quality study did not establish a reliable advantage.
Further model-quality work must also improve evaluation precision and cover
additional stacks, positions, sizes and multiway contexts.

## Evidence

- [Plan](TRAINING-PREPARATION-FULL-UPDATE-PLAN.md)
- [Registration](training-preparation-full-update-control-v1-registration.json),
  SHA256 0f8ce077c79297513231a2edb8eceb2e3335f8db72865632c24eb17230f6e249
- [Result](training-preparation-full-update-control-v1-result.json),
  SHA256 5d8c3f22a6270ee95111e3e8c32a50828cfdac4bcf2e253fd5b295661ab282ef
- [Eight fitted-network checks](VISIBLE-FEATURE-VECTOR-GPU-FINDINGS.md)

The retained control occupies 2.064 GB logical / 0.886 GB allocated in
S:/GTOpen-research/training-preparation-full-update-control-v1. Its admission
inventory was 738.368 GB allocated with 14 GB reserved, within the 800 GB cap.
These are recorded snapshots; re-inventory before another substantial allocation.
