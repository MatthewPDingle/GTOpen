# Next candidate: sampled decisions with full hand and action support

This is a research direction, not an implemented replacement solver. The
wide-state and river-frontier measurements rule out relying on straightforward
compression or a naive every-river re-solve loop for the next BB experiment.

External-sampling MCCFR samples chance and the other player's actions while
enumerating the updating player's actions. Its regret estimates agree with
full traversal in expectation. It trades more iterations for cheaper iterations;
it does not guarantee a smaller final table or faster practical convergence in
our game. The original equilibrium results concern two-player zero-sum games.
Our action-dependent rake still requires measured best-response checks.
[Primary algorithm paper, sections 3–5](https://papers.nips.cc/paper_files/paper/2009/file/00411460f7c92d2124a67ea0f4cb5f85-Paper.pdf).

## Preserve the target

- Use the qualified BB/BTN entry, all 169 BB classes and the same 96 entering
  BTN classes, all three postflop continuations and the existing betting menu.
- Preserve the 112-flop weighted panel initially; this tests a change of
  algorithm, not a simultaneous change of ranges, boards or actions.
- Earlier ranges remain fixed and earlier folded cards remain omitted. The
  incoming BTN policy is approximate, not a new validated opening range.
- Never key a player's strategy by the other player's hand, an unrevealed future
  card, or a sampled terminal outcome. Keep perfect recall of public actions.
- Do not skip the updating player's actions because their current probability
  is zero. Zero-own-reach and re-entry controls are mandatory.
- Lazy allocation can still grow toward the whole state space. Use a hard
  resource stop, retain evidence, and fail the feasibility gate if it grows too
  large before useful convergence. Do not erase regrets to manufacture a fit.

## Chance accounting first

The existing connected panel defines one joint chance law: board weight times
both fixed entry weights, masked for all physical card collisions, divided by
one global normalizer. Conditional on this panel, the board marginal is therefore
proportional to its weight **times its compatible private-pair mass**.

An exact two-stage deal sampler should draw that board, then the first hand by
its compatible marginal, then the other hand conditionally. Drawing the board
from its nominal weight and independently renormalizing each board's game would
change the target. Drawing the first hand without accounting for compatible
opponent mass is also biased. Early folds use this same joint chance law; a
pre-sampled board must never be visible to the preflop policy.

`hu_sampled_deal_oracle_20260922.py` exhaustively compares the factorization
against dense physical pair enumeration over all 112 boards in both contexts.
It also checks the original context's global normalizer against the completed
native connected run. This qualifies only the joint probability calculation.
The canonical panel's full physical preflop symmetry still requires a shared
uniform global suit relabeling (or a separately verified equivalent orbit
scheme); the first oracle does not implement that sampler.

The oracle passed on all 112 boards in both contexts. Maximum pair-probability
error was below 1.4e-19; independent card-subtraction normalizers agreed within
1.4e-15 relative error. The original native normalizer agreed within 2.0e-9.
The intentionally naive nominal-board sampler differed from the correct board
law by total variation 0.06028 in the original context and 0.01653 in BB defense.
Those distances compare probability laws, not poker accuracy. Registration,
per-board results and the log are preserved as `sampled-deal-oracle-v1-*`.
This passes the deal-law calculation only. A subsequent exact finite-game
[update and averaging control](SAMPLED-UPDATES-RESULT.md) passed gate 1 below;
the GPU implementation and subsequent gates remain outstanding.

## Implementation gates

1. Independently verify sampled regret increments and own-reach-weighted strategy
   accumulation against complete finite sums on controlled games. Include two
   changing-policy rounds, rare hands, all-in outcomes, folds before the flop,
   zero own reach, and intentionally incorrect weighting controls. The
   accumulation contract must be explicit before implementing a GPU trainer.
2. Keep a frozen strategy within each GPU batch. Accumulate repeated information
   set updates with a specified reduction order; do not silently mix old/new
   strategies or drop collisions. Verify against the scalar reference.
3. Measure allocator growth, updates per second and variance on the actual wide
   geometry. No preallocation of full physical-hand arrays at every public node.
   CPU work is the correctness oracle, not a CPU performance project.
4. On a tractable control, compare time and memory to reach the same independently
   measured deviation threshold. Sample counts are not equivalent to full CFR
   iteration counts, and matching a noisy training statistic is insufficient.
5. Only after those gates, register the full 112-board BB experiment with fixed
   seeds, budgets, stopping rules, and a separate unused evaluation panel. Do
   not use the already inspected 190-board results to tune a new policy.

Retain ordinary regret matching as the first sampling reference. The original
paper is not evidence that sampled CFR+, our projection schedule, or a new
batched averaging rule automatically inherits its guarantees. Precision,
compression and learned-value changes should remain separate until the update
contract passes.
