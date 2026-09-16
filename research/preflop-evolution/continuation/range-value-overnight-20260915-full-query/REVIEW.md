# Continuation-value research: final review

The candidate passed the frozen average-error screen on both independent source
families. All 3,200 corrected references and the final reported point estimates,
paired bootstrap intervals and per-hand diagnostics passed the independent audit.
This justifies further controlled validation; it does not justify replacing the
live preflop model yet.

## What improved

Training-only selection chose the range-shape encoder with ridge penalty 0.1.
Its validation error was 6.97% of the starting pot, ahead of the seven other
predeclared settings. The PCA option did not win. Neither test family chose the
model or its penalty.

| Independent family | Balanced error | Candidate error | Reduction vs Balanced | Reduction vs raw equity |
|---|---:|---:|---:|---:|
| Eight-player open sources | 12.50 | 9.46 | 24.3% | 33.4% |
| Seven-player straddle sources | 14.05 | 7.75 | 44.8% | 51.5% |

Errors are range-weighted per-hand continuation-value MAE, as a percentage of
the starting pot. The sources supplied ranges; every postflop reference was
recomputed heads-up with zero rake. The improvements over Balanced have paired
95% board-bootstrap intervals of 2.22–3.66 and 4.07–8.08 percentage points of
pot, respectively. Both intervals favor the candidate under this experiment.

## What still needs work

The candidate beats Balanced in five of eight individual cases, and raw equity
in six. Family averages hide regressions:

| Case | Balanced error | Candidate error |
|---|---:|---:|
| test-seven-straddle-00 | 4.99 | 8.71 |
| test-seven-straddle-02 | 7.92 | 8.21 |
| test-eight-open-02 | 6.35 | 9.48 |

One large gain, from 34.26 to 9.62 in `test-seven-straddle-03`, contributes
substantially to that family's improvement. We should not promise uniform gains.

Some hand-level misses are much larger than the average. For example, OOP AA
in `test-eight-open-01` is predicted at 17.90bb against a 50.66bb reference in
the normalized 20bb pot. That hand has only 0.00494% compatible range mass and
was inserted as a tiny probe, so it barely affects the weighted score. This is
not only a probe issue: IP AA in `test-eight-open-03` has 12.23% compatible
range mass, and its prediction is 21.81bb against a 30.94bb reference. Values
can exceed the starting pot because they include future betting.

Reference quality also has limits. Average best-response gains are about
0.082–0.093% of pot, while the largest reported probe gain is 1.049%. The
equity-control-variate reference totals differ from 100% of pot by up to
0.198 percentage points; these are sampled estimators, not individual solved
pot-accounting failures. Candidate totals conserve the pot to numerical
precision. Only two independent source families were tested, and the intervals
do not include uncertainty from training or the cached equity estimates.

## Recommended next experiment

1. Keep this candidate frozen as the benchmark. Add targeted training coverage
   for underrepresented premium hands and the kinds of ranges that regressed.
   Test revised models on new source games and new boards; these test cases
   are now known and cannot serve as a fresh unbiased test after tuning.
2. In a separate experimental build, compare preflop call/raise/fold values and
   resulting strategies in the original blind-defense and early-position spots.
   Check whether better average continuation values improve the decisions the
   user actually cares about, including rare branches. Keep the live model
   unchanged during this comparison.
3. Measure GPU time to the same convergence target and memory use. This study
   contains no evidence of faster preflop solving. Broader sizing, rake and
   multiway coverage remain separate requirements before general deployment.

The rendered comparison graph was inspected: all six bar values match the
evaluation, labels and legend are readable, the axis starts at zero, and its
caption states the fixed-menu, zero-rake heads-up limitation.

Validation evidence is retained under [validation](validation/validation.json).
The solver preflight passed 193 tests with five ignored; both GPU suites passed
(6 postflop and 15 preflop); the final research pipeline suite passed 11 tests.
The full reference/artifact audit passed. The original 2,122-reference batch
remains excluded.

No production deployment or server restart was performed. At final inspection,
56708 had no listening socket and no `gto-server.exe` process was found. The
earlier Windows Update interruption is recorded in the recovery notes; the
research completion does not imply that the desktop app is currently running.
