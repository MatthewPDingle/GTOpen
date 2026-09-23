# Later-weighted averaging: fresh experiment passed its narrow screen

23 September 2026. This is the prospectively registered 78-update experiment,
using one fresh seed and the unchanged training algorithm. No checkpoints were
selected afterward. The equal and linear outputs use the same complete played
bank, with weights 1 and generation+1 respectively. The unused generation 78
is excluded. Both players' later decisions use own-action-reach weighting.

## Exact results

Numbers are profitable unilateral deviations in bb per entry to the fixed
200 bb BB-versus-BTN game. Smaller is better. BB's test reallocates only existing
fold/shove mass; BTN's test changes its fold/call response to the initial shove.

| BB output / BTN output | BB restricted gain | BTN restricted gain |
|---|---:|---:|
| Equal / equal | 0.165138 | 0.138799 |
| Equal / linear | 0.172324 | 0.054446 |
| Linear / equal | 0.038607 | 0.128738 |
| Linear / linear | 0.054021 | 0.054245 |

Giving later rounds more weight reduces the two tested gains by approximately
**67% for BB and 61% for BTN** when both players use the linear output. Both
clear the predeclared requirement of at least 25% reduction. Cross-pairings are
reported in full; opponent-dependent values were recomputed for every pairing.
The two unilateral gains must not be added into an achievable joint win rate.

BB's population fold/call/raise/shove mix changes from
39.98 / 38.62 / 17.82 / 3.58% to 39.31 / 39.71 / 18.86 / 2.12%.
That mix change by itself is not evidence of accuracy. The exact deviation
calculation supplies the improvement evidence, within its stated scope.

## Remaining errors are meaningful

Linear weighting does not eliminate the errors. In the linear/linear pair,
A8s still shoves about 51.0%, while its exact shove value is -8.37 bb versus
-1 bb for folding. AQo shoves about 99.4%, with shove value -1.77 bb. These are
conditional action values for those hands against this fixed opponent.
They are not recommendations to replace all shoves with folds; ordinary
calls/raises require their separate evaluation.

BTN calls the initial shove about 19.5% conditional on reaching that response;
the exact class-only best response to this particular BB calls about 11.8%.
The largest remaining BTN gain contributions include KQs, K8s and AJs calls.
The response data are sparse, and this experiment changes output averaging,
not the underlying sampling or training targets. It is not a solved game.

## Verification and scope

Training completed 39,936 fresh deals in 9,805 seconds, with 78 full updates.
The independent replay passed all deals, action RNG states, reservoir insertion
and final arrays, all generated preflop tables, supported policy rows, frozen
model-bank progression and recorded resource checks. It checked 79,872 native
cashflow/reference traversal records; it did not rerun neural fitting.

The complete 47,478-canonical-pair population was evaluated with the audited
exact board cache. CPU/CUDA initial-decision probabilities agreed exactly.
The independent outcome-wise chip-accounting review agreed within 2.88e-16 bb;
cashflow conservation error was at most 1.43e-14 bb. All four study stages passed.
Total study time including audits was about 172 minutes.

This is one seed, one incoming-range context, one stack size and restricted
first-decision deviations. It does not certify ordinary calling/raising,
postflop strategy, other positions/stacks, or agreement with GTO Wizard.
Production 56708 and the preview were not changed.

## Next decision

Proceed to candidate-specific numeric/resource admission for the already
prepared broader root evaluation, using the complete linear-weighted bank.
Then register the final fixed sampling/storage/time budget before drawing its
training and independent test streams. Its question is whether calls and
ordinary raises reveal additional profitable deviations. The passing exact
screen authorizes that research, not deployment. Exact initial-action training
targets remain a later way to address the known all-in errors directly.

Primary evidence: `later-average-study-v1-result.json`,
`later-average-fresh-pilot-v1-independent-review.json`,
`later-average-exact-v1-result.json` and its independent review. All class rows
and all cross-pairings are retained in the exact result.
