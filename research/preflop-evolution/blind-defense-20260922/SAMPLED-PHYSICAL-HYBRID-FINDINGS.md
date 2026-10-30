# Direct preflop tables have not demonstrated better ranges

The hybrid candidate completed 39,936 training deals and its full independent
training replay. Its repaired evaluation also completed and passed the final
audit: 8,192 response-training deals, 16,384 separate test deals, all 78 played
generations, and the original five comparisons. Generation 78 was excluded as
planned. This is the BB-versus-BTN context, not the UTG/LJ preview.

The candidate is **not qualified for production or preview promotion**. Using
retained preflop targets directly changed its play, but did not establish better
accuracy. Those targets still contain sampling noise and depend on imperfect
postflop strategies.

## Completed root evaluation

Values are gains from changing BB's initial decision against the candidate's
frozen opponent and later strategies, in bb per study entry. Intervals use the
registered bounded paired calculation with 5% family error across five tests.

| BB alternative | Estimated gain | Simultaneous interval |
|---|---:|---:|
| Response learned on the separate training stream | +0.798 | -0.899 to +2.495 |
| Always fold | +0.734 | -1.037 to +2.505 |
| Always call | +0.472 | -1.136 to +2.079 |
| Always raise | -7.807 | -9.702 to -5.911 |
| Always jam | -25.639 | -29.250 to -22.027 |

The learned-response estimate is larger than the dense candidate's +0.389 bb,
whose interval was -0.990 to +1.768. This is **not a statistically established
regression or improvement**: the trials have different test streams, opponents
and continuations, and the hybrid required a float64 evaluation repair. They
were not evaluated head-to-head with paired outcomes. Neither test bounds the
full best response from above or establishes equilibrium.

The hybrid responder met the minimum 16 training observations in 167 of 169
classes. Its other two classes retained the baseline mix for 90 test deals;
they were not omitted. This contrasts with full class support in the dense
trial and illustrates how small some per-hand samples remain.

## How the displayed action mix changed

These are deal-weighted BB root mixes on each complete test stream. They are
descriptive, not measures of range correctness.

| Candidate | Fold | Call | Raise | Jam |
|---|---:|---:|---:|---:|
| Dense neural baseline | 53.81% | 26.04% | 12.87% | 7.28% |
| Direct-preflop hybrid | 45.84% | 28.84% | 13.48% | 11.83% |

Some hands move in a superficially appealing direction, such as AJs calling
59.93% instead of 5.96%. Others remain concerning: 99 jams 86.48%, and KQo
jams 51.71%. These examples cannot establish the correct strategy for those
hands, and they will not be patched or reused as training targets. Wider ranges
and more calls alone do not demonstrate progress toward the user's goal.

## Numerical repair and evidence

The original float32 evaluation failed a CPU/CUDA comparison before generating
held-out deals. It remains preserved. The diagnosed issue was a nearly tied
negative-score river bet/check decision. A separately registered float64
evaluation widened the same stored weights; it did not retrain, select another
checkpoint, change the policy rule or alter the reserved seeds and test counts.
See [repair status and the action-label correction](HYBRID-NUMERICAL-REPAIR-STATUS.md).

The repaired evaluation's 256-deal CPU controls had identical saved policies
and checked payoffs to CUDA. The final reviewer reconstructed 1,536 batches and
81,920 paired differences, replayed both chance streams and checked all artifact
hashes and interval arithmetic. Maximum root-mixture discrepancy was
2.85e-14 bb; maximum forward-cashflow discrepancy was 7.39e-13 bb. The reviewer
did not independently rerun neural inference or native traversal.

Evidence: `sampled-physical-hybrid-evaluation-v2-{registration,result,status,independent-review}.json`
and `sampled-physical-hybrid-comparison-v1-result.json`. The latter retains all
169 hand classes and the dense comparison's source identities.

## Supplementary BTN response diagnosis

The separate post-hoc diagnosis and its independent arithmetic readback also
completed. BTN calls 52.42% conditional on this candidate's BB jam. A class
response selected on the existing training stream gains an estimated 0.271 bb
per original spot entry, or 2.287 bb conditional on reaching that jam. This is
another indication of unfinished strategy, not a fresh statistical confirmation
or a deployable response. Always calling and always folding lose 1.305 and
0.995 bb per entry respectively relative to the existing BTN response.

The independent five-card enumerator checked all 24,576 train/test showdowns
against native terminal values (maximum difference 2.85e-14 bb). The final
review reconstructed response choices and all 16,384 test differences. Forty-two
test deals retained the baseline BTN action due to insufficient class support.
These artifacts are `sampled-physical-hybrid-btn-jam-diagnosis-v1-{registration,result,status,independent-review}.json`.
No such result is a new simultaneous interval or part of the original five-test
family. The next all-in trial predeclares both players' tests instead.

## Next experiment

The already prepared [conditional all-in trial](SAMPLED-PHYSICAL-ALLIN-PLAN.md)
returns to the dense baseline and changes only the training estimator for
preflop all-ins. It averages all possible remaining boards for each sampled
private-card pair rather than learning that terminal value from one board.
It preserves ordinary postflop sampling and evaluates both BB and BTN on fresh
reserved deals. This tests an identified noise source; it does not assume that
all-in noise is the sole cause of the remaining range problems.
