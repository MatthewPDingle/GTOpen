# N12: depth-dependent cached pairwise priors

Specified before fitting. The original 26 training contexts span SPR 1.56 to
19.5, but N09 uses the same adjusted relative-share table whenever SPR is at
least 8. Test one fixed extension that permits hand adjustments to change with
remaining stack depth. Neither N03's new training outcomes nor prospective
evaluation outcomes are used in this experiment.

At knots SPR = 1, 2, 4, 8, 16, 20, form positive priors
`old_prior[h] * exp(d0[h] + log(SPR/8) * d1[h])`. Center d0 and d1 separately.
Construct the same complementary OOP/IP relative-share matrices as N09 at
each knot. Interpolate the two adjacent matrices linearly in log SPR, then
apply the unchanged `min(SPR/8, 1)` blend with raw equity. Outside the knot
interval, clamp the table lookup; prospective deployment remains restricted
to the existing SPR 1..20 interface. No output or coefficient clipping.

Fit on the original 24 training contexts plus the two N01 development contexts.
Use exactly 600 float64 CPU Adam steps, learning rate 0.02, the same
compatible-mass MSE as N09, and penalty `0.001 * mean(d0^2) + 0.01 * mean(d1^2)`.
Both vectors start at zero. There is no parameter grid or epoch selection.
The slope penalty is fixed stronger than the intercept penalty to discourage
unsupported depth trends. Six tables occupy approximately 1.37 MB; inference
requires two table reads instead of one. Runtime benefit is unmeasured.

Exclude each entire source family for four training-validation folds. Compare
on the identical original 26 cases with the recorded N09 fold results and
ordinary Balanced. Require at least 5% lower equal-family mean error than N09,
at least 15% lower than Balanced, and no family more than 5% worse against
either. Keep a failure without changing knots, penalties or thresholds.

If eligible, refit all 26 contexts and freeze, then register before any relevant
fresh reference outcomes exist. Sharing N03/N09's future queries requires
registration before their generation; otherwise select a new disjoint draw.
GPU arithmetic, measured runtime, and changed-policy validation are still
required. This does not deploy anything or extend the ten-hour window.
