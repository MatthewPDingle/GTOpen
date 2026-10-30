# Where the previous model's remaining weakness appeared

This is a descriptive breakdown of the already completed
`exact-initial-wider-study-v1` test. It uses no new deals, fits no policy and
does not change the running root-retention trial.

The frozen challenger gained an estimated **0.2304 bb per incoming hand**
against the prior pilot in this one BB-versus-BTN context. Its original
simultaneous interval was approximately **[0.0303, 0.4305] bb**. That interval
supports a remaining weakness in the tested model. The breakdown below has
no new per-group confidence guarantee.

## The actionable distinction

The model was not simply folding too much. Relative to the baseline, the
challenger's overall frequencies moved approximately as follows:

| Action | Baseline | Challenger |
| --- | ---: | ---: |
| Fold | 41.55% | 43.02% |
| Call | 38.51% | 47.54% |
| Raise | 19.23% | 8.62% |
| Jam | 0.71% | 0.83% |

Among classes where the frozen challenger chose to call, the combined gain
was **+0.1648 bb per incoming hand**. Classes where it chose to fold
contributed **+0.0773**, raises **+0.0065**, and the one jam class **-0.0182**.
These are additive contributions over the entire incoming range, not the
gain each time that group is dealt.

This points toward better allocation between fold/call/raise, rather than
indiscriminately widening every hand. The challenger is a diagnostic pure
class response against frozen later play, not a replacement equilibrium range.

## Exhaustive hand-family breakdown

Broadways mean both ranks are T or higher. The other categories exclude
hands already assigned to an earlier category; all 169 classes are included.

| Hand family | Incoming mass | Contribution to challenger gain, bb/entry |
| --- | ---: | ---: |
| Other offsuit hands | 61.94% | +0.1066 |
| Pocket pairs | 5.89% | +0.0726 |
| Suited broadways | 2.88% | +0.0236 |
| Other suited hands | 15.88% | +0.0184 |
| Other suited aces | 2.30% | +0.0158 |
| Other suited connectors | 2.48% | -0.0013 |
| Offsuit broadways | 8.63% | -0.0053 |

Pocket pairs contribute materially despite their relatively small mass. The
challenger calls 22 through 99 and raises TT through AA in this fixed context.
Examples of irregular baseline assignments are 22 raising 68.5%, 33 raising
approximately 0%, and 88 raising 91.5%. Both independently trained historical
responders choose calls with 22 through 88 and show the same positive point
contributions for those hands on this test. This is useful evidence for
investigating estimation instability; it is not a proof that these frequencies
should be imposed on the game.

The older frozen responder's total is approximately -0.0054 bb/entry. That
near-zero total masks offsetting contributions: pocket pairs +0.0575 and
other offsuit hands -0.0942. Therefore, one near-zero aggregate diagnostic
does not establish that the range is accurate or that all weaknesses vanished.

The new challenger's AKo jam contributed -0.0182 bb/entry. Not every choice
learned from its 256 training observations per class generalized profitably.
The earlier split-half instability finding still matters; this chart must
not be installed as a learned policy.

## What changes next

Nothing in the running experiment is retuned from this breakdown. The full
78-update root-retention trial, independent audit and already prepared fresh
evaluation remain the next tests. Preserving all first-decision samples is a
specific attempt to reduce an avoidable source of variance; downstream
continuation errors can still remain.

If the new independent test improves, assess whether that improvement survives
replication before expanding contexts. If it does not, retaining root samples
was insufficient and continuation value estimation deserves the next focused
investigation. More calling by itself is not the acceptance criterion.

## Verification and limits

`hu_exact_initial_wider_attribution_20260924.py` checked all 2,048 test-summary
hashes, reconciled all 131,072 test observations and class counts, reconstructed
the two sampled call/raise terms independently, and added the registered exact
fold/jam offsets. Both overall totals and both exhaustive groupings agree
with the original reported estimators within 1e-12 bb. All 169 class rows are
saved in `exact-initial-wider-attribution-v1-result.json`.

This readback uses the existing native payoff evidence. It does not rerun
poker traversal, provide fresh holdout evidence, certify the entire game,
or validate other positions, stack depths, sizes or multiway play.
