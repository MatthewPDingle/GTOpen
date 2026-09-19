# Restricted AA call/jam feedback test

Registered before outcomes. Research only; no writes to production 56708,
no frozen-save changes, no reserved Wizard cases, and no model deployment.

Start from the 50,000-iteration compatible fresh policy in
`conditional-hu-20260919`. Preserve the original incoming ranges, dead money,
positions and configured rake. Hold all UTG hands other than AA fixed. Set
AA's root policy to call with probability q and jam with probability 1-q,
where q is 0, 1, 0.5, 0.25 and 0.75 (this execution order is fixed in advance).
At each q, recompute LJ's exact best response to the changed jam range using
compatible private-card probabilities and the existing sampled equity cache.
Report AA's jam value against that response, relative to folding at the root.
The smaller 4-bet is excluded for AA in this restricted experiment; this is
not a complete-game equilibrium or a final poker recommendation.

For each q, derive the resulting UTG calling range. Solve the HU postflop game
against the unchanged arriving LJ range, pot 39.5 bb, effective stack 182 bb,
4% rake capped at 6 bb. Use the already registered 40 stratified flops and two
menus (50% and 75% pot, 100% pot raises, one raise per street, no extra jam,
85% stack conversion). Both postflop players adapt at each q. Total: 400
GPU solves, serial and only while production is idle at each job boundary.

Prepare suit-symmetric ranges by normalizing each to maximum weight one,
trimming weights below .005, and restoring the original eight OOP diagnostic
hands to a minimum .001. Removed and added combination mass must each be less
than .5%. At q=0 this supplies the otherwise absent AA probe; report that
boundary as a small-perturbation estimate rather than an exact zero-mass query.
Record actual AA mass and preparation changes for every q.

Accept each solve only if GPU and independently materialized CPU global gaps
are <=0.05% pot, all eight OOP probe class best-response gains are <=0.05 bb,
and pair-mass/rake accounting passes existing checks. Maximum 5,000 iterations.
Preserve failures; never silently omit a board or loosen a gate.

Estimate AA's gross continuation value by physical pair mass and canonical
flop multiplicity / inclusion probability; subtract the incremental 12 bb
call cost. Use 5,000 paired, within-stratum bootstrap draws for board-sampling
intervals. Compare call minus jam at every registered q under each menu.
Do not claim a precise mixing rate from five points or from an uncertain sign.
An interior sign change is evidence for feedback in this restricted problem,
not proof of full-game convergence. Equity-cache uncertainty, folded-card
bunching, range trimming, earlier fixed policies and restricted postflop trees
remain outside the bootstrap intervals. This is a diagnostic study, not
training or a production performance benchmark.
