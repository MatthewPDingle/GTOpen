# Two nearly equal negative scores caused the verification discrepancies

The prepared diagnostic completed in 25 seconds. It reproduced both historical
error-count differences and both original GPU board-average losses exactly.
An independent saved-array audit checked all 151,340 target decisions, rebuilt
prices from the retained native public states, and verified the arithmetic.

The original comparison still failed its accuracy gates and its full independent
readback. This explanatory check does not convert either failure into a pass.

## What happened

The network predicts a score for folding and another for calling. The current
conversion divides positive scores into action probabilities. When both scores
are nonpositive, it chooses whichever score is larger, with ties going to fold.

In the two flagged decisions, both scores were negative and almost equal. Tiny
differences between the CPU and GPU calculations reversed their ordering. The
fallback therefore changed the call probability completely, from zero to one or
one to zero. This was not merely a tiny probability change around 50%.

| Case | CPU call rate | GPU call rate | Reference benefit of calling over folding |
| --- | ---: | ---: | ---: |
| Board 51, state 50 | 0% | 100% | +1.181313bb |
| Board 101, state 48 | 100% | 0% | +1.996212bb |

The differences between call and fold scores were only about 0.00000003 to
0.00000009, in normalized score units. Both cases are outside the original
economic indifference band. The discontinuity in the fallback amplifies the
small numerical differences into meaningful changes for these individual hands.

Those hands are rare within the evaluated rows, so their effect on board-average
loss is small. That does not make their individual decisions equivalent.

## A second issue: the estimated values are wrong on these hands

Folding has exactly zero incremental value in this restricted test. The learned
fold values were approximately -0.02854bb and -0.02340bb. The learned call values
were almost the same negative amounts, despite the reference call advantages
of +1.18bb and +2.00bb. Thus the network is uncertain in the wrong place; these
are not two genuinely indifferent decisions according to the reference.

This points to two related tasks for the next method design:

1. Represent the known fold value exactly, and define an action conversion whose
   numerical behavior is tested explicitly. A separate learned fold score adds
   an unnecessary source of error in this particular terminal decision model.
2. Improve or calibrate the estimated call advantage, especially where a value
   error changes a meaningful decision. Fixing the fold score alone would make
   both predictions fold here, so that change by itself is not an accuracy fix.

These are design recommendations, not results from a new model comparison.
Future choices require separate controls and fresh evaluation boards. Do not
tune an alternative policy on these two known failing test cases or relax the
old readback tolerances after observing their outcome.

## What was checked

- Frozen seed 9297101, random-board arm, 362 inputs, selected update 8192.
- Original 40bb context, 70 public decision states, test boards 51 and 101,
  and every one of their 1,081 legal holdings.
- Original CPU matrix dimensions of 138,368 holdings per state and the 160
  full original GPU batches touching the target boards.
- Exact CPU/GPU feature equality for those GPU batches.
- Complete target raw scores, call probabilities, card/public-state identities,
  reference advantages, losses and disagreement masks saved locally.
- Independent arithmetic reconstruction without any further network inference.
- Historical error counts reproduced: board 51 GPU 994 / CPU 995 out of 75,652;
  board 101 GPU 908 / CPU 907 out of 75,670 eligible decisions.

The historical evaluation did not retain its raw scores. We reproduced its
counts and GPU board means, and directly observed the mechanism in this new
diagnostic. We cannot prove the original raw predictions were bitwise identical.

This check covers only two selected boards in one river Fold/Call context against
a uniform legal opponent. It does not establish full readback equivalence,
explain the balanced-training accuracy regression, or validate preflop ranges.

## Resources and retained evidence

The diagnostic used about 304 MB of reserved CUDA memory and wrote 4.06 MB of raw
evidence. The process exited successfully, its lock was released, and no training
or production changes occurred. GTOpen on port 56708 was untouched. Nothing was
pushed or deployed.

Evidence prefix: `stack-board-boundary-diagnostic-v1`.

- `-registration.json`: frozen scope, inputs, batch layout and resource limits.
- `-attempt.json` and `-result.json`: execution identity and retained outcome.
- `-readout.json`: independent saved-array audit, hashes and case details.
- `S:\GTOpen-research\stack-board-boundary-diagnostic-v1`: complete raw arrays.

The earlier approval block was an overly broad interpretation of the monitoring
restriction on starting another learning experiment. This check was limited to
debugging the already authorized study's failed verification. The original
failed attempt was neither restarted nor replaced. A new training comparison
has not been launched.
