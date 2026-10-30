# More evaluation deals alone would be expensive

The completed dense and hybrid evaluations do not yet distinguish modest
improvements reliably. Their learned-response gain intervals have half-widths
of about 1.38 and 1.70 bb respectively. This matters independently of training:
a model can change substantially while the evaluation remains too noisy to
establish whether that change helped.

A new descriptive calculation reconstructs all five means and variances from
both completed test streams, then plugs those observed variances into the
existing registered interval formula. It does not draw new deals, alter either
result, change a stopping rule or train a policy.

## Planning estimates for the learned-response comparison

| Desired interval half-width | Dense: test deals / estimated evaluation hours | Hybrid: test deals / estimated evaluation hours |
|---|---:|---:|
| 0.50 bb | 69,247 / 0.9 h | 107,397 / 1.6 h |
| 0.25 bb | 206,666 / 2.6 h | 353,000 / 5.2 h |
| 0.10 bb | 1,003,903 / 12.8 h | 1,899,223 / 28.2 h |

These are **planning calculations, not guaranteed future precision, power or
completion times**. They assume the observed variance and throughput persist,
and exclude CPU-reference preparation, response training for a new evaluation,
and final audits. Candidate behavior, caching and hardware load can change the
cost. The 0.10 bb row is an illustration, not an adopted strategic success
threshold. Even a narrow interval here is not a full best-response certificate.

## Most observed variation is within hand classes

For the learned-response paired differences, the exact empirical sum-of-squares
decomposition attributes 95.8% of the dense sample's variation and 94.5% of the
hybrid sample's variation to differences **within** starting-hand classes.
This combines opponent-card and board variation; it does not isolate them.
The class means are themselves noisy. These fractions are not population
variance estimates or a validated stratified evaluation design.

The result cautions against expecting an order-of-magnitude improvement merely
from giving every starting-hand class equal sample counts. Better per-class
coverage can still be valuable, but it does not directly remove the large
within-class payoff variation observed here.

## Candidate next step, separate from active training

After the registered all-in training experiment finishes, investigate whether
exact conditional preflop-all-in values can also reduce **evaluation** variance.
For a fixed private-card pair, preflop action probabilities do not depend on the
future board, so that terminal component can potentially be averaged exactly.
The remaining postflop continuations must retain their actual strategies and
card sampling; they must not be replaced by raw showdown equity.

Such an evaluator needs its own native/reference checks, a demonstrated
expectation-preserving decomposition, correct pot/rake accounting, and measured
variance and cost on a separately labelled control. Reducing one component's
variance does not automatically reduce the variance of the complete paired
difference, because components may covary. Any new confirmation requires a
registered fresh stream and fixed statistical rules. The active trial's original
evaluation stays unchanged.

Evidence: `sampled-root-evaluation-precision-diagnosis-v1-result.json` records
all reconstructed series, source hashes, the exact within/between decomposition
and the numerical sample-count calculations. It makes no new confidence claim.
