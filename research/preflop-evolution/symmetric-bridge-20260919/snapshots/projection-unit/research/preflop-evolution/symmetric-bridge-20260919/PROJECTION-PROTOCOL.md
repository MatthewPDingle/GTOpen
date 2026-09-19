# Exact policy tying diagnostic

Registered after the initial guard-only failures, before projected tests.

The initial wrapper checks root reaches but leaves internal action policies
free to lose suit symmetry through floating-point accumulation. Preserve the
failed results. Add an explicit projection after each traverser's update:
average that player's regret and strategy-sum entries over the suit group
fixing the board at each action node. Reduce into one canonical entry per
hand orbit, then broadcast in a separate launch to avoid races. Use f64 only
for this short sum; the stored solver state remains F32.

This changes the numerical update rule, so compare BOTH a fully enumerated
reference and a chance-compressed candidate using the same projection. Keep
the old unprojected reference as a sensitivity diagnostic rather than silently
replacing it. No production kernel or default solver behavior is modified.

Required checks before wider connected experiments:

- Independent CPU projection reproduces the GPU storage operation within
  2e-6 absolute on unit-scale synthetic arrays, with zero final orbit drift.
- Two-tone, monotone and rainbow tests: same-state full CPU/GPU sweeps differ
  by <0.002 bb per unit opposing mass; immediate root average error <0.002.
- After 100 iterations, projected full/compact GPU root strategies differ
  by <0.01, average/BR values by <0.002 bb. All materialized action policies
  must preserve their stabilizer exactly (both current and average strategies).
- Same final strategy evaluated through quotient versus all future cards
  differs by <0.0001 bb per unit opposing mass.
- The original input and initial-state guards still pass. No locks or warm
  imports are enabled as part of this experiment.
- Preserve measured allocations and test runtime. No accuracy claim or
  deployment follows merely from symmetry equivalence.
