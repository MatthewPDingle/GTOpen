# N11: fixed residual correction to cached pairwise priors

Specified after the N10 training result and before this fit. No prospective
evaluation outcomes have been generated or inspected for this candidate.

N09's nonlinear relative-share formula and N10's additive transfer make different
training errors. Test one two-stage composition: fit the unchanged N09 positive
priors, then fit the unchanged N10 additive hand/position adjustments to the
remaining training residual. Both stages use only the same allowed training
families in each fold. In particular, never use the full-data N09 candidate to
predict an excluded training-validation family.

Retain N09's 600 Adam steps, learning rate 0.02 and penalty 0.001. Retain N10's
ridge penalty 0.01 and compatible-mass normalized, equal-context objective.
No joint optimization, parameter search, coefficient clipping or extra blend
weight. Both components share `min(SPR / 8, 1)`. The final pair table is N09's
relative share plus `a[h]-a[j] +/- (b[h]+b[j])`. Complementary pair values and
whole-pot accounting remain mandatory. This composition can be precomputed;
GPU cost is a hypothesis until independent arithmetic and timing checks pass.

Use the original 26 training/development contexts, excluding entire source
families in all four folds. Require at least 5% lower equal-family mean error
than N09, at least 15% lower than Balanced, and no family more than 5% worse
against either control. Reproduce N09's recorded excluded-family predictions
before using them as a control. Do not change gates or model after outcomes.

If eligible, refit both stages on all 26 contexts and freeze. Register for
fresh evaluation before any corresponding reference generation. Sharing the
reserved N03/N09 reference queries is allowed only if that temporal separation
still holds; otherwise use a new disjoint draw. Fresh accuracy, GPU arithmetic,
runtime and changed-policy checks are separate prerequisites. No production
deployment is authorized, and the original night-shift deadline is unchanged.
