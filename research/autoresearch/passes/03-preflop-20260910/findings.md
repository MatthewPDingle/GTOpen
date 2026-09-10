# Preflop performance research — interim

The ten-hour run remains active until **21:34:18 UTC, 10 September 2026**
(07:04:18 Adelaide on 11 September). These are isolated research results;
the live application on port 56708 has not been replaced or restarted.

## Best measured GPU candidate so far

| Fixed control | Original iteration | Candidate iteration | Reduction |
|---|---:|---:|---:|
| Eight-seat saved game, checkpoint 74 | 9.788 s | 6.239 s | 36.3% |
| Seven-seat fresh game | 2.821 s | 1.508 s | 46.6% |
| Six-seat fresh control | 99.535 ms | 55.613 ms | 44.1% |
| Three-seat small control | 2.481 ms | 2.379 ms | 4.1% |

Iteration figures are medians after the first iteration, with identical input
and iteration counts for each comparison. Early fresh-game iterations change
workload as strategies develop; compare only the matched controls, not rows
against each other. The three-seat result is small and sensitive to timing noise.

All four controls have **identical complete regret/strategy fingerprints,
gaps and EVs**. The eight-seat accuracy check fell from 11.700 to 8.261 seconds.
Its estimated solver VRAM fell from about 20.9 GB initially to 13.1 GB;
the intermediate normalization candidate used 21.4 GB. These are constructor
allocation estimates, not whole-device memory measurements.

Changes retained in the research branch use a 192-thread terminal launch,
prepare counterfactual probabilities once, skip unused learning CDF slots,
normalize reach once before particle scans, and allocate CDF scratch for the
largest individual traverser span instead of the union across all seats.
Low-memory fallbacks preserve direct normalization and union storage where needed.
All 1,024 particles, precision, bet menus, policies and model semantics remain.

The compact candidate passed 11 internal GPU tests, exact union/compact graph
comparisons, and a real direct/cached one-particle memory-boundary test. Earlier
normalization also passed the 13-test preflop GPU suite. Final combined CPU/GPU,
legacy and save/profile checks remain required before integration.

## CPU work

Minimum exact quadrature reduces redundant tie-share products for fewer than
eight opponents. Recorded three/four-seat solves reached the same target at
the same iterations with identical gaps, EVs and root strategies. A six-seat
20-iteration control also matched those outputs and completed sooner.

An all-eight-opponent terminal microbenchmark regressed approximately 5%.
Several source-shape experiments did not fix it and are not being retained.
A whole nine-seat limp-only control reached the same target in 20 iterations,
about 15% sooner in the first trial and 13% sooner with the clean candidate.
The full default CPU suite passed 174 tests (four ignored) across 36 executables.
Two initial fixture lookup failures were runner working-directory errors;
the identical executable passed all 56 preflop tests from the Cargo package folder. Do not describe the CPU change as universally
faster or bitwise identical at the f64 equity level: reference differences are
around machine precision, though the measured solve outputs matched.

## Remaining work

The eager CUDA phase diagnostic attributes nearly all time to CDF generation
and coupled terminal evaluation. It preserves the expected final fingerprint,
but event timings are diagnostic and are not production graph benchmarks.
Next experiments target unnecessary terminal blocks and repeated address work.

Raw evidence is append-only in `raw/` and `events.jsonl`; `results.json`,
`cpu-comparisons.json` and `progress.png` are derived views. Failed/rejected
trials remain visible. No final speed claim or completion is implied here.

## Further trials, 13:32 UTC

The static live-terminal worklist passed all correctness gates but was rejected:
its repeatable roughly 1.5% gain missed the fixed 2% retention threshold and
required extra indices. Its source and evidence remain archived.

Precomputed 64-bit CDF base addresses (dea49d1) are promising: the eight-seat
median is 6.018 seconds and its check 7.867 seconds, with exact original outputs.
This is still under repeat/control testing. CDF block geometry trials run
sequentially at 8/16/4 independent warps; all use identical scan arithmetic.
