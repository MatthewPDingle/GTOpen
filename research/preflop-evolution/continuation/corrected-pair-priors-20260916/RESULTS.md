# N11 result: rejected at the training screen

Adding the fixed residual correction did not improve N09. Equal-family mean
hand-value error was **10.382% of pot**, versus **10.223%** for N09 and
**14.998%** for ordinary Balanced. That is 30.8% lower than Balanced but 1.55%
worse than N09. The worst family became **10.65% worse than N09**, exceeding
the fixed 5% limit. No final candidate or GPU workload was created.

| Excluded training family | Balanced | N09 | N11 |
|---|---:|---:|---:|
| Eight-player equal blinds | 22.827 | 14.583 | 14.465 |
| Eight-player straddle | 10.760 | 10.812 | 10.942 |
| Seven-player open | 14.835 | 7.568 | 8.375 |
| Six-player modeled | 11.570 | 7.928 | 7.745 |

Both fitting stages excluded the entire validation family. The refitted N09
controls reproduced all 26 previously recorded case errors within 1e-9.
This prevents the second stage from benefiting from a prior model trained on
its validation cases. These remain training-selection results, not prospective
accuracy or full-game equilibrium evidence.

Two additional tests passed: equality of combined and separate predictions
with pair complementarity and pot accounting, and isolation of both fitting
stages to the supplied cases without changing the original targets. N10's
three arithmetic/recovery tests cover the additive component.

The specification and implementation were committed as `bf94639` before fitting.
See [frozen inputs](implementation-freeze.json) and
[complete results](training-screen.json). N09 remains the eligible cached-table
candidate; this failed correction will not change it or its pending evaluation.
