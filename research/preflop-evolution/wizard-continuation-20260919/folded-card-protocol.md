# Folded-card diagnostic

Exploratory read-only diagnostic, 19 September 2026. Hold the saved 1,000-iteration
200bb baseline policies fixed. Export the eight actions leading to UTG facing
LJ's 3-bet after six folds. Preserve the save and production session.

Condition hero on one AA combination (suit symmetry before the flop). Sample
uniform physical deals to the other seven players from the remaining 50 cards.
Weight each deal by the product of the saved probabilities of LJ's 3-bet and
the other six players' folds. This conditions on observed actions, not just
on the two hands remaining live. Compare with two-hand compatibility alone.

Use 2,000,000 deals in 40 independent batches with fixed seeds. Report effective
sample size, repeat-batch variation, LJ reply probabilities and AA's all-in
value. First confirm that omitting folded-seat likelihoods reconstructs the
analytic two-hand-compatible calculation within sampling uncertainty.

The value diagnostic uses the existing sampled AA-versus-class equity cache.
It DOES NOT account for folded cards' effect on the future board. Thus the
experiment isolates opponent-range and action-probability conditioning, not
the full value of card bunching. Policies do not adapt and no production change
is proposed from this result alone. Do not tune sample size to match Wizard.
