# Next diagnostic: river call-versus-fold values

## What the fitting experiments ruled out

The original 512-step fit remains the best supported reference for the four
saved datasets. Shorter fitting underfit; longer fitting overfit. Explicit
pot/stack/price inputs raised mean postflop validation error 0.36%. Zero-output
initialization raised it 0.79%. Zero-output initialization plus public pot
scaling, preserving the original chip-error objective, raised it 4.81% versus
the original and 3.99% versus the zero-output control.

Pot scaling modestly helped smaller pots, but worsened the 200+ bb bucket
15.51%. It failed the predeclared gate in every dataset. Do not promote it or
the new initialization, and do not tune the scale divisor after seeing this
outcome. These checks narrow the search; they do not improve poker ranges.

Rather than another numerical tweak, the next diagnostic should ask a more
poker-specific question: can the baseline predict a river call's value relative
to folding, and how does it compare with a simple visible-cards-only reference?
This removes the common state-value offset from the two action targets.

## Stage 1: verify the stored river labels

Use the same four generation-77 source reservoirs and original partitions.
Inspect training and validation only; keep final-test rows out of the audit.
Select river decisions with both Fold and Call in their native legal menu.
Reconstruct the exact public state from the existing qualified catalog.
First verify in native controls that Call ends the hand at these states.

Let P be the current pot, C the incremental call, and R the configured rake on
the matched pot P+C. With cap >0, R=min(rake_fraction*(P+C),cap); a zero cap in
the current native code means uncapped. The difference between the recorded
Call and Fold advantages must equal one of:

- Loss: -C.
- Tie: (P+C-R)/2-C.
- Win: P-R.

The walk records action return minus its current-policy mean, so that common
mean cancels in Call minus Fold. The branch's constant value offset also
cancels. Confirm these identities using actual native transitions/payouts and
known win/tie/loss deals before auditing the reservoirs. Declare a numerical
tolerance before running (start from 1e-7 bb for saved float64 targets).

Record coverage, source weights and largest endpoint residual by dataset and
pot bucket. Investigate any mismatch instead of clipping or excluding it.
Matching one of the three endpoints checks units and terminal accounting; it
does not independently verify which opponent hand was dealt or its rank.

Relevant existing code: `research_sampled/state.rs` (river Call transitions and
payouts), `research_sampled/poker_reference_v1.rs` (Walk::finish and Walk::post),
and `board-later-public-state-catalog-v1.json` (public amounts and legal actions).

## Stage 2: a visible-only reference, not an opponent model

For every eligible validation input, decode only the actor's two cards and five
visible river cards from the existing observation. Enumerate the 990 legal
opponent pairs from the remaining 45 cards. Calculate exact win/tie/loss counts
against a uniform opponent, with card removal. Reuse results across identical
visible card sets, ignoring public history only for this uniform reference.

For equity E=(wins+ties/2)/990, predict the Call-minus-Fold value as
`E*(P+C-R)-C`. Compare it with the original saved network's prediction
`training_scale*(score_call-score_fold)` and with predicting zero difference.
Do not use the actual sampled opponent cards, hidden future cards, target
values or GTO Wizard outputs to construct the uniform reference.

This uniform-opponent calculation intentionally omits the real opponent's
incoming range and betting-history selection. It is not ground truth, GTO,
an estimate of the actual caller's equity, or a replacement policy. Its purpose
is to test whether a simple, physically valid hand-strength relationship
reveals structure the current network has not learned.

Use `solver::evaluator::evaluate7` in a separate Rust helper. The existing
`hu_board_hand_ranks_v1.rs` demonstrates native fixed-river enumeration. Check
known nuts, ties, suit relabeling, card order, overlap rejection, and exactly
990 legal opponent pairs. Compare selected enumerations with an independent
scalar implementation and the existing board-rank export. Distinguish shared
evaluator checks from a genuinely independent hand-ranking oracle.

## Fixed reporting and resources

- No new training, fit-budget changes or final-test scoring.
- Use original source weights. For this one action contrast, squared-error
  denominator is source-weight sum, not legal-action count times source weight.
- Report each dataset and the existing five pot buckets, plus equal-dataset
  means. Include original bb-squared MSE and error relative to zero difference.
  Do not select only examples where the uniform reference looks good.
- Bind original checkpoint/source/catalog identities and the new source/control
  hashes in a registration before the full comparison.
- Benchmark a small, deterministically selected prefix to set a realistic bound
  before enumerating all cases. Use native CPU parallelism, up to 16 workers
  when resources are free, rather than per-pair Python loops. No GPU required.
- Keep the shared locks, production-activity checks and 800 GB allocated-storage
  cap. Bound retained new outputs to 100 MB and the admitted full diagnostic to
  30 minutes. Do not duplicate historical datasets or retain bulky row traces.

If the uniform reference is useful, a separately registered visible-hand-strength
input experiment may be justified. If the network already beats it, the result
still helps distinguish basic hand-strength representation from range/history
conditioning. Neither outcome alone proves improved preflop play. Conditional
target-noise estimation still requires repeated situations under fixed policies.

Production remains unchanged. Accurate flexible ranges across positions,
stacks, betting menus and multiway play remain unproven. No research process
was left running at the end of the pot-scale comparison.
