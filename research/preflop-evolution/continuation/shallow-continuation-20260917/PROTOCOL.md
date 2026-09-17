# Prospective shallow-continuation check

Production port 56708 stays unchanged. All work uses offline reference processes.

The preceding audit found optimism in the Balanced fallback at SPR 17.5/45.
This study does not assume that the error generalizes or that a correction works.

## Samples fixed before new reference values

- Confirmation: 100 fresh canonical flops, 20 in each rank/suit stratum, excluding
  the preceding 50. Estimate the full board population by treating those old 50
  as a certainty stratum (weight one), plus inverse-probability weighted samples
  of the remaining boards. Also report the new-board complement alone.
- Training: three pre-existing designed range-pair families, at SPR .2 and .75,
  20 stratified flops each: 120 solves. Family-level cross-validation selects
  one of four fixed ridge penalties. No saved-game range enters training.
- Held-out: two newly specified range pairs (a mixture and a premium-heavy
  matchup), at SPR 17.5/45, 30 stratified flops each: 60 solves. Range mixtures
  share components with training, so this is not a completely unrelated population.
  The saved-game confirmation is a third external range matchup.
- Training and held-out panels are independently selected from the full 1,755
  canonical boards; incidental board overlap is allowed. Range contexts remain
  separated. Board is never a predictor input.

Total: 280 new reference solves, with both GPU and transported full-enumeration
CPU best-response gaps <=0.1% pot. Same finite postflop action menu as the preceding
audit, 2,000 iteration ceiling; failed jobs are not accepted or silently dropped.

## Candidate and decision rules

Fit a small, centered polynomial of equity, position, pair/suited indicators and
stack depth. Predict the residual from raw equity, in pot units, with a multiplier
that vanishes at zero remaining stack. Center by legal-pair mass and apply a shared
payoff-bound multiplier to conserve the pot. Coefficients and penalty are selected
using synthetic training references only and frozen before held-out evaluation.

Per-hand reference quality requires postflop best-response gain <=0.5% pot.
Report qualified pair mass and errors for both players; do not hide weak support.
Primary candidate screen: >=10% reduction in qualified pair-mass-weighted MAE
against the equity-control-variate reference in *each* held-out context, including
the saved-game context, relative to the exact Balanced fallback. Direct-reference
MAE must not worsen >5% in any held-out context. At least 95% of pair mass must pass
the per-hand quality screen in each case. Report uncertainty from 5,000 stratified
paired bootstrap replicates; scores alone do not establish a statistically robust win.

Regardless of pass/fail, substitute the frozen prediction only at the shallow
4-bet leaf in the previous frozen-policy action audit. Report call/fold and
call/3-bet errors and sign screens on the same qualified hands, preserving the
earlier primary gates. These are fixed-policy counterfactual checks, not newly
solved preflop equilibria. Existing call and 3-bet labels are reused; no claim of
fresh independent confirmation for those branches. All-in and SPR>=1 predictions
remain untouched. No deployment from this study alone, even on a passing screen.

Limitations: zero rake, heads-up, one finite postflop menu, modest board samples,
cached preflop equity, and tested shallow stack depths only. No general multiway,
arbitrary-sizing, GPU speed or GTO Wizard equivalence claim.
