# Exact sampled-update and average-strategy control passed

This is a prerequisite for a new GPU training implementation, not a completed
poker solver or a performance result. The test enumerated every sampling outcome
in a small imperfect-information game using exact rational arithmetic.

## What was checked

The control has 24 legal private/public deals, 60 information sets and seven
public decision nodes. It includes folds before the board is revealed, calls,
raises, postflop betting, an all-in, ties, unequal private-card frequencies and
a rare hand. It uses two different frozen strategy profiles in succession and
runs both without rake and with action-dependent rake. The smallest tested
chance marginal at an information set is approximately 0.00001160.

The independent full traversal sums all chance histories and every action. The
sampled traversal fixes a chance deal and opponent action tape, enumerates all
of the updating player's actions, and updates only that player's regrets.
Enumerating and weighting all possible tapes gives its exact expectation.
Both paths agreed on **all 128 information-set/action regret entries in each
round**, with zero error. There were 768 nonzero tapes in the first round and
864 in the second, for each utility mode.

The game deliberately contains seven information sets where the updating
player's own earlier action has zero probability, yet the correct regret update
is nonzero. These updates were retained. All seven re-enter in the second round;
their accumulated average policy was also checked exactly. Preflop information
keys hide both the future board and the other player's card; postflop keys reveal
the board. Every distinct public action history has its own node ID.

## Average-strategy contract

The average strategy required by CFR weights each round's policy by the player's
own probability of reaching that information set. It must not be averaged by
the other player's changing reach probability. See equation 3 in the
[primary MCCFR paper](https://papers.nips.cc/paper_files/paper/2009/file/00411460f7c92d2124a67ea0f4cb5f85-Paper.pdf).

For this proposed implementation, record the non-updating player's strategy
when visiting its information sets during the other player's traversal. That
player's earlier actions are sampled, while the updating player's actions are
all enumerated. With one frozen policy per batch and the target chance law:

`E[average increment at I,a] = Q(I) * own_reach(I) * sigma(I,a)`

Here `Q(I)` is the fixed chance marginal for the private hand and public cards
visible at the information set. It sums over hidden opponent cards and future
cards. It does not include action probabilities. Since it is constant across
rounds at the same information set, it cancels when the accumulated action sums
are normalized. No division by a tiny `Q(I)` is needed in the stored average
accumulator. The oracle compared the scaled increments, then verified normalized
averages after both policy rounds against the full own-reach reference.

This contract assumes fixed incoming ranges and unchanged chance sampling.
Changing the sampling proposal, merging incompatible information sets, skipping
zero-probability own actions, or updating strategies partway through a batch
requires a new derivation and verification. Different per-round weights must
be applied consistently to the reference and sampled accumulators.

## Deliberately incorrect variants were rejected

- Multiplying sampled regret updates by opponent reach a second time changes
  their expectation; those action probabilities were already used to sample.
- Multiplying by chance probability a second time is also incorrect.
- Collecting unweighted averages at the updating player's nodes weights them
  by the opponent's reach. After two policy rounds, this wrong method differed
  from the correct average by up to **17.573 percentage points** in this control.
  This is an intentionally injected error, not a finding about production code.
- Pruning updates solely because own reach is zero would discard the seven
  nonzero-regret witnesses. Their correct average contribution is zero in that
  round, which is different from their regret contribution.

## What remains unproven

This proves the stated expectation and averaging identities on the finite
control. It does not prove a sampled poker implementation, GPU reduction,
full-deck suit handling, practical convergence or capacity on the wide BB study.
Expected updates do not imply identical sampled training trajectories, and no
claim is made that applying CFR+ clipping after noisy updates reproduces full
CFR+. Start the implementation with ordinary regret matching.

Next: implement frozen-batch traversal and deterministic accumulation of
duplicate information-set updates, with keys that retain private hand, visible
cards and full action history. Compare the implementation with this oracle,
then measure state growth and updates on the actual wide geometry. Only after
those checks should time-to-independent-convergence be compared on a tractable
control and the full BB experiment admitted.

The script, pre-run registration and result are
`hu_sampled_updates_oracle_20260922.py`,
`sampled-updates-oracle-v1-registration.json` and
`sampled-updates-oracle-v1-result.json`. The run took 0.266 seconds, used no GPU,
changed no policies and did not touch production. Runtime is only the exact
small-control check; it is not a forecast for a poker training run.
