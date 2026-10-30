# Next investigation: river decomposition

This is a feasibility design, not a registered strategic run or a production
change. The public-chance census established the reason to investigate it:
1,087.68 GB of river state versus 6.25 GB on flop and turn in this exact panel.
Keeping only the earlier arrays is not sufficient; boundary information and
the cost of reconstructing continuations must be included.

## Relevant method and limits

CFR-D keeps trunk strategies and averaged counterfactual values at subgame
roots, solves subgames during trunk training, then discards their interior
policies. Later policy reconstruction needs the appropriate resolving game.
The paper requires mutual counterfactual best responses, including hands with
zero own reach; ordinary locally optimal play on reached hands is insufficient.
It explicitly trades extra computation for storage. Its guarantees concern
two-player zero-sum perfect-recall games.
[Burch, Johanson and Bowling, 2014](https://poker.cs.ualberta.ca/publications/aaai2014-cfrd.pdf).

Our candidate includes action-dependent rake, so the complete game is not
constant-sum. We must not transfer that guarantee by calling it heads-up. Some
river boundaries may already be above the rake cap; classify those from actual
terminal cashflows. A zero-rake control is useful for implementation checks but
cannot replace the original 5%-capped-at-2-bb experiment.

## First engineering gate

Count the actual river frontier before building a decomposition solver:

- Group each river subgame by the complete public betting history and ordered
  public cards. Retain all private hands in its information sets, with the same
  suit-orbit mapping; do not merge distinct betting histories because their
  current ranges happen to resemble each other.
- Account for both players' accumulated boundary values and any normalizers,
  plus the retained earlier-street arrays. Include the largest active river
  workspace and metadata separately. Reconcile the sum of river interior sizes
  with the 1,087.68 GB census.
- Count subgames and their size distribution. A memory saving is not useful if
  repeatedly solving that many subgames makes the outer study impractical.
- Determine which boundaries have constant terminal rake and which remain
  general-sum. Preserve pot, previous investments and utility offsets exactly.

This is CPU geometry/accounting work, not CPU performance optimization. It
does not use or interrupt the production solver.

## Gates before interpreting strategy results

If the frontier fits, register a bounded GPU prototype and compare against a
resident full-tree reference on the same small control game. Audit extracted
river utilities, counterfactual reach weighting, zero reach and reentry, policy
averaging, and reconstruction. Test the returned assembled strategy and earlier
deviation incentives, not just each river's local gap. Keep zero-rake and raked
results separate and report numerical error without claiming the zero-sum
theorem applies to the latter.

This addresses the prior
[resolving warning](../representative-coverage-20260919/RESOLVING-INTERPRETATION.md):
plain fixed-range re-solves can change earlier incentives. No frozen-value
shortcut, hand-support pruning, forced mixed strategy or smaller betting menu
is authorized as a substitute for the actual blind-defense comparison.
