# Physical-board extension

Registered after the 2-million-deal action-conditioning diagnostic. That
diagnostic changed AA's jam value by about +0.25bb, but retained cached equity
and omitted the effect of folded cards on the board.

Now sample full physical deals: AA fixed, fourteen distinct other hole cards,
then five distinct board cards. Use the same saved action and reply policies.
Compare weights that include only LJ's 3-bet with weights including six folds.
Both arms use the same deals and boards. Evaluate actual showdowns with the
repository's seven-card evaluator, with ties split equally.

Fix 32 million deals, 40 independent batches of 800,000, SplitMix64 seeds
1909192600 + batch index, four CPU threads. Partial Fisher-Yates uses unbiased
bounded random draws. No equity cache participates in this extension.
Report probabilities, called equity, effective sample size, action EV, paired
batch-jackknife standard errors and approximate Monte Carlo 95% intervals.
Do not extend the sample based on matching or failing to match Wizard.

The two-live-hand arm must reproduce analytic card-compatible action
probability within sampling uncertainty; equity differences from the cache
can reflect either Monte Carlo sample, and should be reported rather than
silently corrected. This remains fixed-policy analysis, not a re-solve.
Preserve production and original evidence.
