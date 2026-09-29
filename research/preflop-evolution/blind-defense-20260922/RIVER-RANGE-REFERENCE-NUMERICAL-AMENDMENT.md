# Preserve the v1 subnormal-weight failure and qualify v2

After v1 passed its original six-case control, an extra adversarial check found
a numerical error on the retained board-only royal flush. One opponent holding
had the smallest positive float64 weight (approximately4.94e-324). There were
990 supported hero holdings, all tied. V1 returned equity0 instead of0.5:
multiplying the tie mass by0.5 before normalization underflowed to zero.

V1 and its original passed control are retained unchanged. Their passing result
covers the registered cases, not this newly identified numerical boundary.
Do not use v1's payoff calculation in a future range-conditioned study.

V2 inherits the nonnegative outcome-mass sums but normalizes each outcome mass
by compatible total mass before applying the half-tie share. It rejects
nonfinite accumulated mass or public payoff instead of returning a prediction.

Repeat the original12 retained boards and six cases, adding smallest-positive
single-hand and uniform weights. Check the latter directly against the original
integer outcome counts divided by990, and the former against the scalar rank
comparison with the one opponent hand. Reproduce and record v1's royal-flush
failure. For the smallest weights, test doubling rather than scaling down to
an unrepresentable zero. All other settings, tolerances and resource caps stay
as in RIVER-RANGE-REFERENCE-PLAN.md. Fix the independent expected-payoff arithmetic
to average normalized outcomes, with the new discrete-outcome checks preventing
the original shared underflow mistake.

This is correction of a mathematical primitive on reused probe data. It does
not change the queued learning experiment, train a model, inspect its new test
labels, or qualify the real-policy reach-vector binding.
