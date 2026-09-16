# N10: cached additive pair-value adjustments

This specification precedes N10 fitting. It follows N09's training-family
screen, but uses no evaluation outcomes. This is an isolated accuracy and
runtime candidate, not a production change.

## Fixed model

For each ordered pair of hand classes h and j, use cached preflop equity plus
`a[h] - a[j] + sign * (b[h] + b[j])`, where sign is -1 for OOP and +1 for IP.
The two sides' values complement exactly. Average over the actual compatible
opponent holdings, then blend the adjustment by `min(SPR / 8, 1)`.

The 169 a coefficients describe hand-dependent continuation value; the 169 b
coefficients describe the positional transfer. Unlike a probability ratio,
the expression can represent winning additional money through future bets.
It is an approximation to value, not a probability of winning. No output
clipping or extra softening is applied. Report extreme values explicitly.
Pair tables can be cached with the same size and inner loop as N09; that is
a runtime hypothesis until separately measured.

Fit exactly one ridge model on the original 24 training contexts plus the two
N01 development contexts. Each context has equal weight; within it use exact
compatible hand-pair mass, masking unobserved target cells and normalizing the
remaining weight. The objective is mean squared residual error plus
`0.01 * (mean(a^2) + mean(b^2))`. Center a after fitting to remove its irrelevant
constant. Use float64 CPU least squares. No parameter grid, N03 training data,
validation-label tuning or reuse of an already fitted N09 model.

## Selection and subsequent evidence

Exclude each entire source family for the four training-validation folds.
Compare equal-family mean absolute errors with ordinary Balanced and the
already recorded, family-excluded N09 predictions on the same 26 cases.
Eligibility requires at least 15% lower mean error than Balanced and at least
5% lower than N09, with no family more than 5% worse against either control.
Do not round thresholds. Retain a failed result without widening the grid.

If eligible, fit all 26 contexts and freeze before prospective evaluation.
It may share the N03/N09 reserved evaluation references only if its candidate
and evaluation registration both precede every one of those reference solves.
Otherwise a separately reserved, disjoint reference set is required. Fresh
accuracy, independent GPU arithmetic, repeated timing and changed-policy
validation remain prerequisites to considering use in the app. A training
screen alone is insufficient. The night-shift deadline remains unchanged.
