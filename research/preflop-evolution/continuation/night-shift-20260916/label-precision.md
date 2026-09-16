# Flop-sampling precision diagnostic

Subset versus full 100-board training labels; not error versus exact all-flop truth, not an irreducible error floor or model-selection score.

200 deterministic without-replacement stratified subsets, 4/10/20 boards per each of 5 strata; paired ratio estimator, equity control variate; original targets unchanged.

| Training family | Model family-CV error | 20-board subset deviation | 50-board subset deviation |
|---|---:|---:|---:|
| train-eight-equal | 8.116 | 4.824 | 2.457 |
| train-eight-straddle | 7.487 | 4.912 | 2.461 |
| train-seven-open | 5.522 | 4.934 | 2.471 |
| train-six-modeled | 6.433 | 5.072 | 2.537 |

All figures are compatible-mass-weighted mean absolute deviations as a percentage of starting pot. The model column uses family-withheld predictions on the same 26 training cases. The other columns compare subsets with their containing 100-board sample, so their errors are correlated. They do not estimate the exact uncertainty of a separate 20-board sample or the full 100-board labels.

No evaluation labels were read; no model, threshold or reference changed. This diagnosis guides later data collection. N03 remains on its original 20-board-per-context protocol. Per-case intervals, missing hand mass and range-average reference BR gains are in [the JSON record](label-precision.json).
