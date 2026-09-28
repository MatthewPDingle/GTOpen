# Shared preparation: full-bank output and performance check

Completed 2026-09-28. Session 93137 exited 0 after the main coverage pipeline
had completed and released the shared research locks. Every registered check
passed. No production or historical data changed.

The candidate prepares bank-independent inputs once, validates each bank's
context, then retains separate bank-specific tables/uploads and unchanged
float64 inference and ordered averaging over both complete 78-generation banks.
It changes no precision, sampling, model, targets or reduction order.

On all ten old training fixtures (both actors and every pot band), reference
and candidate policy and own-reach arrays were byte-for-byte equal. Both also
matched independently checked archived outputs exactly. Reconstructed
conditional values had zero discrepancy against archived values.

| Pass | Inclusive seconds | Guard seconds | Seconds excluding guard |
|---|---:|---:|---:|
| Separate preparation 1 | 9.988 | 1.299 | 8.689 |
| Shared preparation 1 | 5.120 | 0.021 | 5.099 |
| Shared preparation 2 | 4.792 | 0.012 | 4.780 |
| Separate preparation 2 | 8.741 | 0.032 | 8.709 |

Combined counterbalanced passes give 1.761x speedup excluding guard time,
or 43.2% lower time for this preparation-and-inference stage. The saving was
0.376 seconds/case. Inclusive speedup was 1.889x, but the first separate pass
incurred a scheduled desktop-use probe; 1.761x is the cleaner comparison.

This small cached-input benchmark excludes bank loading, native export,
archives, later training and evaluation. It is not complete collector or
production solver throughput. The complete qualification took 97.5 seconds,
including both bank loads and output checks. Peak CUDA allocation was
177,450,496 bytes; peak reservation was 224,395,264 bytes.

Passing permits this exact reuse in a newly registered future collector.
Preserve the qualified helper and per-bank context validation. Do not rewrite
completed study sources or infer qualification for copy removal, other batching,
precision changes or asynchronous workers.

Evidence: board-river-shared-preparation-gpu-v1-registration.json and
board-river-shared-preparation-gpu-v1-result.json. This runtime qualification
is separate from the scientific learning and estimator-integration gates.
