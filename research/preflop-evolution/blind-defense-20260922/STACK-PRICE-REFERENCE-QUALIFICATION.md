# Qualification of the exact stack/price reference

This bounded probe checks the oracle proposed in STACK-PRICE-REFERENCE-DESIGN.md.
It is not a fitted-model experiment and supplies no final-test data.

Use all native river public states with exactly fold/call at fitting depths
20, 40, 100, 200 and 400 bb. Join them to the existing native terminal audit by
full history and branch within that exact context. Confirm terminal calls,
action count, actor, pot, call cost, configured rake, and loss/tie/win cash flows.
The uniform opponent is a deliberate diagnostic assumption; these are terminal
river bets, not necessarily jams. Do not interpret it as an observed betting range.

The probe uses four fixed edge-case boards and eight deterministic random boards
(seed 9296301), all distinct under full-board suit isomorphism. Enumerate all
1,081 hero holdings and 990 legal opponent holdings per hero on each board.
Compare native ranks with an independent implementation that evaluates every
five-card subset. Compare full conditional counts with the native direct
enumerator. Check probability mass, win/loss complement symmetry, royal-board
ties, card-order/suit invariance, invalid cards, menus and count records.

The independent cash-flow oracle computes call-minus-fold values from exact
win/tie/loss counts and native public amounts. Compare with the separate equity
formula; the exact optimal call/fold rule must have zero decision regret.
Report actual price coverage, row counts and compute/storage cost. A passing
result establishes this restricted reference, not learned poker quality.

No strategic labels at held-out depths 60/150 bb. Exclude every probe board's
canonical group from any subsequent training/validation/final-test dataset.
Do not reuse the old fixed-200bb diagnostic's results as fresh evidence here.

Eight hidden CPU workers maximum, one numerical-library/native enumeration
thread per worker. Production activity and other studies take priority. Bound
the probe to one hour, 250 MB new evidence plus 50 MB admission reserve, 800 GB
global allocated research storage and 40 GB S: free space. No GPU allocation,
model fitting, production modification or deletion of existing evidence.
Freeze sources, boards and inputs in a new registration before execution.
