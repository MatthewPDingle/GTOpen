# N05: train the same pot-conserving function that inference evaluates

Specified 16 September 2026 before this screen is run. Offline research only.
Port 56708 and all previous datasets, protocols and models remain unchanged.

The existing ridge fit minimizes uncentered per-hand residual errors; inference
then removes the compatible-mass mean of the predicted residual to conserve the
pot. This changes the function being optimized. Instead, project each case's
104 feature columns to zero compatible-mass mean before fitting. Keep the same
targets, case weights and feature encoder. The existing inference formula can
evaluate the resulting coefficients with no extra work because projection
commutes with the linear predictor. An independent numerical test must verify
that equivalence, including unequal and concentrated range masses.

Use only the original 24 training cases plus the two N01 development cases.
Require no positive compatible mass on unobserved labels. Leave each of the
four entire source families out in turn. Fixed penalties: 0.03, 0.1 and 0.3.
Score equal-family mean hand-value MAE against the unchanged ordinary
shape/0.1 fit on the same 26 cases. Select the lowest-error candidate only if
it reduces mean error by at least 5% with no family more than 5% worse.
Retain rejected candidates and results; do not expand the grid from outcomes.

This is a training-only selection screen. If eligible, freeze a 26-case model
and its hashes before choosing and generating any new prospective evaluation
references. Never evaluate or select using N01 test results or N03 reserved
evaluation labels. No candidate is deployed from this screen alone. Any later
evaluation requires a separately recorded protocol, new boards, an independent
GPU inference check and matched runtime measurements. No inference speedup is
claimed from algebraic equivalence alone.
