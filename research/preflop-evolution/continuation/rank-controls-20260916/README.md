# N07: rank-event controls for reference-label precision

Specified before running this diagnostic, 16 September. Existing models and
reference labels stay immutable. No evaluation labels or application changes.

Twenty-board subsets of the 100-board training data differ from the full
sample by about 5% of pot on average. Test eight cheap rank-event controls:
flop hits the high hole-card rank; hits it twice or more; hits the low rank;
hits the low rank twice or more; has an overcard to the high rank; has two or
more overcards; has any paired rank; has trips. Low-rank features are zero for
pocket pairs. No suit or hand-equity feature is added.

For each compatible pair of private hand classes, calculate exact feature
expectations over the remaining 48 cards with hypergeometric counting. Suit
compatibility enters through the existing exact compatible-combination matrix.
Average over the opposing range conditional on the player's hand class.
Validate these moments independently by enumerating physical flops for
representative concrete private-card pairs, including rank overlap.

Fit eight slopes separately for OOP/IP and pair/suited/offsuit hand groups.
Within each case and hand, center features and existing EV-minus-equity labels
over sampled boards before fitting. Use compatible-mass-weighted least squares
with ridge 0.01 times mean diagonal feature covariance. Exclude the entire
target source family when fitting slopes. No hyperparameter search.

Adjust each sampled board residual by subtracting beta times its feature
deviation from the exact conditional feature mean. Compare the dispersion of
200 fixed stratified 20- and 50-board subsets with their respective full
100-board estimates, before and after adjustment. Use the same subsets in each
comparison; retain missing-mass and full-label-shift diagnostics. Do not silently
recenter, clamp or replace existing labels.

This is a finite-population variance diagnostic, not accuracy versus exact
all-flop truth. Source families share board identities; fitted slopes are not
independent of the historical board population. Ratio denominators are sampled,
so exact control means alone do not prove finite-sample unbiasedness. Any
benefit needs a fresh-board validation before changing data generation or
model training. A promising result requires at least 20% lower subset
deviation in each training family for both sample sizes. If it fails, retain
the failure; do not alter the controls or gate based on these outcomes.
