# Make the broader call/raise test more informative

23 September 2026. This is preparation using an already inspected old study,
not a new accuracy result and not an evaluation of the running averaging trial.

## What changed in the calculation

A first-action deviation's gain can be separated into an exactly known fold/
shove contribution plus a sampled call/raise contribution. The complete private-
pair equity table supplies the former. Only the latter needs new test runouts.
This preserves the expected value and avoids repeatedly sampling quantities
that can already be calculated exactly.

The implementation also supports subtracting a hand-class prediction fitted
only on the independent response-training sample and adding its exact population
expectation back. This optional centring changes variance, not the target value.
Its centre, responder and physical bounds must be frozen before future test draws.

## Completed old-sample diagnostic

All 8,192 training and 16,384 test deals from the completed combined 269-input
candidate were retained. Its original responder and all five comparisons were
unchanged. Full class masses and fold/shove values came from that same candidate's
separately audited complete exact endpoint calculation. No current training
output, new deal, GPU inference or policy selection was used.

| Fixed comparison | Residual / original sample variance | Change |
| --- | ---: | ---: |
| Original fitted response | 0.3124 | 68.8% lower |
| Always fold | 0.5219 | 47.8% lower |
| Always call | 0.5735 | 42.6% lower |
| Always raise | 1.1151 | 11.5% higher |
| Always jam | 0.0436 | 95.6% lower |

Removing sampled components can remove beneficial covariance as well as noise;
it does not guarantee a variance reduction for every alternative. The optional
class centring reduces the fitted-response residual variance by only a further
0.32% here. Neither version establishes that the old policy was accurate.

Using the old fitted-response variance and the existing conservative five-test
formula for planning, the uncentred residual would require approximately 43,615
deals for a 0.50 bb radius, 111,847 for 0.25 bb, or 441,239 for 0.10 bb. These are
**hypothetical counts**, not achieved confidence intervals or an adopted budget.
They assume this variance persists under a future frozen candidate and test.
For perspective, its hypothetical radius at the old 16,384 count is 1.089 bb,
compared with the original 1.448 bb radius: a useful reduction, still too broad
for fine distinctions. The always-raise comparison would be slightly worse.

The means and all alternative calculations are recorded in the result JSON for
reproducibility, but are explicitly post-hoc estimates, not fresh confirmation.
Sampling uncertainty remains in ordinary calls, raises and their continuations.

## Verification and next decision

Synthetic finite-population controls checked seven response policies with and
without centring, including unchanged play, unequal population probabilities,
missing centre-training classes and every call/raise payoff corner. The exact
expectation identity held within 1.78e-15 bb. Invalid classes, nonfinite values,
invalid policies and values outside physical bounds were rejected.

The independent old-data review reconstructed training-only centres, all 16,384
residuals per comparison, physical bounds, sample variances and minimum projected
counts using scalar sums. Maximum discrepancy was 1.14e-13. Original reported
statistics were reproduced before the estimator comparison. These checks took
seconds and did not use the GPU occupied by the fresh training run.

If the averaging trial passes its exact screen, the next wider evaluation should
combine the exact contribution with materially better per-class response-training
coverage. A larger test alone cannot fix an unstable fitted responder. Freeze
the method, candidate, responder, sample count and intervals before drawing fresh
test deals. Do not import these inspected means as fresh evidence or promise
the same variance reduction for the new candidate.

Evidence: `root-residual-control-v1-{registration,result}.json` and
`root-residual-diagnostic-v1-{registration,result,independent-review}.json`.
The reusable arithmetic is `tools/research/root_residual_evaluation_v1.py`.
Production and the running experiment are unchanged.
