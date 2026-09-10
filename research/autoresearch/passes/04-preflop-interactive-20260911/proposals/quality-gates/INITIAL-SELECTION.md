# Frozen first candidate

`coupled_subset_herding_v1_64` is frozen from `raw/ensemble-audit-a.log` before independent output inspection. Exact indices and source SHA are in `frozen-herding64.json`; that manifest's SHA-256 is `a772dc61b470ec01e32d26908f6eb7b7a7528471be6fcfd7fe8e44b04bda979c`.

Seen-regression results for64: core physical MAE1.5856pp, worst5.2998pp, maximum case mean2.3145pp; original BB mean1.6417pp/worst2.1233pp. Premium stress mean5.4637pp/worst15.3299pp, below the full reference's corresponding physical errors. Rebuilt BB, independent cases, policy quality and whole-workflow timing are pending. `historical-gates-initial.json` retains all six candidates, including failures.

The32-particle herding candidate's nominal worst error is7.4978pp for AA against eight uniform opponents, beyond the7pp core threshold. However, the existing physical95% half-width is0.2942pp, making its0.4978pp excess fall within the registered two-half-width inconclusive band. Therefore32 does not pass, but that single boundary is not a conclusive physical rejection. No threshold has been relaxed, and no extra MC is required to proceed with the already passing64 candidate.

These are seen development regressions, not the independently registered new contexts. Candidate selection may use these results; tuning on subsequent independent output consumes the holdout and must be disclosed.
