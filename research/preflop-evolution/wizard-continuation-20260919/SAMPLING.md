# Small-panel sensitivity

Earlier continuation experiments used small board panels. To assess how sensitive labels can be, this exploratory diagnostic takes 5,000 different ten-flop subsets (two per stratum) from the completed forty-flop study. No solver was rerun and no extra board outcomes were acquired.

The numbers below are the median absolute change from the forty-flop estimate, in bb. This is not an error estimate against the true value, an independent test, or a confidence interval. It measures instability from choosing a smaller panel within these observed boards.

| Hand | 50% menu direct | 50% menu equity control | 75% menu direct | 75% menu equity control |
|---|---:|---:|---:|---:|
| AA | 4.19 | 3.81 | 4.50 | 4.09 |
| A5s | 1.71 | 0.91 | 1.57 | 0.86 |
| KQo | 2.51 | 1.42 | 2.54 | 1.59 |
| QJs | 2.14 | 1.42 | 2.08 | 1.40 |
| 99 | 4.58 | 3.43 | 5.08 | 3.74 |
| 88 | 5.61 | 3.72 | 5.87 | 3.98 |
| 55 | 4.01 | 2.61 | 4.06 | 2.73 |
| 76s | 3.94 | 2.48 | 4.08 | 2.63 |

This supports measuring label precision before treating small differences as training targets. Equity control helps some hands but does not eliminate the effect of uncommon high-value boards. This diagnostic alone cannot attribute the previous models' transfer failures to sampling noise: those studies used different ranges, boards and targets.
