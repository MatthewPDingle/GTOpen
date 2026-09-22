# Conditional all-in values pass transport and noise controls

The new, separate format-3 research bridge replaces the sampled final-board
payoff **only at preflop all-in leaves** with equity over all 1,712,304 possible
remaining boards for the actual four private cards. Postflop decisions and
their sampled showdowns remain unchanged. This is not a production change.

The earlier exact-board control provides the reference integer win/tie/loss
counts for 16 existing private-pair fixtures. For a preflop all-in, no player
has seen a board or can make another decision. Integrating those unseen boards
therefore preserves the expected terminal cash flow for that private pair in
this two-player game. The argument would not justify averaging away a board
that a player has already observed. Earlier folded cards remain omitted, as
in the existing experiment.

## Correctness and isolation

- Format 3 explicitly identifies the conditional estimator. Format-2 consumers
  refuse its batches; it cannot silently masquerade as the old payoff protocol.
- Each label is bound to its original private-card ordering. Invalid totals,
  mismatched cards, duplicate deal cards, missing labels, extra label fields,
  stale policy inputs and incompatible formats were rejected.
- Observations, query order and visible neural inputs match format 2 exactly.
  Equity is simulation metadata; the policy never receives the opponent's hand
  or the conditional equity as an input feature.
- Cached versus direct query lookup matched exactly. A separate reference
  converted preflop all-in leaves into deterministic utilities using
  `equity * (pot - rake) - invested`, then ran the unchanged old walker. Its
  payoffs and update records matched the new walker, with identical RNG state.
- Controls covered uniform, unequal-action and forced-jam/call policies with
  zero, capped and uncapped rake. Synthetic win/tie/loss endpoint labels
  reproduced the original sampled-board walker within 2.85e-14 bb. These endpoint
  labels are correctness fixtures, not claimed exact private-pair equities.
- The first control verified 1,536 updater traversals and 43,095 unchanged
  postflop/opponent-policy records. Its independent readback reconstructed all
  stored comparisons and repeated ten input rejection checks.

Native checks verify label geometry and integer totals. They do not prove that
arbitrary caller-supplied counts enumerate the deck correctly. Training must
use the separately completed and independently reviewed exact cache, with its
recorded identity; that integration remains pending.

## Noise under fixed policies

Both controls use the same old 16 private pairs and 32 board/action replicates.
They compare the old and new estimators on the same deals, policy and action
seed. Board sets come from the earlier control, with a frozen random ordering
for flop/turn/river. These are diagnostic fixtures, not fresh strength tests.

For each private pair, we measured the variance across replicates of all four
BB root advantages (action return minus current-policy return), then averaged
over pairs and summed the four components:

| Fixed policy | New / old summed advantage variance | Reduction on this fixture |
|---|---:|---:|
| Uniform | 0.11793 | 88.2% |
| Dense trial's last actually played generation, 77 | 0.26621 | 73.4% |

Generation 77 was fixed by chronological position before the comparison. It
was not selected for poker performance; generation 78 was never played.
This is one current-generation training policy, not the final averaged bank.

For the learned policy, root action-return variances in bb squared were:

| Root action | Sampled-board estimator | Conditional all-in estimator |
|---|---:|---:|
| Fold | numerical zero | numerical zero |
| Call | 851.85 | 851.85 |
| Raise | 1,926.69 | 1,926.69 |
| Jam | 11,699.15 | 59.82 |

The sampled policy return is shared by all four advantage targets, so noisy
jam payoffs can affect the targets for non-jam actions as well. The learned
control verified 1,024 traversals and 31,727 unchanged postflop/opponent records.
Independent readback reconstructed all 512 paired fixture deals and checked 512
policy rows with a separate float64 forward pass; maximum probability difference
was 0.00002544.

These results support a controlled training experiment. They do **not** imply
73% faster convergence, improved ranges, a universal variance reduction, or a
bound on exploitability. Averaging just one component can change covariance
with other actions; the full advantage vector must be measured, not inferred
from the all-in equity calculation alone. Private-hand sampling, opponent-action
sampling, postflop board noise, regression error and context limitations remain.

## Next step

Finish and audit the exact training-pair cache. Preserve the ongoing hybrid
trial and its reserved evaluation. Then register a separate training comparison
that changes only the preflop all-in estimator, uses the same training schedule,
and reserves fresh evaluation samples. Continue testing both players and later
decisions; a better BB root score alone is insufficient for deployment.

Evidence: `sampled-physical-allin-bridge-control-v1-{registration,result,independent-review}.json`
and `sampled-physical-allin-learned-control-v1-{registration,result,independent-review}.json`.
The exact inputs and paired native outputs are hashed in those records and kept
under their matching `S:/GTOpen-research/` directories.
