# Independent folded-card experiment

Frozen before execution. Use the earlier eight-player action history. Sample
the two live hands from each player's original entry policy over physical
combos; reject collisions. Draw six mutually disjoint folded hands and then
five board cards without replacement. Reweight by the product of those six
actual fold probabilities. The paired control uses the same physical deals
with weight one. Integrating its uniformly dealt dead cards leaves the usual
two-player full-deck distribution.

Use 40 independent batches, seed 9026191930 + 1000*kind + batch, with
kind zero for the root population and 1..8 for the preselected probes.
Root: 50,000 accepted pairs per batch (2 million total). Probes: 100,000
accepted pairs per batch per hand (4 million per probe). Probe order and
physical representatives: AA [48,49], AKs [48,44], AKo [48,45], QQ [40,41],
JJ [36,37], TT [32,33], 99 [28,29], AQs [48,40]. Symmetric source policies
make the chosen suit representatives equivalent in expectation.

Retain batch totals, squared weights, equity numerators, and root class/board
counts. Estimate paired differences with batch influence functions for the
ratio estimators; report pointwise 95% intervals using t(39), not simultaneous
claims across all 169 classes. Report effective sample size. Verify the entry
proposal independently against exact physical pair enumeration, and check
that unit fold weights yield identical paired estimates. No range policy is
modified by these measurements. Equity shifts are diagnostic, not action EVs.
