# Interpreting transfer after rebuilding postflop responses

Written 20 September 2026 while the final original independent95 comparison
is still running. This changes neither the frozen protocol nor acceptance
criteria. It records a hypothesis to test, not a diagnosed implementation bug.

The transfer procedure preserves preflop policies but independently trains
both players' postflop responses. Thus it changes two things relative to the
original connected solve: the board panel and the continuation strategies.
A small postflop best-response residual establishes local convergence against
the resulting opponent; it does not establish that replacing the original
continuations preserves earlier action incentives.

Brown and Sandholm explain why solving an imperfect-information subgame using
fixed entering distributions can increase full-game exploitability. Their safe
resolving constructions retain information about the opponent's counterfactual
outside options. The guarantees concern two-player zero-sum games.
[Safe and Nested Subgame Solving (2017)](https://noambrown.github.io/papers/17-NIPS-Safe.pdf).

Kubicek, Lisy and Sandholm additionally show that distinct equilibria of a
resolving gadget can have different full-game performance. Their refinement
perturbs auxiliary opponent decisions using a prior, rather than imposing a
permanent action-frequency floor everywhere. Their experiments use small
benchmark games; this does not establish benefits for GTOpen or justify
artificially adding mixed actions to its displayed poker ranges.
[Equilibrium Refinements Improve Subgame Solving (2026)](https://arxiv.org/html/2601.17131v1).

Our current experiment is raked and therefore general-sum; it rebuilds both
postflop strategies and does not implement those safe-resolving gadgets.
Neither paper supplies a drop-in correctness guarantee for this experiment.

## Diagnostic order

1. Finish the original four comparisons with unchanged gates and preserve all
   outcomes. Their transfer metric describes the newly assembled strategy.
2. Reuse independently trained workers on each source's exact original board
   panel and weights. This removes the change in board coverage. Compare with
   its original connected solve before attributing deviation to unseen boards.
3. If that matched-panel deviation is material, audit preservation of source
   continuation values and averaging semantics before investing in a larger
   training panel. A controlled zero-rake miniature game would help separate
   reconstruction issues from general-sum behavior.
4. Investigate constrained resolving or continued joint training only after
   that diagnosis. Evaluate the assembled preflop/postflop strategy and its
   deviation gains; a locally converged continuation is insufficient evidence.

The existing conditional-hand residual audit narrows ordinary local numerical
error as an explanation for two completed panels. It does not eliminate
continuation-selection sensitivity. See CONDITIONAL-RESIDUAL-DIAGNOSTICS.md
and the registered matched-training-panel analysis in
POPULATION-SUPPLEMENT-RUNTIME.md. No production changes were made.
