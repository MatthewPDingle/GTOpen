# Probability and value contract

This document specifies the offline experiment, not a production solver model.

## Legal pair counts

Let `c[h]` be a hand class's number of physical combinations (6, 4 or 12),
and `C[h,j]` the number of ordered, nonoverlapping physical combinations for
the two classes. Define `K[h,j] = C[h,j] / (c[h] c[j])`.

The Python oracle enumerates physical two-card holdings. The GPU calculates
the same counts using rank incidence. With uniform class priors `u=c/1326`,
`u' K u = 1225/1326`. The resulting physical pair prior is therefore
`C[h,j] / (1326 * 1225)`. No Monte Carlo approximation is used for these
pair counts. The separate cached equity table remains Monte Carlo.

## Anchor once per heads-up branch

On each downward pass, find the first node on a branch with exactly two live
players. Normalize their arriving class reaches to `d0_entry, d1_entry` and
record `Z_entry = d0_entry' K d1_entry`. Every descendant uses that anchor,
including descendants where someone folds. Recomputing the anchor separately
at each terminal would change the relative probability of the actions.

At a terminal, let `d0,d1` be the current normalized class reaches,
`den_p[h] = (K d_other)[h]`, and `Z_terminal = d0' K d1`.
Let `P_other` be the product of all other seats' unnormalized reach totals.
Let `I_p` be the player's invested chips, and `V_p[h]` the terminal gross
payout conditional on that hand and compatible opponent holdings.

For either member of the anchored pair:

```
CFV_p[h] = P_other * den_p[h] / Z_entry * (V_p[h] - I_p)
```

For a player who folded before this pair was formed:

```
CFV_p[h] = -P_other * I_p * Z_terminal / Z_entry
```

The latter factor is necessary: the folded player's sunk cost must occur
under the same terminal joint probability as the surviving players' payoffs.

For a fold-win, `V` is the pot for the winner and zero for the loser. For an
all-in, it is the pot times compatible-weighted cached equity. Supported
learned continuations use the unchanged predictor's gross pot fraction.
Other continuations use compatible-weighted Balanced pricing. The reference
and GPU check both class-level values and weighted chip conservation.

An entirely unreachable arriving range uses the uniform class prior only to
define its off-path anchor. A terminal with zero opponent reach has zero
counterfactual value. The learned predictor is not applied when either pair
range has zero total reach; the compatible Balanced fallback is used.

## What this establishes, and what it does not

At a two-player root this supplies exact suit-symmetric pair probabilities
through the entire tree. Fixed continuation payoffs would define an ordinary
two-player chance model. However, the learned continuation predictor changes
with the arriving ranges. Its current best-response calculation freezes those
values; ordinary fixed-game CFR convergence claims do not follow.

In larger games the first-heads-up anchor is an explicit probability reset.
It omits folded-card bunching and earlier multiplayer card correlations.
Anchors themselves can change as earlier policies change. The tests establish
that the implementation matches this stated approximation and conserves chips;
they do not establish exact multiplayer dealing or equilibrium quality.

No clipping, refitting, shared balancing offset, or adjustment of predictor
coefficients is part of the interface fix. Future performance work should
preserve this contract and rerun the independent action-value oracle.
