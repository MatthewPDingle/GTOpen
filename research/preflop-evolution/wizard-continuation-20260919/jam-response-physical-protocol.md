# Physical-deal check of local jam responses

This diagnostic follows an exploratory analytic finding: conditioning the
jammer's range on the caller's actual cards substantially changes some hand
EVs, even before the AA allocation changes. It is not held-out validation.

Use the frozen 1,000-iteration UTG-open/LJ-3bet/six-folds/UTG-jam history.
For each selected LJ hand (AA, KK, QQ, JJ, AKs, AKo, AQs, AJs, ATs, KQs), fix
one representative combination, deal all other seven players and the five
board cards uniformly without replacement. Weight by the saved probability
of UTG opening and then jamming, optionally also by the six folds. LJ's own
earlier 3-bet likelihood is constant for a fixed hand and cancels.

Fix 32 million deals per hand, 40 independent batches of 800,000, four CPU
threads. SplitMix64 seed 20260919000 + hand_index*1000 + batch_index. Compare
actual seven-card showdown results with the existing sampled class-equity
calculation. Report batch-jackknife Monte Carlo standard errors; do not force
agreement or extend samples to obtain a desired sign. Small edges may remain
unresolved and are not evidence for a pure action.

Calling costs LJ 182bb; final pot is 403.5bb with 6bb rake. Call EV relative
to folding is 397.5 times conditional showdown share minus 182. No future
decision remains in this branch. Both arms share each physical deal and board.

Record effective samples, raw batch sums and input/binary hashes. Preserve
production and saved policies. This tests a local all-in response valuation;
it does not show the result of re-solving the entire preflop game.
