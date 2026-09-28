# Review: broader deal coverage improves the river learning probe

Reviewed 2026-09-28 after collection, all 48 fixed fits, final evaluation,
independent metric readback and the pre-registered robustness analysis completed.
Collector session 52256 and pipeline session 37598 both exited 0. The plot was
visually reviewed. No production change or full-policy training occurred.

## What we learned

With the same 1,152 training examples, using 192 distinct deals instead of 64
reduced fresh-deal mean squared prediction error by 16.28% and local Fold/Call
decision cost by 36.28%. Direction agreement rose from 64.8% to 73.6%.
Both actors in both frozen opponent banks improved on both primary metrics.
Every reported pot band improved versus dense-exact, although the smallest-pot
prediction improvement was small. This is evidence for broader deal coverage
within this fixed experiment, not a scaling law or universal accuracy estimate.

In the broader dataset, exact opponent integration also beat 16-sample labels:
6.36% less prediction error and 15.72% less local decision cost. Cost improved
for both banks. This was not universal across all diagnostics: bank B / BTN
had worse prediction MSE with exact labels (3107.311 versus 3014.082), despite
slightly lower decision cost (8.990 versus 9.022). Under-10bb pot decision cost
was also higher for exact than sampled labels (0.723 versus 0.635).

Both separate, predeclared advancement gates passed. The earlier target-only
study's failed bank-A gate remains a failed result; this fresh test does not
rewrite it. The current comparison retained all three paired model seeds.

## How much confidence to place in this

The evaluation contains 576 states but only 32 distinct physical deals;
the states and frozen-bank comparisons are correlated. The descriptive
leave-one-deal-out checks preserved the aggregate advantage for both metrics
and both primary comparisons. No confidence interval or significance claim
was made. Broader-exact decision cost won on 20/32 deals versus dense-exact,
and 17/32 versus broader sampled targets: it does not win on every deal.

Generalization remains imperfect. Broader-exact training MSE is 8.599 versus
2245.221 on fresh deals. The improved averages do not mean the model is ready
to price every unseen river reliably. Data covers one restricted 200bb
BB-versus-BTN context, inherited incoming ranges and two fixed opponents.
There is no evidence here for other stack depths, multiway play, full-policy
EV, exploitability or improved preflop opening/calling ranges.

## What advances next

Proceed to a separately controlled estimator integration experiment, starting
with fully enumerable synthetic games as described in
BOARD-RIVER-TARGET-INTEGRATION-NOTES.md. Derive and test the exact sampling,
opponent-history conditioning and weighting used by the real traversal.
Include complete legal action vectors, zero-probability own actions, unequal
deal proposals, rare opponent histories, ties, rake and ancestor returns.

The current regressor supervises only Call minus Fold against an averaged
frozen opponent. Its other heads are not learned action values and it cannot
be inserted as a full regret update. A learned baseline must retain a sampled
correction, rather than replace the true payoff. Measure variance reduction
per elapsed second before committing to a bounded self-play comparison.
Require a fresh complete-policy evaluation after integration; this final set
is now spent and cannot be used to tune a purported new final result.

The separate shared-input performance qualification changes no predictions
or targets and has its own acceptance checks. It can improve future collection
throughput without establishing any additional poker-model result.

## Evidence and resources

See BOARD-RIVER-DEAL-COVERAGE-FINDINGS.md and
BOARD-RIVER-DEAL-COVERAGE-ROBUSTNESS.md for full tables and source evidence.
Independent scalar reconstruction covered 4,309,730 exported observations;
maximum discrepancy was 3.64e-11. All targets were supported and the matched
training actor/pot quotas remained equal. The new store used about 0.420 GB
against its 2 GB cap. Training took 65.8 seconds and scoring 6.6 seconds.
The final collection invocation took 28.0 minutes; this excludes the earlier
interrupted collection and recovery overhead, so is not total experiment time.

The broader goal remains active. No production deployment, historical archive
deletion or additional GitHub push was performed for this result.
