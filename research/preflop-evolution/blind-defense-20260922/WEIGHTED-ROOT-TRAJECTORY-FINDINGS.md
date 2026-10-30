# Complete training histories: coverage improved, movement remains

The independent CPU trajectory analysis finished in 34.7 seconds using two
workers alongside the start of the GPU evaluation. No new deals, training or
production changes were made. Its result is weighted-root-trajectory-v1-result.json.

All four arms have 39,936 root samples. The stratified sampler removes the
missing-class updates of the baseline: every class receives at least three
observations in each generation. That is the intended coverage improvement.

| Arm | Final samples per class, min / median / max | Mean classes missed per update | Middle-to-last window TV | Mean update TV, last 26 |
| --- | ---: | ---: | ---: | ---: |
| 9266201 baseline | 91 / 178 / 405 | 18.88 | 12.14% | 1.84% |
| 9266201 stratified | 234 / 236 / 241 | 0 | 15.04% | 2.11% |
| 9266301 baseline | 82 / 185 / 420 | 19.04 | 16.37% | 2.36% |
| 9266301 stratified | 234 / 236 / 241 | 0 | 13.87% | 2.03% |

These movement diagnostics are mixed: one stratified seed moves more than
its baseline and the other less. Better coverage alone has not clearly
stabilized learning. Missing baseline classes represent about 6.3-6.4% of the
original entry mass in the average update. Differences in final visit counts
are expected under the two sampling laws; importance weights, not equal raw
counts, preserve the original objective.

The final current policy differs from its played-history average by 12.08%,
14.07%, 12.15% and 12.75% TV in the table's order. The unplayed final generation
is used only for this movement diagnostic and remains excluded from the
evaluation bank. Reconstructed played averages agree within 3.331e-16.

TV here describes the class-weighted amount of action probability moved; it
is not exploitability, win rate or a convergence certificate. These results
motivate the separately tested lower-noise board estimator, but do not prove
that it will produce stronger play. The registered fresh-data payoff evaluation
and its final review are still required before interpreting the main study.
