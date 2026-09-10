# CPU preflop repeated-work and allocation review

Assessment/proposals only. No source-checkout modifications, compilation or
hardware benchmarks. The active CoupledDeck uses clean423 minimum quadrature;
these proposals do not modify it, its1024 particles, f64 arithmetic or layout.

## Narrow candidates

**1. Consume owned sigma vectors — recommended first.** In `traverse`, the
current code allocates/zeros `na*169` floats, then calls `average_strategy`,
which allocates another vector, and copies it into the first. Forced policy
vectors are also already owned but copied into a fresh sigma allocation.

`owned-sigma.patch` consumes the owned average/forced vector directly. Current
learning-strategy calculation keeps its original allocation and operation
order. A boolean records whether the consumed option was forced, preserving
all pruning/update/constrained-BR branches. Length assertion retains the old
copy operation's shape check. This removes one allocation, zero-fill and copy
at every average/forced action-node visit; average/BR checks visit many such
nodes. Saved payload work is4*169*action_count bytes per removed zero-fill or
copy, plus allocation/free overhead. No timing percentage is claimed.

**2. Reuse terminal opponent masses — smaller independent candidate.**
`terminal_value` reduces every opponent's169 weights into an f32 sum for the
counterfactual product, then repeats each live opponent's reduction for
normalization. `reuse-masses.patch` stores the first sums in a nine-f32 local
array and reuses them. The same reduction and f64 multiplication order remain;
own reach is not included. Opponent order, divisions and zero guards are
unchanged. Saves up to eight169-element reductions per live pot-share terminal,
but this is small relative to1024-particle CDF/product work.

Both patches apply independently to the recorded base. `combined.patch` is
provided only for final integration after separate measurements; do not use it
for attributing a benchmark win to one change. No additional tests mirror these
simple ownership/reuse changes. Use existing full CPU solver tests and frozen
3/4/6-seat same-gap controls; compare exact arena/gap/EV outputs to the retained
clean423 baseline. Include frozen/forced/adaptive profiles, pruning, zero own
and opponent reach, and calibrated/legacy cases from existing tests.

## Where larger duplication actually exists

`CoupledDeck::equities_with_rule` already constructs each opponent CDF **once
per particle**, outside the169-hero-class loop. There is no repeated CDF build
per hero hand to remove. The CDF array is stack scratch, not a heap allocation:
eight170-element f64 rows =10,880 bytes. Its zeroing occurs once per call, while
the rows are overwritten for all1024 particles. Merely reusing that scratch
would save only a once-per-call initialization and is low priority.

`terminal_value` does allocate an outer `Vec<Vec<f32>>` plus a normalized vector
per live opponent. Those ranges are normalized once per call, not per particle.
Thread-local reusable buffers could remove these allocations without changing
the CoupledDeck API, but would introduce borrow/reentrancy complexity and may
offer little against a millisecond-scale coupled terminal. A slice-based stack
API avoids TLS but changes hot-function specialization/code generation—the Q5
experience argues against assuming that will be free. Measure before choosing.

The strongest larger opportunity is **paired CPU checkpoint evaluation**.
`gaps_and_evs` currently invokes `traverse` twice for each player: BR/constrained
BR and average. Both read the same average strategy and propagate the same
opponent reaches. For a fixed node/player, terminal values are identical, so
normalization, CDFs and quadrature are computed twice. At the player's own nodes
only the upward combination differs: max versus sigma-weighted sum. Other
nodes add child values for both outputs in the existing action order.

A dedicated read-only traversal returning `(br[169], avg[169])` could compute a
terminal once and combine both outputs on the way up. Preserve exact per-hand
addition order, the different mode2/mode3 forced-policy rules, and average's
zero-action pruning behavior. Traversing BR's superset must not accidentally
give average a nonzero skipped branch or expose stale scratch. Parallel action
collection must preserve action order, and stop handling must remain equivalent.
This is a concrete higher-value next design, but larger than the two patches
and requires dedicated baseline-pair comparison tests before implementation.

Caching every terminal result between the two existing traversals is simpler
but memory-heavy:676 bytes per terminal per player. At805,640 terminals this is
about544.6MB per player, roughly4.36GB for eight parallel checkpoint players,
before metadata. Fusing the traversal avoids that persistent cache and reuses
only recursive result storage. Do not cache across alternating learning sweeps:
the preceding player's regret update changes later opponents' current policies.

Cross-player CDF reuse during average evaluation is also possible in principle,
but each player excludes a different distribution and existing traversals run
in parallel. Full per-source1024-particle f64 caches are enormous. Shared mutable
global caches would require exact state/generation keys and synchronization.
That is a separate design, not an allocation-cleanup patch.

## Recommendation order

Measure owned-sigma reuse first, then mass reuse if inexpensive. If checkpoint
time remains important, design paired BR/average traversal next. Defer TLS CDF
scratch and broad cross-seat caching until allocation/phase measurements justify
their complexity. Preserve the clean quadrature implementation while testing
these independent changes.
