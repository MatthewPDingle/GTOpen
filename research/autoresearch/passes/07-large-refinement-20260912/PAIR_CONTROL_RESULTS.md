# Bounded-memory GPU pair control: initial version rejected

Research only; no deployment or mutation of port 56708. This estimates the
existing coupled_deck_v1 canonical model, not physical multiway poker equity.

Five numerical tests passed: direct canonical pair means, full-correction
cancellation and fixed constraints, captured/eager execution, zero reach and
reactivation, and all 1,024 cyclic sample offsets on twelve fixed-range fixtures.
The separate GPU regression run also passed all 6 postflop and 13 preflop tests.
CPU comparisons in those tests are correctness references only. The final
default `cargo test --release -p solver` suite also passed (193.344 seconds
including compilation); this is regression validation, not a CPU speed trial.

The pooled variance ratio was 0.648320 (35.2% reduction). This pooled number
conceals a material player-count effect:

| Players | Flat | Pair-heavy | Mixed |
|---|---:|---:|---:|
| 3 | 0.059 | 0.113 | 0.128 |
| 4 | 0.196 | 0.366 | 0.409 |
| 6 | 0.526 | 0.768 | 0.808 |
| 8 | 0.750 | 0.917 | 0.937 |

All 169 hand means in every fixture stayed within the registered 0.0002 bb
tolerance. Individual hand variances, including regressions, remain in the raw
JSON; these are fixture-level pooled ratios, not a guarantee for every hand.

Same executable, six-player fixture, gamma15/64, full canonical checks every
25 iterations, target 0.005 bb twice:

| Seed | Control iterations / seconds | Correction iterations / seconds | Final corrected gap |
|---|---:|---:|---:|
| 42 | 275 / 3.141 | 300 / 4.314 | 0.003893 |
| 314159 | 325 / 3.559 | 275 / 3.809 | 0.004485 |

The correction allocated 7,366,372 extra bytes on this fixture. Both saves
round-tripped exactly. Seed 42 exceeded the pre-registered 1.25x runtime cap;
therefore the runner correctly skipped the large trial. These short timings
are a rejection screen, not a precise estimate of production throughput.
Fewer iterations on one seed did not compensate for the added work. The current
implementation projects exact pair means and then launches a separate
correction kernel which rereads CDF values; its overhead has not been isolated
with a profiler, so attributing all slowdown to that launch would be premature.

`python research/autoresearch/passes/07-large-refinement-20260912/check_pair_control.py`
independently recomputes numerical weighting, all per-hand mean/variance checks,
canonical global gaps, convergence streaks, shared executable identity, memory
caps and the learning gate. Exit zero means valid evidence, including rejection;
the emitted `learning_pass` is false.

Large-game conditional accuracy remains unqualified. The earlier branch
refinement and unrestricted-global consistency failures are not resolved by
these numerical tests.

## Next bounded experiment, registered before execution

Test whether spending the variance reduction on fewer particles is useful
before rewriting/fusing kernels. Run same-binary native gamma15/64 controls
against pair-corrected gamma15/32 candidates for seeds 42 and 314159, limit
1,000, full canonical checks every 25, target 0.005 twice, cap 600 seconds each.
Require both candidates to converge and each total time to beat its paired
control before investing in further qualification. Keep both successes and
failures. This is a new lower-sample hypothesis, not a rerun or reversal of the
failed 64-particle gate. No large run is authorized by this screen alone:
32-particle numerical/constraint verification and additional seeds must precede
a large trial. Do not tune control coefficients or change the accuracy target.

## Lower-sample result: also rejected

The first invocation (`pair-budget-...-v1`) stopped before candidate learning:
32 was absent from the research experiment allowlist. That failure is retained.
Version 2 adds 32 only to the offline research harness and its exhaustive cyclic
inclusion test. Six pair-control tests then passed, including 32- and 64-sample
captured/eager agreement and twelve full-offset numerical fixtures at each size.

| Seed | Native 64 iterations / seconds | Corrected 32 iterations / seconds |
|---|---:|---:|
| 42 | 275 / 3.086 | 300 / 3.290 |
| 314159 | 325 / 3.576 | 275 / 3.034 |

Both reached the unchanged accuracy target twice, but only one beat its control.
The registered gate failed, so no large trial followed. The corrected 32-sample
variance was 1.55, 1.93, and 1.94 times native 64 on the three eight-player
fixtures. Thus halving the sample count spends more variance than this control
removes in the relevant large-player setting. It is not a supported replacement.

`check_pair_budget.py` independently checks all 24 numerical fixtures, every
hand, allocation caps, control/candidate executable identity, full global checks,
saved-state round trips, and the rejected speed decision. It emits
`evidence_verified: true, learning_pass: false`.

Next priority: investigate sampling arrangements which reduce variance without
adding per-terminal matrix projections/correction work. Do not expand this
pair-control implementation or deploy it on the strength of the pooled 35.2%
number. Any new sampling scheme must preserve equal inclusion of every canonical
particle, leave full evaluation unchanged, and pass numerical and convergence
screens before attempting the unresolved large-game conditional qualification.
