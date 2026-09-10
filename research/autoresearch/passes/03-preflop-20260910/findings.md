# Preflop performance research — interim

The ten-hour run remains active until **21:34:18 UTC, 10 September 2026**
(07:04:18 Adelaide on 11 September). These are isolated research results;
the live application on port 56708 has not been replaced or restarted.

## Best measured GPU candidate so far

| Fixed control | Original iteration | Candidate iteration | Reduction |
|---|---:|---:|---:|
| Eight-seat saved game, checkpoint 74 | 9.788 s | 5.462 s | 44.2% |
| Seven-seat fresh game | 2.821 s | 1.368 s | 51.5% |
| Six-seat fresh control | 99.535 ms | 49.225 ms | 50.5% |
| Three-seat small control | 2.481 ms | 1.314 ms | 47.0% |

Iteration figures are medians after the first iteration, with identical input
and iteration counts for each comparison. Early fresh-game iterations change
workload as strategies develop; compare only the matched controls, not rows
against each other. Small controls remain sensitive to timing noise. The eight-seat repeat was 5.469 seconds.

All four controls have **identical complete regret/strategy fingerprints,
gaps and EVs**. The eight-seat accuracy check fell from 11.700 to 7.036 seconds (repeat 7.030).
Its estimated solver VRAM fell from about 20.9 GB initially to 13.1 GB;
the intermediate normalization candidate used 21.4 GB. These are constructor
allocation estimates, not whole-device memory measurements.

Changes retained in the research branch use a 192-thread terminal launch,
prepare counterfactual probabilities once, skip unused learning CDF slots,
normalize reach once before particle scans, and allocate CDF scratch for the
largest individual traverser span instead of the union across all seats.
They also precompute opponent CDF addresses and specialize exact terminal
calculations by opponent count without changing arithmetic order.
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
Those experiments are complete: address hoisting and opponent specialization
were retained; live-terminal worklists and wider CDF blocks did not clear the
whole-solve retention threshold. Current work covers modeled/frozen tables,
forced-policy VRAM budgeting, and CPU checkpoint traversal.

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

## Checkpoint and modeled-workload gates, 14:03 UTC

Paired CPU checkpoints reuse terminal values between best-response and average
outputs. Four fixed controls preserved every checkpoint gap, EV, iteration and
root strategy. Total time fell 22.7%, 8.5%, 16.0% and 6.9% for the three-, four-,
six- and nine-seat controls versus the preceding CPU candidate; the six-seat
control is fixed 20 iterations, not converged. Checkpoint time roughly halved.
Observed peak RSS was 54.6 MB versus 54.7 MB on six seats and 15.95 MB versus
15.48 MB on nine seats. Wider-frontier and parallel cancellation gates remain.

Forced-policy GPU storage was omitted from the previous memory planner. The
common accounting fix now passes host routing/budget, internal GPU, real
minimum-fit and all 13 preflop GPU tests. It will be applied to both original
and optimized modeled-workload controls. A new native fixture helper caught a
post-save preservation mismatch and refused its output; that fixture is not
yet an accepted benchmark input. Original user saves remain untouched.

## Modeled tables and memory sensitivity, 14:40 UTC

Native measured-policy fixtures now pass strict typed and raw metadata checks.
Legacy and frozen-legacy comparisons match exact arenas/gaps/EVs and show no
material timing change. Coupled modeled trees use 15.36GB optimized versus
22.89GB original allocations at the same23GB budget, with batch32 versus30.
The first iteration medians were3.52s versus28.09s, but original at21GB falls
to6.60s and a23GB repeat is much slower. This demonstrates memory sensitivity;
do not report a stable eightfold kernel speedup or claim measured paging.

The full comparator checked861384actionnodes. Aggregate EV/gap differences
are below3e-8bb, but individual conditional policies differ by up to28.2
percentage points on tiny-reaching branches. This is real distribution change,
not the native uniform fallback. The weighted mean does not establish local
correctness. A matched-batch control and an original-grouping compatibility
planner are being assessed before accepting modeled-table behavior.

### 14:51 UTC: matched grouping restores exact modeled strategies

The optimized layout with explicit batch 30 matches original batch 30 in all 623,785,422 regret/strategy-sum values, all 311,892,711 effective policy entries, every gap and EV, and the native header. Median iteration is 3,624.8 ms and check 4,525.6 ms. Production candidate b7e8583 preserves the original corrected-budget batch and HU cache selection while using compact physical storage. Budget controls and minimum-fit fallback checks remain pending. The earlier default batch-32 local policy divergence is not accepted.

### 15:10 UTC: deployed versus corrected reference scope

The modeled exact-parity controls above include the forced-policy accounting correction in both baseline and candidate. The deployed pre-pass code omitted that allocation, so its batch/cache selection can differ. We are separately reviewing preservation of the deployed grouping when the accurately accounted compact allocation fits. This does not change the frozen convergence protocol or establish deployed-model parity yet.

### Modeled six-seat convergence, corrected-accounting reference

The predeclared 19 GB pair reached the unchanged 0.004 bb learning-gap target at iteration 80 in both versions. Original trajectory 526.5105347 seconds; compatible candidate 289.5910553 seconds (44.998% less). All eight checkpoint gaps, EVs, learning-seat masks and final arena fingerprint d2df70bd6515aabf match exactly; both native save/reload checks passed. This comparison uses the explicitly frozen original kernel with the common forced-policy accounting correction, B23/HU cache enabled. Literal deployed grouping differs for this modeled fixture and remains a separate pending gate; do not relabel this result as that comparison.

### Eight-seat fixed continuation trajectory

Both versions completed native iterations74→174 and missed the predeclared0.005bb target, finishing at0.13924453875862922bb. All ten checkpoint gaps, EVs, learning masks and the final arena fingerprint34d3d0185ea97ce4 match exactly; native round trips passed. Original trajectory1064.6219903seconds; compatible602.4928996seconds (43.408% less). This is fixed-work speed, not time to convergence. Full elementwise native comparisons are running separately.
