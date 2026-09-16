# N21: wider flop-menu sensitivity

Registered before this experiment's outcomes. This is a validation study of the
unchanged N15 predictor and N20 implementation, not additional training. It asks
whether restricting reference solves to half-pot bets hides important error.

Use all four iteration-500 contexts from N20's changed-policy study, without
selecting contexts from their errors. Generate 20 unused canonical flops, four
from each of the five existing rank/suit strata, with deterministic seed
`flop-menu-20260916-N21`. Exclude every board in previous or reserved manifests.
Freeze the predictor, contexts, board list, helper and dependencies before any
new labels. Use identical boards and ranges for both menus (160 solves total).
Order jobs by board, context and paired control/expanded menu so early batches
exercise the more expensive tree; never interpret an incomplete batch as a pass.

The control has half-pot bets/donks on all three streets. The expanded menu
adds one-third-pot and three-quarter-pot bets/donks on the flop, retaining the
half-pot option. Both have pot-sized raises, maximum one raise, no all-in
option, zero rake and unchanged stacks/pots. Turn and river menus stay fixed.
This is a nested flop-menu comparison, not a complete unrestricted tree.

Require both CPU and GPU gaps <=0.1% pot, materialized full-enumeration queries,
finite hand values and compatible-pair pot conservation for every reference.
Maximum 2,000 iterations; preserve failures rather than loosening limits. Use
the existing inclusion-probability/isomorphism weighting and paired bootstrap.
No inference from partial results. Archive exact reference hashes and freeze
timestamps. Report per-hand reference quality separately from prediction error.

The fixed accuracy criterion is the same per-context requirement as N20:
at least 15% lower weighted value error than Balanced and no more than 10%
regression versus the previous conditional predictor, in all eight
context/menu combinations. Show all cases and separate menu summaries. Also
report paired changes in the reference hand values; those changes describe
menu sensitivity, not model improvement. A failed gate does not revoke prior
evidence on its original tree, but prevents a broad betting-menu claim.

Only execute after N20 completes and passes its original gates and reference
audit, and when no other research controller owns the GPU. N19 has priority.
Start with at least 90 minutes left before the fixed 20:49:02 UTC deadline.
Stop safely between batches at that deadline. No app mutation, production
model changes, automatic deployment, altered arithmetic or model fitting.
Twenty boards per context give a limited, conditional estimate; intervals do
not capture training uncertainty, and the contexts are familiar. Passing this
test does not establish full-game convergence or GTO Wizard agreement.
