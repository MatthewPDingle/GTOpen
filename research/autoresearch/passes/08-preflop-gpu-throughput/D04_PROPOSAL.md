# D04 proposal: cross-player CDF sharing in average checks

D03 puts about44% of large check time in CDF construction. C01 removes exact
duplicates within one traverser, but `queue_evaluation` clears/rebuilds the
classification and CDFs for every player after a single common average down
sweep. Average reaches are immutable across those checks.

Before changing dispatch, inventory exact normalized-distribution overlap across
players under the actual ungated evaluation path. Build a global bitwise
interner; hashes only find candidates, full169-value equality establishes
identity. For each traverser collect the unique identities that its CDF writer
actually produces (skip zero mass, do not use the learning-active mask). Verify
same-source vectors are identical across traversers. Count pairwise unions and
saved CDF rows relative to C01's separate unique sets, plus all-player union.

Report all pairings, a deterministic minimum-union pairing, and natural adjacent
pairs; do not cherry-pick one pair. Include an odd-player singleton. Calculate
both static worst-case and unique compact CDF sizes at the unchanged batch32,
plus an extra full value buffer needed to preserve one player's terminal sums
while evaluating the other. Include classification/remapping scratch and total
engine/headroom estimates. Shared CDFs cannot be kept by simply reordering
loops while overwriting the sole value buffer.

The potential implementation would evaluate a pair's terminal values across all
particle batches, then perform that pair's two usual up sweeps per player.
Learning traversals remain untouched: their alternating updates invalidate this
cross-player reuse argument. Keep each hand's per-particle and batch accumulation
order unchanged. No reduced sampling, sparse-output shortcut or changed game.

This proposal is not implemented. Register a protocol before running the read-only
inventory on immutable small and large saves. Require full arena/iteration
preservation and exact collision/signed-zero identity tests. Gate further kernel
work on at least25% fewer CDF rows across a full check AND a credible unchanged-
batch memory plan within23GB. This only admits a prototype; actual complete-run
speed and numerical qualification remain mandatory. GPU work serial/guarded,
cap180s per inventory, production56708 unchanged. No speed or convergence claim.
