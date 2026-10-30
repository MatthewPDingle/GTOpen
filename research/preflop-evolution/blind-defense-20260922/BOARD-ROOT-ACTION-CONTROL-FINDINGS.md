# Root-action decomposition: correctness control passed

The retained evaluation can be separated into the values of folding, calling,
raising and shoving without retraining or changing later play. Both predetermined
batches reproduced their original native results exactly. This qualifies the
diagnostic; it does not show that either strategy is better.

## What was checked

The two batches were `test-000000` and `test-032768`, one from each retained
evaluation attempt. They contain 64 existing physical deals, evaluated under all
eight original crossed profiles. Each profile was copied four times, changing
only BB's initial action to fold, call to 2bb, raise to 6bb, or shove to 200bb.
The original averaged continuation policies, game, conditional preflop all-in
equities and sampled public boards were preserved. Suit-canonical root identities
were reconstructed from BB's visible cards, without using hidden cards.

Multiplying the four action values by the original action probabilities recovered
the saved values for both players and expected rake. The largest discrepancy was
1.42e-14 bb. Native forward-cashflow and pot-conservation checks also passed.
Five deliberately invalid transformations were rejected in each batch: changed
later probabilities, wrong root actor, wrong root identity, changed batch input,
and a mixed root action in place of the required pure action.

A separate readback compared 930,336 policy rows and recalculated 1,536 mixtures
using 40-digit decimal arithmetic. Both original native replays were exactly
identical to the archived results; the largest decimal mixture discrepancy was
2.19e-14 bb. This review used the same frozen poker evaluator's outputs, not an
independent poker engine or another neural inference run.

## Cost and next step

Each 32-profile forced evaluation took 0.84–0.89 seconds. Including archive
restoration, validation, input serialization and output retention, each batch
took 5.13–5.45 seconds. The complete control invocation took 183.61 seconds,
mostly the global storage admission scan. Independent readback took 7.58 seconds.
The two control folders retain about 152 MB. No GPU was used, no new deals were
sampled, and production was not changed.

The next step is a fixed-input CPU worker benchmark, then a bounded replay of the
original 65,536 deals. Its purpose is to distinguish costly root-action differences
from close choices across all 169 hand classes. Reusing these deals is exploratory:
maximizing the resulting action values is not a verified best response, an
exploitability bound, or a fresh confirmation of improved playing strength.

## Bound evidence

- Control registration: `board-root-action-control-v1-registration.json`, SHA256
  `1b4e3ffa642290579de0d3ebd91451e9a5f8f1d63f4548eae77c8440fd2d59b7`.
- Control result: `board-root-action-control-v1-result.json`, SHA256
  `9cbcd16b35feeb8047ff7e3bf24bf64ab4203da08fecc094bc77cac6e8aa88be`.
- Completed readback: `board-root-action-control-v1-review.json`, SHA256
  `235280d6125371efbfe1d1b4b65abf1bc18528a4bf24a6b8ee8ad892935b894f`.
  It resolves the result's historical `independent_readback_pending` flag; the
  original result has not been rewritten.
- Raw control evidence: `S:\GTOpen-research\board-root-action-control-v1`.

The full replay had not launched when this control report was written.
