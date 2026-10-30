# Faster visible-feature preparation, unchanged training inputs

25 September 2026. `sampled_visible_features_bulk_v1.py` bulk-decodes the
original 36 one-hot groups and computes the unchanged visible-card summary
once per distinct visible hole/board tuple within a call. The original 269
features, including betting history, remain intact; all 33 additional summaries
use the original scalar poker calculation. Reuse is local to a call, with no
persistent cache or new source of hidden information.

## Complete saved-data equivalence and paired timings

The control used both complete final-update retained datasets and one complete
native query batch from the finished replication. Three reference/candidate
pairs alternated order, without cProfile. Each timed call includes construction
of observation dictionaries, allocation and feature output. All output bytes
matched in every repeat; the two retained-dataset hashes also match the earlier
profiling run's recorded outputs.

| Dataset | Rows | Reference median | Bulk median | Stage speedup |
| --- | ---: | ---: | ---: | ---: |
| BB retained data | 245,141 | 28.609 s | 5.953 s | 4.806x |
| BTN retained data | 121,251 | 14.047 s | 3.719 s | 3.777x |
| Native batch 78/00 | 29,046 | 3.218 s | 0.219 s | 14.694x |

The same control checked 6,000 synthetic observations covering all four streets,
permuted feature order and varying history lengths. It checked empty output and
13 invalid cases against both implementations: short/long rows, duplicates,
boolean/float/NumPy-integer input, overflow and negative indices, invalid
one-hot groups, mismatched missing cards, incomplete visible boards, history
gaps and duplicate cards. No original registered source was edited.

These are feature-stage measurements on saved data, not whole-training or
production-solver speedups. The single native batch is not a timing survey of
every scenario. No new statistical poker validation was performed.

## Complete CUDA fit replay

`sampled_visible_hybrid_fit_bulk_v1.py` changes only the feature-builder import
from the original fitter; initialization, grouping, objective, optimizer,
precision, chunk order and gradient accumulation are unchanged.

The CUDA control restored the original final reservoirs and replayed both
players' complete 512-step fits, with their original seeds, device, versions and
deterministic settings. Both resulting network dictionaries matched the stored
original networks exactly. Every non-timing fit metric also matched exactly.

| Player | Original setup | Bulk setup | Original optimizer phase | Replay optimizer phase |
| --- | ---: | ---: | ---: | ---: |
| BB | 33.047 s | 6.469 s | 47.546 s | 44.890 s |
| BTN | 15.313 s | 4.015 s | 24.203 s | 21.969 s |

The setup total fell from 48.360 to 10.484 seconds in this historical comparison.
Optimizer math did not change; its timing difference is not attributed to the
feature optimization. The whole replay worker, including checkpoint loading,
checks and both fits, took 114.281 seconds. This is a saved-step equivalence
control, not a fresh candidate run or a paired full-training benchmark.

## Adoption and remaining work

The separately versioned bulk builder and fitter are available for future
research runs. Existing completed trials, registered readers and production
56708 remain unchanged. The optimization has not been used to make a range-
quality claim or to reinterpret the negative matched-estimator study.

New research inference and audit versions can consume this builder after their
own output checks. Repeated checkpoint restoration/validation remains a measured
bottleneck. GPU batching remains another candidate; no GPU-kernel speedup has
been established here. Use these improvements to reduce the cost of the next
diagnostic separating chance noise from continuation-learning error.

All controls had exclusive research ownership, production-idle and resource
guards. New output was capped at 10 MB per control, with fresh global storage
admission; the latest measured combined research allocation was 767.567 GB.
The CPU control took 205.14 seconds and the CUDA replay 114.28 seconds, excluding
their controllers' prelaunch storage inventory.

## Evidence

- `visible-features-bulk-control-v1-result.json`: all repeat timings, input
  cases, row counts and output hashes.
- `visible-features-bulk-cuda-replay-v1-result.json`: exact network and metric
  equality for both fits, and stage timings.
- `visible-features-bulk-controls-artifact-review-v1.json`: registration/result
  links and original selected metrics/query hashes checked against the complete
  trial artifact manifest. This is an identity review, not a second replay.
- Both controls preserve their source registration, terminal status and log.
