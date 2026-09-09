# Measured preflop sizing

A player model has two separate jobs: deciding whether to fold, call or raise,
and deciding how much to raise. A history-backed hand range does not by itself
establish a history-backed size choice.

The Preflop Lab's evidence badge reports **Hands** and **Sizing** separately.
Expand it to inspect their sources and limitations. A measured hand policy can
still have fallback sizing. Painted hand probabilities and edited sizing are
checked separately against the supplied dataset.

## Amounts and menus

Opening and isolation sizes are raise-to amounts in big blinds. Re-raise
sizes are multiples of the previous raise-to amount: a 3x re-raise facing an
open to 2.5bb is a raise to 7.5bb, not an additional 7.5bb.

The runtime maps observed sizes to the available non-jam menu by nearest
logarithmic distance, breaking ties toward the smaller legal amount. Duplicate
targets combine their probability. Menu entries are not guaranteed a nonzero
frequency: variation should come from the observations, not an invented floor.
The engine's minimum-raise and near-stack rules still determine legal actions.

Recorded ordinary sizes distribute the existing **raising** probability.
The existing fold, call and explicit jam probabilities remain separate.
In this version, sizing is independent of the individual hand conditional on
raising. It does not claim that every hand uses the same sizes in real games;
it is a pooling assumption until hand-dependent sizing has sufficient evidence.

## Source limitations

The source is the validated Ignition NL10 regular anonymous-opponent pool,
excluding the user's hero seat. Common contexts can have their own estimates;
sparse contexts borrow broader observed distributions. An eight-player game,
different blind ratio, unusual stacks or a distant menu can be an unvalidated
transfer even when the original observations are genuine.

Historical development periods have already been inspected. Chronological
prediction checks on them are retrospective evidence, not a fresh independent
test or proof of a profitable strategy. More branches also create new arriving
ranges; solve convergence measures accuracy within the configured model, not
accuracy of that model's assumptions about opponents or postflop play.

## Current release

The extraction found **7,545 ordinary non-opening raises** in 34,466 validated
hands across 555 sessions. Another 610 jams are kept separate. Position/table
detail improved ordinary 3-bet sizing prediction in the retrospective check;
isolation raises, squeezes, limp re-raises and later re-raises use pooled
observed distributions. Three-or-more-limper payment groups borrow the
same-limper-count pool of only 50 raises, so that part remains sparse.

On a menu of 2, 2.5, 3 and 5bb, a common observed 4bb isolation raise maps to
5bb. That option can still dominate; adding a 4bb option would represent it
more closely. The model does not change your configured size menu.

The [study, support counts and progress graphs](../research/ignition-action-sizes/README.md)
record the selection gates and limits. Existing hand probabilities, opening
sizes and non-Ignition library models are unchanged by this release.

## Compatibility

`BucketPolicy.raise_sizes` remains a list of absolute bb amounts and weights.
`raise_multiples` is a separate optional list for re-raise-to multiples. A
policy may specify only one nonempty list. Empty lists retain the prior
minimum/maximum sizing rule. Explicit jam conversion removes ordinary mixes.

Older binaries ignore the new multiplier field and retain their fallback;
they cannot accidentally reinterpret a multiplier as a bb amount. Use the
updated app to apply measured re-raise sizing. Existing saved games retain
their stored policies until their models are updated and the game re-solved.
