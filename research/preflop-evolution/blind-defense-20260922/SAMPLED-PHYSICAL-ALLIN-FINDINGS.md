# Cleaner all-in training reduced shoving; calling remains unresolved

The 39,936-deal conditional-all-in candidate completed both predeclared player
checks and both independent audits. It is not qualified for deployment.
The physical context remains BB versus a fixed BTN opening range at 200 bb,
with a restricted betting menu. This is separate from the UTG/LJ preview.

## Changes in the BB range

| First action | Dense baseline | Direct-preflop hybrid | Dense with exact all-in values |
|---|---:|---:|---:|
| Fold | 53.81% | 45.84% | 55.73% |
| Call | 26.04% | 28.84% | 26.16% |
| Raise to 6 bb | 12.87% | 13.48% | 16.31% |
| Jam to 200 bb | 7.28% | 11.83% | 1.80% |

These are complete-test-deal-weighted strategy frequencies, not an unweighted
average of 169 cells. All 169 classes are retained in the comparison artifact.
Different test streams and both players' changed policies prevent a paired
strength-improvement claim. The dense baseline used float32 evaluation; the
hybrid and new all-in candidate use separately checked float64 inference.

The main structural change is substantially less shoving. Calling barely moves,
and aggregate folding increases. Removing all-in board noise did not by itself
resolve the original missing-calls problem.

## Fresh strategic checks

The complete 78-model played bank was frozen before evaluating 8,192 response-
training deals and 16,384 held-out deals. Both tests retain sampled-board
payoffs, the originally registered counts, selection rules and reserved seeds.
Each player family uses alpha .025, for joint error at most .05 across these
five BB and three BTN comparisons within this trial.

| Tested change | Measured gain, bb per original spot entry | Conservative interval |
|---|---:|---:|
| BB: separately trained first-action response | -0.643 | -1.964 to +0.677 |
| BB: always fold | -0.484 | -1.696 to +0.727 |
| BB: always call | -0.342 | -1.456 to +0.772 |
| BB: always raise | -1.204 | -2.218 to -0.190 |
| BB: always shove | -12.314 | -14.868 to -9.761 |
| BTN versus BB jam: separately trained response | -0.081 | -0.881 to +0.720 |
| BTN versus BB jam: always fold | -0.066 | -0.847 to +0.715 |
| BTN versus BB jam: always call | -0.587 | -1.512 to +0.338 |

No tested alternative demonstrates a profitable improvement. This does **not**
prove approximate equilibrium or accurate hand ranges. A separately learned
response can be worse than the original policy because its estimates are noisy;
a negative response gain is not negative exploitability. The intervals remain
wide, and these tests do not optimize all later decisions.

BB's response-training support rule retained baseline behavior for 76 test
deals; BTN's did so for 34. BTN calls approximately 18.37% conditional on the
candidate's BB jam reach. Its response gains above are per original spot entry,
not per jam. Earlier dense/hybrid BTN diagnoses were post-hoc, unlike this
predeclared second-player family; do not compare them as equal evidence.

## The average still contains early training behavior

A post-audit decomposition reconstructs the published BB range within 4.44e-16.
It retains all 78 generations and all 169 classes, without selecting a new bank.

| Played generations | Fold | Call | Raise | Jam |
|---|---:|---:|---:|---:|
| 0-12 | 57.08% | 19.87% | 15.35% | 7.70% |
| 13-25 | 60.91% | 22.64% | 13.98% | 2.48% |
| 26-38 | 62.60% | 24.44% | 12.51% | 0.45% |
| 39-51 | 53.53% | 29.92% | 16.52% | 0.03% |
| 52-64 | 50.93% | 29.12% | 19.92% | 0.03% |
| 65-77 | 49.33% | 30.99% | 19.57% | 0.11% |

About 94.2% of the averaged shove frequency comes from the first 26 generations.
The initial uniform generation alone contributes 0.32 percentage points to each
root action. These are contributions from ordinary full-bank averaging, not
an imposed hand-level minimum frequency.

This suggests the average still contains substantial early behavior. It does
not justify discarding that history or claiming the last block is stronger:
opponents and continuations change during learning. Some hands remain troubling.
For example, 99 folds about 23.2% in the average and 46.5% in the last block.
The apparent aggregate improvement can hide worse individual-hand behavior.
No latest-only replacement, hand patch or new deployment was made.

## Next investigation

The earlier direct-preflop hybrid removed neural fitting at preflop decisions
but still used noisy sampled all-in outcomes and jammed more. The new dense
trial removes all-in noise but retains neural preflop fitting. The missing
controlled combination is **direct per-hand preflop learning plus exact all-in
values**. That can test whether neural fitting is still distorting important
calls without mixing in a larger architecture at the same time.

Prepare that combination with explicit source/checkpoint formats and integrated
controls before training. Preserve this candidate and its inspected streams.
Do not use individual held-out hand values as training targets. A cleaner fresh
evaluation is also needed: the separately checked conditional evaluator can
reduce all-in noise in both response selection and testing, but requires its
own protocol, labels and reserved streams before use. Neither a nicer chart
nor an improved fitting loss is a strength qualification.

The visible-hand summaries and matched initialization remain prepared follow-ups,
not a newly trained model. Longer training also remains an option; temporal
changes alone do not choose its budget or prove that it fixes the weak hands.

## Verification and evidence

Training completed 78 updates and passed full replay. Original evaluation v1
failed the numerical control before any held-out draws. The diagnosed float64
repair passed 256-deal complete-bank controls and independent readback without
changing weights, sample counts or tolerances. See `ALLIN-NUMERICAL-REPAIR.md`.

The repaired BB evaluation took 1,188.5 seconds, including its fresh numerical
controls; its independent audit took 396.7 seconds. BTN evaluation took 145.9
seconds and readback 60.4 seconds. BTN's independent hand enumeration matched
native showdown values within 2.842e-14 bb for all 24,576 training/test deals.
The BB audit checked all batch evidence and reconstructed both chance streams,
response selection and interval arithmetic. Neither audit reran model fitting.

Evidence prefixes: `sampled-physical-allin-evaluation-v2`,
`sampled-physical-allin-btn-evaluation-v2`, `sampled-physical-allin-repair-v1`,
`sampled-physical-allin-comparison-v1`, and
`sampled-physical-allin-bank-diagnostic-v1`.
Production and the experimental preview remain unchanged.
