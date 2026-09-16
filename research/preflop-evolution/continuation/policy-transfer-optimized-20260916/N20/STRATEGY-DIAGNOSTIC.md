# Equal-work strategy diagnostic (N20)

Equal work is not equal solution quality. These descriptive frequencies are not an accuracy comparison, a GTO Wizard comparison or converged ranges. Gaps freeze the range-dependent continuation values.

At 500 iterations the ordinary path has summed frozen-value gap **0.004809 bb**, versus **0.090492 bb** for the candidate. This raises an unresolved time-to-stability concern; the roughly 6% per-iteration overhead is not a demonstrated solve-time overhead.

The candidate reduces calling in several blind/straddle contexts. Wider calling alone is not an accuracy criterion. The separately registered N19 trajectory and independent reference values are needed to interpret these changes.

All frequencies below are percentages, shown as ordinary -> candidate. UTG is the posted straddle in this configuration; the first voluntary actor is UTG1. Intervening actions in the response rows are folds.

| Actor | Situation | Fold | Call | Raise / 3-bet |
|---|---|---:|---:|---:|
| UTG1 | First in | 85.44 -> 85.23 | - | 14.56 -> 14.77 |
| MP | First in | 83.13 -> 82.95 | - | 16.87 -> 17.05 |
| HJ | First in | 79.99 -> 80.16 | - | 20.01 -> 19.84 |
| CO | First in | 75.21 -> 75.63 | - | 24.79 -> 24.37 |
| BTN | First in | 68.62 -> 68.51 | - | 31.38 -> 31.49 |
| SB | First in | 62.48 -> 64.20 | - | 37.52 -> 35.80 |
| BB | First in | 42.84 -> 40.51 | - | 57.16 -> 59.49 |
| SB | After BTN Raise 6 | 84.54 -> 84.19 | 9.00 -> 8.91 | 6.46 -> 6.90 |
| BB | After BTN Raise 6 | 70.66 -> 73.43 | 22.08 -> 19.04 | 7.26 -> 7.53 |
| UTG | After BTN Raise 6 | 53.07 -> 64.03 | 38.39 -> 25.52 | 8.54 -> 10.45 |
| MP | After UTG1 Raise 6 | 93.71 -> 94.19 | 2.48 -> 0.53 | 3.81 -> 5.28 |
| HJ | After UTG1 Raise 6 | 92.84 -> 93.58 | 3.21 -> 1.34 | 3.95 -> 5.08 |
| CO | After UTG1 Raise 6 | 92.41 -> 93.15 | 3.61 -> 1.36 | 3.98 -> 5.49 |
| BTN | After UTG1 Raise 6 | 91.15 -> 92.69 | 4.72 -> 1.46 | 4.13 -> 5.85 |
| SB | After UTG1 Raise 6 | 90.85 -> 91.38 | 5.47 -> 4.41 | 3.68 -> 4.21 |
| BB | After UTG1 Raise 6 | 83.57 -> 86.83 | 12.63 -> 9.35 | 3.80 -> 3.82 |
| UTG | After UTG1 Raise 6 | 69.70 -> 79.56 | 26.27 -> 16.76 | 4.04 -> 3.68 |

## KQo in blind and straddle response nodes

| Actor | Situation | Ordinary call | Candidate call |
|---|---|---:|---:|
| BB | After BTN Raise 6 | 99.98% | 99.92% |
| UTG | After BTN Raise 6 | 8.94% | 42.54% |
| BB | After UTG1 Raise 6 | 99.97% | 77.29% |
| UTG | After UTG1 Raise 6 | 100.00% | 99.99% |

The entire strategy comparison, source hashes and all prespecified hand probes remain in the adjacent JSON artifacts.
