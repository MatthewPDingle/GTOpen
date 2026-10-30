# Exact checks expose remaining all-in errors

Both candidates have definite, independently reconstructed mistakes at the
tested all-in decisions. This is stronger adverse evidence than the earlier
inconclusive sampled tests. Neither candidate is ready for deployment.

## Complete calculation

The fixed BB-versus-BTN 200 bb context has 776,650 compatible positive-probability
physical private pairs, represented by 47,478 suit-canonical cases with player
roles preserved. The complete equity table includes all 1,712,304 possible boards
per case. Previously reviewed counts supplied 28,438 cases; the remaining 19,040
took 2,100.66 seconds including control overhead. The population/equity audit
passed, with independently reconstructed probability error below 6.1e-20.

Both full 78-generation policy banks passed CPU/GPU catalog agreement, native
reference comparisons and independent repeated CPU lookup. No model was selected
after looking at these endpoint results. No sampling interval is needed for
these finite calculations, subject to their stated numerical/model assumptions.

## Profitable unilateral deviations

Values below are **bb per original entry into this fixed spot**, not per entire
poker hand, per shove, or an estimate of total exploitability.

| Restricted deviation | Combined 269-input model | Visible-feature 302-input model |
|---|---:|---:|
| BTN: best class-based fold/call response to BB shove | +0.147081 | +0.151880 |
| BB: reallocate only existing fold/shove probability | +0.187170 | +0.153994 |

Each test changes one player while holding the other player's policy fixed.
The two gains are not simultaneously realizable profit and should not be
presented as a single win rate. These are lower bounds on available unilateral
improvement, not upper bounds on full best-response gain. The opponents differ
between candidates, so the table does not rank them against a common opponent.

BTN's exact conditional call rate after a shove changes from 25.16% to 15.25%
for the old model and from 26.26% to 12.83% for the new model under the respective
best class response. In the new candidate, 55 calls 71.90%, KQo calls 51.40%, and
J9s calls 85.02%; the exact response folds those classes against that frozen BB
shoving range. This is specific to the studied opponent and 200 bb price.

The BB check retains each hand's call and non-all-in raise probabilities exactly.
It moves only that hand's combined fold/shove probability to the more valuable
of those two actions. Its shove rate falls from 4.17% to 2.34% for the previous
model and from 3.71% to 2.26% for the new one. This does not establish the right
call/raise distribution or joint equilibrium.

For a concrete new-model example, Q9s shoves 49.64%, despite an exact shove value
of -11.91 bb versus -1 bb for folding against the frozen BTN policy. Q9s accounts
for 0.01606 bb per entry of the restricted BB improvement. KQo shoves 12.84%
with shove value -7.69 bb. The errors therefore are not merely display rounding.
Classes shoving at most 0.5% account for 0.03869 of the new model's 0.15399 bb
restricted gain; that descriptive cutoff does not identify which training
iterations caused the errors.

## What this changes next

Additional visible features and more realistic-looking calling frequencies
have not resolved these concrete defects. Before another full architecture
trial, decompose the exact errors across all saved played generations against
each fixed final opponent. That can distinguish persistent learning mistakes
from pollution by early policies in the equal-weight average. It must not select
and promote a flattering final iteration or discard early policies post hoc.

The call/raise continuations still need stronger evaluation. The exact-component
control prepares one way to reduce avoidable noise there, but these all-in tests
do not establish postflop or cross-stack accuracy. No hand-specific corrective
patch or production replacement follows from this diagnosis.

## Evidence and implementation limits

- `complete-private-allin-cache-v2-{result,independent-review}.json`: complete
  support, weights, reused counts, new native counts and independent sampled-board
  scoring. The audit does not rerun every exhaustive board enumeration.
- `exhaustive-btn-response-v2-{result,independent-review}.json`: all class
  contributions, source policies and exact BTN gains. Independent scalar-sum
  disagreement is below 2.9e-16 bb; cashflow conservation error is below 1.5e-14 bb.
- `bb-fold-jam-response-v3-{result,independent-review}.json`: all 169 BB classes,
  unchanged call/raise policies and exact restricted gains. Independent scalar
  disagreement is below 3.6e-15 bb.

The BB v2 runner reached output serialization but stopped because NumPy's integer
class-count scalar was not JSON serializable. Its stopped status and empty result
are preserved. V3 converts persisted numeric scalars to built-in numbers and uses
new output names; its mathematical calculation and selected policies are unchanged.

The finite context still omits earlier folded cards, fixes incoming ranges and
uses a limited betting menu. Neither the cache nor these endpoints certify full
physical-poker equilibrium or general preflop accuracy.
