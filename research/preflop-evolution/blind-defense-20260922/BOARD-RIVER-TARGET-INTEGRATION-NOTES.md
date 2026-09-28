# Conditional target learning: integration requirements

Prepared on 2026-09-28 while the fresh-deal target-learning experiment was
collecting data. This is a code/literature review, not an integration approval,
executed estimator control, or change to the registered experiment. Advancement
still requires its held-out gate. Do not tune that experiment from this note.

## What the current research walker does

`crates/solver/examples/research_sampled/policy_walk_allin_v1.rs` explores all
actions for the updating player and samples one action for the opponent. Its
`finish` method stores each action payoff minus the current policy-weighted
payoff at an updating-player decision. At an opponent decision it returns the
selected child's value. Preflop all-in leaves integrate board equity; ordinary
postflop terminal values use the sampled physical board and private cards.

`tools/research/weighted_physical_reservoir_v1.py` retains uniform visit samples
and an explicit source-deal weight. `weighted_visible_objective_v1.py` applies
that weight to the loss, not directly to target values. An integration must
preserve this distinction and the exact proposal distribution of its caller.

The current supervised probe instead predicts one conditional quantity:
Call payoff minus Fold payoff against a frozen, averaged opponent. Its four
network outputs are only a convenient architecture; only output 1 minus output
0 is supervised. The other output heads are not learned action values.

## Requirements before a separate implementation

1. Use the policy actually generating each self-play iteration's data when
   defining its opponent posterior. The two averaged 78-model banks in this
   diagnostic are fixed test opponents, not interchangeable with that policy.
2. Derive the conditional distribution for the actual sampled-deal proposal,
   blockers and opponent action history. Account for source-deal weights once.
   Positive own-history reach is not the same as counterfactual reach: the
   updater still explores its zero-probability actions.
3. Preserve the joint expectation of visits and stored updates. A conditional
   answer alone does not establish an unbiased regret estimator. Test both
   individual information sets and the values returned to their ancestors.
4. If raising is legal, derive a consistent full action vector and subtract
   one common policy-weighted value. A correct Call-minus-Fold contrast does
   not define the raise/jam regrets or a full policy update.
5. Freeze any learned baseline for the traversal that uses it, and retain
   explicit correction terms for sampled residuals. An inaccurate learned
   value must not silently become the true terminal payoff.
6. Validate first on fully enumerable synthetic games: unequal deal proposals,
   asymmetric policies, zero-probability own actions, rare opponent histories,
   ties, and rake. Verify complete action-update expectations and upstream
   values against exhaustive enumeration. A positive river regression result
   cannot replace these controls.
7. Measure variance reduction per elapsed second, including posterior
   enumeration and inference. Lower target variance may still be slower to
   obtain for the available CPU/GPU budget. Only then consider a bounded
   self-play comparison and a fresh complete-policy evaluation.

These are implementation requirements inferred from the inspected code and
estimator structure. No candidate satisfying them has been qualified here.

## Primary references and their limits

Deep CFR connects external-sampling visit targets with conditional advantages
and fits accumulated samples using reservoir memory. Its theoretical results
are stated for two-player zero-sum games. This supports checking the complete
sampling/update scheme, not treating a supervised value regressor as CFR.
[Brown et al., ICML 2019](https://proceedings.mlr.press/v97/brown19b/brown19b.pdf)

VR-MCCFR uses a baseline together with a sampled correction whose expectation
cancels it. The paper also shows how corrected estimates can propagate up the
tree. A baseline by itself is not that estimator; poorly correlated baselines
can increase variance. This is a possible design reference, not evidence that
its published speedups will transfer to GTOpen.
[Schmid et al., VR-MCCFR](https://arxiv.org/html/1809.03057)

The current game includes action-dependent rake. Do not transfer a two-player
zero-sum equilibrium guarantee to this raked model without additional analysis.
The present study measures local prediction and decision error only. Accurate,
flexible preflop ranges across positions, stacks and multiway play remain the
broader goal and are not established by this experiment.
