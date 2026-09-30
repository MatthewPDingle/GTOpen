# Fixed-teacher action-value path: qualified building block

The next prediction diagnostic needs to learn how valuable each legal action
is under one fixed teacher. The live experiment's training regrets combine
different earlier policies; those records cannot be relabelled as the final
teacher's action values.

`stack_context_teacher_path_v1.py` binds the complete chronological public
history to native query rows, on preflop, flop, turn and river. It reconstructs
both players' earlier decisions, the original own-history links, and the native
24-suit canonical card keys. Each query includes only that player's cards and
the board visible at that decision. The full physical deal is label-generation
data, not a network input. Existing registry preparation remains the network
input contract; this helper does not introduce a feature matrix.

The teacher must be inferred once, with its original own-reach averaging and
all policy overrides, before applying an intervention. Then force both
players' earlier actions and the target action, keeping every future policy
row frozen. The existing fixed-profile root evaluator can now return that
action's value for the supplied conditional physical deal, including sunk
investments and exact preflop all-in terms. Use the original target strategy
to subtract its baseline and divide by the original starting stack.

Forcing only the target leaves off-path outcomes in the root value. Dividing
that value by arrival probability does not remove their contribution. Forcing
only the target player's past also leaves the opponent's off-path outcomes.
The synthetic forward/reverse payoff control explicitly rejects all three
shortcuts. Recomputing the teacher's own-reach average after forcing history
would change the teacher; the adapter instead copies and freezes the original
probability table.

## Evidence retained locally

- Path check v2 passed in 3.781 seconds on CPU: 918 native rows at 20bb/60bb,
  2,918 original own-history links, 1,980 native BOTH-player river paths,
  2,086 legal interventions, 298 invisible-future-card checks and 24 corruptions
  rejected. Each depth's 32-row retained evaluator batch repeats two distinct
  physical deals; this is an implementation fixture, not a population sample.
- Native payoff check v1 passed in 1.140 seconds: four invocations of the
  unchanged CPU evaluator, 16 targets covering both players on all four streets.
  The original fixture value replayed unchanged; the original target mix
  matched its action values within 8.89e-16. Every tested fold lost exactly the
  actor's invested chips. Maximum independent forward-cashflow error was
  7.11e-15; maximum chip-conservation error was 1.78e-15.
- Preserve the failed path check v1. It incorrectly required the visible
  format-2 query source and conditional format-3 label source to be identical.
  V2 corrected only that fixture binding, explicitly checked their shared raw
  fields, and preserved the original failed source, attempt and outcome. The
  implementation module did not change. No scientific cycle was retried.

Sources and receipts: `stack_context_teacher_path_v1.py`, path checks v1/v2,
`stack_context_teacher_native_check_v1.py`, and their attempt/result/failure
files in this directory. Native replay artifacts remain under
`stack-context-teacher-native-check-v1/`, bound by the result's SHA256 manifest.
The retained teacher probability table is a qualification fixture, not the
future complete 64-model teacher. No fitting, new scientific deal, CUDA work,
production change or additional scientific experiment occurred.

## Still required before a prediction experiment

This verifies native path intervention and fixed-board payoff transport. It
does not yet integrate the opponent's conditional range or unknown future
boards. Compute those with the original teacher's opponent-action likelihoods
and compatible entry mass; handle blockers and legal future runouts; retain
draw multiplicities and avoid applying the posterior twice. Add independent
posterior/future-board controls and repeated-label noise checks.

The original design's prospective teacher remains complete A-baseline played
generations 0..63, excluding unplayed fit 64, after successful main training.
Bind that bank and qualify inference before drawing diagnostic labels. The
actual public-flop split, separate preflop holdout, seeds, sample/fit/noise
budgets, statistical plan and diagnostic admission are still outstanding.

The live four-arm comparison and every registered input/gate remain unchanged.
Its required sequence remains all64 cycles/arm, actual complete-bank throughput
gate, fresh 4096x7 evaluation, independent readback and plain-English analysis.
Neither this implementation control nor that restricted heads-up comparison
can establish full-position/multiway preflop accuracy by itself.
