# N10 result: rejected at the training screen

The cached additive-value model did not improve on N09's recalibrated pairwise
priors. Equal-family mean hand-value error was **10.351% of pot**, versus
**10.223%** for N09 and **14.998%** for ordinary Balanced. That is 31.0% lower
than Balanced, but 1.25% worse than N09. Its worst family was **25.9% worse than
N09**, exceeding the fixed 5% limit. No final candidate was fitted or frozen,
and no GPU integration or prospective reference work was launched for N10.

| Excluded training family | Balanced | N09 | N10 |
|---|---:|---:|---:|
| Eight-player equal blinds | 22.827 | 14.583 | 12.404 |
| Eight-player straddle | 10.760 | 10.812 | 10.922 |
| Seven-player open | 14.835 | 7.568 | 9.530 |
| Six-player modeled | 11.570 | 7.928 | 8.547 |

All entries are mean absolute hand-value error as a percentage of the starting
pot. These are training-family selection results, not independent accuracy or
equilibrium evidence. Each entire family was excluded from that fold's fit.

The implementation passed three CPU checks: complementary pair values and
pot accounting; recovery of known synthetic values on unseen ranges; and
invariance to an irrelevant constant hand offset with no hidden clipping.
They test arithmetic and fitting mechanics, not realism. Runtime was not
measured because the accuracy selection gate failed.

The fixed protocol and implementation were committed as `8617dd9` before the
fit. [Frozen inputs](implementation-freeze.json) and
[complete training results](training-screen.json) retain provenance and
per-case extremes. The parameter set will not be widened against these results.
