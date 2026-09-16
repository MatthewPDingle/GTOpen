# N09: cheap recalibration of relative hand priors

Declared before fitting this experiment. CPU-only screening runs alongside N03
reference generation, with no changes to the application or shared fit cache.

Hypothesis: some continuation-value error comes from the older class adjustments,
which were not fitted to this zero-rake reference set. Relearn 169 positive class
priors while retaining the pairwise relative-equity formula. This has no 104-feature
conditional predictor at inference; its pairwise matrices can be cached. A cheap
formula does not establish actual GPU speed, which must be measured separately.

Use the original 24 training cases plus the two N01 development cases. Exclude
whole source families for cross-validation. Do not use any historical evaluation
labels or N03 outcomes. The target remains per-hand gross EV / pot, estimated
using the existing equity control variate. Do not clip training targets or scores.

For a pair of classes h,j, replace the equity share with
e[h,j] * q[h] * position / (e[h,j] * q[h] * position +
(1-e[h,j]) * q[j] * opposite_position).
Position factors stay fixed at 0.92/1.08. Blend with raw equity by min(SPR/8,1).
Average over exact compatible opponent-class counts. Both players therefore
conserve the pot under the same compatible-pair measure. This differs from the
original application's independent-class aggregation, which remains a separate
reported baseline. No folded-card bunching or multiway correctness claim follows.

One fixed fit: q = old_q * exp(delta - mean(delta)); initialize delta to zero;
600 full-batch Adam steps, learning rate 0.02, float64, CPU, two threads. Minimize
compatible-mass-weighted squared error plus 0.001 * mean(centered_delta^2).
No candidate grid, early stopping, validation-based epoch choice or outcome-based
adjustment. Retain the full per-family and per-case results even if rejected.

Gate: at least 5% lower equal-family mean error than unchanged priors evaluated
with the same compatible-pair calculation, and no family more than 5% worse;
also at least 15% lower mean error than original Balanced, with no family more
than 5% worse. Passing selects one model for separate prospective evaluation;
it does not permit deployment. The earlier learned predictor is reported as
context, not used to fit or select this candidate.

If eligible, freeze the model before any new evaluation reference generation.
It needs new-board accuracy, GPU arithmetic, repeated timing and changed-policy
checks within the remaining window. It cannot join the already frozen N06b/N08
evaluation protocol. Keep port 56708 and cache/realization_fit.json unchanged.
