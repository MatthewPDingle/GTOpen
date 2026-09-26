# Exact-mean showdown control: exploratory protocol

Reuse the completed 65,536-deal fixed-root archive, all four banks and all three non-jam contrasts. This is another exploratory diagnostic on inspected data. Preserve the earlier confirmatory study and the negative flop-rank result.

For each physical deal, calculate BB's showdown share on the full supplied board (0, 0.5 or 1). Subtract its exact expected share conditional on the two private hands, using the archived integer win/tie/loss counts over all 1,712,304 compatible five-card boards. This centered feature has expectation zero conditional on the private cards. Both private hands are used only in target construction; no opponent private information is added to a policy observation.

Fit one coefficient per hand class, bank and action contrast using the opposite global-index parity half. Keep the previously specified intercept-centered least squares, fixed ridge penalty 1 on summed normal equations, and zero coefficient if fewer than 20 fitting observations exist. No outcome-driven feature selection or penalty search. Unlike the prior eight-feature proposal, this candidate uses only the full-board showdown feature. Its expected value is already retained, so no new equity enumeration, training or neural inference is needed.

Before the full diagnostic, validate the isolated native card scorer with known wins, losses, ties and invalid-card rejection. Independently reproduce supplied showdown results using best-of-21 five-card scoring with explicit category/kicker tuples. Verify each count row's physical-private identity, integer totals and board count; preserve all source digests. Use complementary player scores as an additional accounting check.

Admission requires idle production, no other research owner, 20 GB available RAM, the combined 800 GB evidence ceiling plus 2 GB metadata reserve, and a 50 MB output limit. Runtime is bounded at 30 minutes after launch. Native scoring is bounded at 120 seconds and 65,536 supplied deals. Original evidence is read-only.

Publish per-class means and variances, incoming-mass-weighted variance ratios, coefficient norms and coverage for all banks. An independent readback must check scores/cards and reconstruct coefficients using a different linear-algebra route before conclusions. Cross-fitted outputs share coefficients; do not claim independent-sample confidence coverage. Lower variance alone is not improved poker play. A positive diagnostic would motivate a separately budgeted fresh-seed training experiment and evaluation, not immediate deployment.
