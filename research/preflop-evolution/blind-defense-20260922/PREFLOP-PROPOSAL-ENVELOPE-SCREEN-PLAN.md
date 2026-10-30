# Cheap reach-weighted envelope screen

After the complete-bank preflop export passes, propagate each of the eight
crossed profiles through the fixed 15-node preflop tree for every supported
class pair. Verify total terminal reach equals one. Use exact-key class
invariance already established by the complete physical catalog and original
inference; do not reinterpret the 169-by-169 matrix's restricted best-response
method. Its fixed class-pair mass and terminal-payoff entries are used linearly.

Verify the decomposition against the original native complete-policy evaluator
on its retained training transport, using all eight frozen profiles. Preserve
postflop policies and force only preflop choices to enter each of the three
postflop leaves. This supplies 24 conditional leaf values. Recombine these with
independently propagated preflop reach and an actual-investment terminal ledger;
require agreement within 1e-10 with the native full-profile values. This is a
transport/algebra check, not poker accuracy data or a universal error bound.

For the planning screen, use safe postflop payoff bounds [-200,200.5] for each
seat. For each contrast the conditional half-width is 200.25 times the sum of
its old and new postflop reaches. The shared proposal uses the largest of the
eight widths per class pair. Integrate that maximum under the original class
pair mass to obtain Z. Integrate the deterministic preflop terms and postflop
midpoint contributions to obtain each C. Report the fixed 16,384-observation
empirical-Bernstein additive term implied by this candidate width, without
altering historical results or using their outcomes to form the proposal.

No new deals, training, GPU use or production changes. One hidden native call,
at most 60 seconds, only if production is idle. Total control limit 180 seconds
and output under 4MB, within the prior export's 16MB reserved follow-up budget.
Freeze sources and retained inputs before running. Preserve failed artifacts.

This is deliberately a cheap go/no-go planning screen. C/Z are floating-point
planning calculations, not yet a qualified sampler or rigorous numerical bound.
If the width is still too large, retain the finding and choose a simpler design
or return to cross-stack modeling instead of extending this path indefinitely.
