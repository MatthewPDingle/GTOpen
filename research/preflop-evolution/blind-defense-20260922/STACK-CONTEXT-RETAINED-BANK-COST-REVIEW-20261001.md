# Retained full-bank cost review

Prepared 1 October 2026 during the original fresh evaluation. This reviews the
already completed mandatory CUDA/reference check and current implementation
sources. No fresh-test payoffs or range probabilities were inspected; no new
benchmark, scientific deals, fits, native execution or GPU workload was launched.
The running evaluator and all registered inputs remain unchanged.

## Measured control timings

All rows use 32 previously retained training deals and all four actual played
banks, with 64 generations per bank. Query geometry and fitted local overrides
vary across depths, so these rows are not controlled comparisons of one changed
implementation. Loading is per context, not per 32-deal scientific batch.

| Stack | Fit status | Query rows | Context load seconds | Four bank averages, seconds | Median per-bank seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| 20bb | fit | 4,720 | 79.640 | 32.343 | 7.804 |
| 40bb | fit | 8,400 | 73.391 | 56.546 | 14.304 |
| 60bb | held-out fit | 9,936 | 70.094 | 12.015 | 2.977 |
| 100bb | fit | 12,752 | 81.375 | 87.906 | 21.914 |
| 150bb | held-out fit | 13,520 | 79.172 | 15.782 | 3.930 |
| 200bb | fit | 14,544 | 82.516 | 100.859 | 25.546 |
| 400bb | fit | 16,464 | 81.328 | 109.391 | 27.383 |

The 60/150bb held-out contexts score much faster here despite substantial query
counts. This pattern is consistent with fitted local-table work contributing to
the slower fitting contexts. It does not isolate a causal timing contribution:
query geometry, local data and desktop load differ, and the whole evaluation
also includes native queries/payoffs, serialization, journal checks and archives.
Do not extrapolate a full-run duration or a universal speedup from this control.

## Verified source behavior

PlayedBank.average prepares model-independent features/history once, then visits
every played generation. For each generation it directly calls every local
preflop overlay's apply method over the COMPLETE observation batch. A fitted
context has weighted preflop, exact-BTN and board-root overlays in the original
precedence order. The underlying scalar table loop checks each observation,
including postflop rows that it cannot change. Held-out contexts have no fitted
local overrides. These paths differ from shared neural inference itself.

The existing routed/batched CurrentPolicy candidates are not imported by the
registered study. More importantly, merely swapping that CurrentPolicy.prepare
method would NOT remove the separate full-batch per-generation overlay loop in
PlayedBank.average. A future integration must qualify the actual averaged-bank
path, not infer its speed or correctness from a single-current-policy control.

CurrentPolicy.infer also slices the same prepared NumPy actor features, copies
them to CUDA and copies actor scores back to CPU for every generation. Weights
are already cached; query features are prepared once but the device input
copies and score synchronizations still repeat. Genuine per-generation own
history reach is computed after all overrides and before weighted averaging.
It cannot be replaced by an unweighted average of the model probabilities.

## Suggested future work, not installed or admitted

First qualify a played-bank adapter that validates canonical query geometry and
history once, routes each original overlay over only preflop rows, preserves
original indices/precedence, and keeps the exact generation-specific own reach,
weights and unsupported-row fallback. Retain existing malformed-input refusals,
including one-action rejection when a table would have rejected it.

Then assess caching actor device feature tensors per query batch, or batching
independent frozen-generation inference, while preserving complete all-generation
policies, action legality, local tables, own histories and numerical tolerances.
Do not truncate the bank, discard overrides or reduce the scientific sample
budget to obtain a faster result. Such changes need actual integration controls,
retained full-bank CPU/CUDA reference checks and resource measurements before
future adoption. The earlier small current-policy CPU fixture speedup does not
establish a GPU played-bank or full-evaluation speedup.

These are source-based optimization leads, not profiled time attributions or
performance/accuracy results. Leave the admitted comparison and final reader
unchanged. No new scientific experiment, deployment or GitHub push follows from
this review; broader preflop accuracy and the separate prediction diagnostic
remain outstanding.
