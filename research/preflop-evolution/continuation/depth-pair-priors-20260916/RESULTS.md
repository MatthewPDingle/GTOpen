# N12 result: below the fixed improvement requirement

Depth-dependent cached priors reduced equal-family mean hand-value error to
**9.809% of pot**, versus **10.223%** for N09 and **14.998%** for Balanced.
That is a **4.05%** improvement over N09, below the predeclared **5%** threshold.
The worst family was 3.60% worse than N09, within the 5% family limit. The
mean requirement still failed: no final candidate was frozen or evaluated.

| Excluded training family | Balanced | N09 | N12 |
|---|---:|---:|---:|
| Eight-player equal blinds | 22.827 | 14.583 | 15.109 |
| Eight-player straddle | 10.760 | 10.812 | 9.814 |
| Seven-player open | 14.835 | 7.568 | 7.155 |
| Six-player modeled | 11.570 | 7.928 | 7.160 |

These are original-data training-family selection results, not independent
accuracy or full-game convergence evidence. Two tests passed for interpolation
endpoints/midpoints, reduction to N09 when the depth slope is zero, complementary
pair values and compatible-mass pot accounting. No GPU timing was performed.

Protocol and implementation were committed as `4e094fc` before fitting. See
[frozen inputs](implementation-freeze.json) and [all results](training-screen.json).
The [separate N12b repeat](../depth-priors-expanded-20260916/README.md) keeps all
settings fixed and asks whether the already-running expanded data collection
helps. N12b does not change this outcome or loosen any threshold.
