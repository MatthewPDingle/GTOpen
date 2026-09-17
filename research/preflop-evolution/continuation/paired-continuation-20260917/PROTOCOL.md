# Connected continuation-value correction pilot

Research only; production port 56708, defaults and binaries remain unchanged.

The completed original heads-up audit and shallow-native feedback audit become
development data. Their previous test status is explicitly retired for this
candidate. Use both players' settled postflop values from called opens, called
3-bets and called 4-bets; preserve their board weights and per-hand quality gates.

Fit 18 centered polynomial features as an additive residual to the frozen
shallow/N15 baseline. The features and shared physical-bound shrink preserve
legal-pair-weighted pot conservation. Minimize the sum of a leaf loss in pot
fractions and a backed-up call-versus-3-bet loss divided by a fixed 5bb scale.
Consider ridge penalties 0.0001, 0.001, 0.01 and 0.1, and action-loss weights
0, 1 and 4. Select by leave-one-policy-family-out adjusted action MAE, requiring
mean leaf MAE within 5% of baseline in both estimators in each held-out family.
Ties favor stronger regularization, then smaller action weight. The final model
uses both development families and is frozen before any new references run.
This small development set is a pilot, not comprehensive range coverage.

Test two new, coherently perturbed policy trees. One tempers the original policy
to exponent 0.8; the other tempers the shallow policy to 0.9 and applies a mild
hand-strength tilt between calling and raising. Recompute reaches from the
perturbed action probabilities. No illegal actions are added and no new preflop
equilibrium is claimed. These are unseen perturbations of known policy families,
not evidence of generalization to arbitrary tables or independent real players.

Solve the same 20 stratified boards in all six test contexts (120 solves), seed
paired-continuation-test-v1, four per stratum. Sample the full canonical-board
population; overlap with development boards is allowed but exact test ranges
and labels are new. Keep the established finite postflop action menu, zero rake,
40bb preflop stack, CPU/GPU gaps <=0.1% pot, and 2,000 iteration ceiling.

Keep individual-action support >=0.0001 and propagated per-hand BR gain <=0.025bb
for the call-versus-3-bet comparison. Leaf gates use gain <=0.005 pot. Report
excluded classes and qualified mass. Bootstrap 5,000 times within strata with
seed 2026091705, preserving paired boards across all contexts and families.

Advance to a new native integration experiment only if, in BOTH test families:
adjusted action MAE falls >=10%, direct action MAE does not regress, qualified
decision mass is >=20%, and mean leaf MAE does not worsen >5% in either estimator.
Additionally require the pooled adjusted error-reduction 95% interval to be
strictly positive. Do not change gates, add samples or refit after seeing results.
Passing is permission for another research stage, not production deployment.

Before references, verify exact-leaf action reconstruction, null correction,
pot conservation, physical bounds, and recovery of a known synthetic residual.
After references, independently reconstruct complete-tree action values and
record all input, model and label hashes. Failures remain visible.
