# Prepared visible-hand summaries; no trained candidate yet

The current physical-poker network receives 269 inputs encoding the player's
visible cards, street and betting history. These preserve the observation but
do not explicitly identify made hands or rank/suit patterns. The completed
dense fit diagnosis also found much larger training residuals postflop than
preflop. That motivates a representation experiment; it does not establish
representation as the sole cause, since the sampled targets are noisy too.

The new, unused encoder appends 33 deterministic summaries to the original
269 inputs. It keeps all original information, including turn/river order and
the complete encoded action history. The summaries include:

- Current best-five hand category and its ordered tiebreak ranks.
- Board rank multiplicities and distinct ranks.
- Board/hole suit counts, sorted without assigning meaning to suit names.
- Rank coverage of straight patterns, hole overcards and board-rank matches.

These are visible-card descriptions, not estimated equity, clean outs, GTO
labels or historical player tendencies. A river made hand may play the board.
Straight coverage does not imply a profitable draw. Every added input is zero
preflop, so the proposed test adds explicit poker structure to postflop inputs
without hand-editing preflop actions. Different public histories still retain
their distinct original inputs.

## Completed encoder checks

`sampled-visible-poker-features-v1-control-result.json` records:

- 12,288 deterministic random five-, six- and seven-card cases compared with
  an independent enumeration of all five-card subsets, plus five explicit
  rare-hand fixtures including a wheel straight flush and two sets of trips.
- 2,304 suit-relabeling and card-order invariance checks.
- All 1,326 preflop private pairs producing zero added features.
- 29,035 actual native observations from the first completed dense **training**
  batch: 235 preflop, 1,152 flop, 5,504 turn and 22,144 river. Features decoded
  from the original input matched those derived from the visible-card key.
- Eight invalid-input/future-card cases rejected.

This is correctness evidence for the encoder on the checked cases, not proof
of learning quality. No held-out evaluation outcomes were used, no neural model
was fitted, and no active training/evaluation source imports this encoder.

## Conditions for a future experiment

Finish the currently registered all-in trial and its two player-specific tests
first. If a representation experiment is then admitted, register its full
training and evaluation recipe before fitting. Keep the same physical game,
incoming ranges, action menus and player-specific evaluation requirements.
Version model files explicitly so a 302-input network cannot be silently loaded
as a 269-input policy, and include the encoder identity in its checkpoint.

Compare full played-policy averages on fresh evaluation streams; do not select
an attractive hand chart or an intermediate checkpoint. Account for the extra
input weights and initialisation when interpreting a comparison. An offline
fit improvement alone cannot establish better continuation values or preflop
ranges. Keep this separate from the all-in-estimator experiment so their effects
are not combined without evidence.

Neither production nor the experimental range preview changes here.
