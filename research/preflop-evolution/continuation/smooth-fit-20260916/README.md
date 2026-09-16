# N22: sensitivity-regularized fitting

Hypothesis: the current range-conditioned predictor responds strongly to small
range changes, which may contribute to slow preflop settling. Sensitivity alone
does not prove error or causation. Test a training change; do not damp runtime
values or modify convergence stopping thresholds.

Use only the original 24 training contexts plus the two development contexts.
Exclude each entire source family when validating. Keep all N15 features,
normalization, two width-8 neural residuals, seeds 90210/20260916, 500 Adam steps,
learning rate .01, output penalty .1, parameter penalty .001 and final .75
residual shrinkage unchanged. Refit the neural residual to each newly fitted
linear base. All fitting uses CPU float64, OpenBLAS one thread, Torch two.

Add a positive-semidefinite sensitivity penalty to the linear ridge system.
For each fitting context, separately mix each player's normalized range 1%
toward premium pairs (TT-AA), offsuit broadways or suited connectors with rank
gap <=2. Recompute all features and compatible masses. The penalty is the
mean original-mass-weighted squared derivative of the *centered correction*,
using actual range total variation as the denominator. This penalizes extra
learned sensitivity, not raw equity's legitimate change. It uses no labels
from perturbed ranges. Three fixed strengths: .0001, .001 and .01; control 0
must reproduce N15's existing validation values within 1e-9. No adaptive grid.

Validation sensitivity uses the same prescribed directions on the held-out
training family, after all fitting. Eligibility requires mean and every-family
value error at most 5% worse than N15, at least 5% lower mean error than the
original linear control, at least 25% lower mean local sensitivity than N15,
and no family with greater local sensitivity than N15. Sensitivity is mean
original-compatible-mass absolute predicted-value change divided by actual
range total variation, averaged over all six directions. Family means receive
equal weight. Among eligible strengths choose the lowest mean value error.
No rounding of thresholds; retain all failed results.

Freeze this protocol and implementation before fitting. If a strength passes,
fit it on all 26 training/development cases and freeze the model. Its inference
shape stays identical, but that does not itself prove GPU correctness, runtime
or convergence. It requires separately registered fresh-board accuracy,
numerical checks, repeated GPU timing and changed-policy/convergence evidence
before deployment. Existing N15/N20 test outcomes cannot select this strength.
No production edits. Respect the existing 20:49:02 UTC deadline; CPU fitting
may accompany reference generation but never isolated GPU speed measurements.
