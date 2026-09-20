# Common basis for policy comparisons

`strategic-common-prior-v1.json` freezes the two live players' collision-conditioned entry distribution from the original subtree, before reading final new policies or reserved strategic outcomes. It uses the same 0.00001 per-combo entry cutoff. The surviving support is 56 hand classes for player 0 and 19 for player 1. Earlier folded players remain omitted.

The calculation enumerates all 1,326 by 1,326 private-hand pairs and removes shared-card collisions. A separate total-minus-card-masses calculation, including the identical-combo correction, reproduces each marginal within 2.09e-17. Uniform ranges yield 1,624,350 compatible ordered pairs; AA versus AA yields six. The common unnormalized entry mass is 10,783.720565950962. This is a deterministic physical-card calculation in float64, not an empirical player model.

Use player 0's frozen combo prior for standardized root action frequencies and prior-weighted root policy total variation among the final 112-weighted, 112-equal and older 47-board policies. Preserve all source policies unchanged. This removes differences caused solely by each training panel's own conditional hand distribution. It does not condition on reaching a later action node; any later-node frequency comparison needs explicit arrival probabilities and a separately stated common condition.

Do not use this full-deck entry marginal to replace the new reserved panel's board-conditioned normalizer when calculating its EVs or deviation gains. Those metrics must retain the frozen board weights and legal hand-pair accounting. Standardized policy distances and reserved-panel strategic values answer different questions.
