# Full-flop expansion

The full-combo two-flop panel would require25.68GB just for regret/strategy
arrays, before traversal buffers. This exceeds available24GB VRAM.

The earlier entry ranges contain extremely small residual probabilities.
Create a separately named executable from the frozen engineering pilot,
removing entry combo weights below1e-5 of that player's maximum. This retains
322 UTG combos /56 classes and106 LJ combos /19 classes before board removal.
Removed entry probability is1.6203e-6 /1.2845e-6, respectively. No branch-specific
trimming, added probe floors or fixed AA policy is permitted. All retained
hands can use every legal preflop option and adapt postflop.

First reproduce the two-river engineering game with supported ranges, then
test KhQd9d with ALL turn/river cards and all three betting streets. The panel
is still deliberately small: results establish connected computation, not
full-deck range accuracy. Initially run20 iterations to measure memory/time
and conservation; only then set the larger experiment budget.

Use the same39.5/93.5 pots,182/155 stacks,50%/75% betting menus, pot raises,
one raise per street,4% rake capped6. Verify physical root prior and bound
the change caused by entry trimming in joint-chance total variation.
Keep the all-combo source/executable and original freeze intact for replay.
