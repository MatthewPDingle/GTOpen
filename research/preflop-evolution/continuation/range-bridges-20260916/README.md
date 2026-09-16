# N03: coverage between concentrated and broad ranges

Prospective specification, prepared while N01 is still running. This experiment
is queued, not permission to overlap its GPU jobs with another workload.
The night-shift deadline remains 16 September 2026, 20:49:02 UTC.

## Motivation from training data only

The two preliminary feature revisions failed the training-family screen. The
largest original shape-model CV errors include `train-eight-equal-02` (16.79%
pot) and `train-eight-straddle-03` (12.51% pot). One player's distribution in
these cases has an effective hand-class count near one. The range-weighted
reference BR errors are below 0.1% pot, and sample pot-accounting deviations
are around 0.2% or less; neither explains errors of this size.

Select the worst original shape/0.1 CV case from each training family as the
narrow/problem parent: six-modeled-03, seven-open-03, eight-equal-02 and
eight-straddle-03. Pair each with that family's broad case 00. Only training
outcomes informed this selection; no evaluation labels are used.

## Fixed data expansion

Normalize each parent to class-combination probability, then interpolate both
players' range marginals with broad-parent fractions 25%, 50% and 75%. Cross
each interpolation with SPR 4, 10 and 16. This produces 36 synthetic range
contexts across four source families. These are research fixtures, not claimed
real-player profiles. All derivatives inherit their parent's source-family fold.

Use 20 fresh stratified flops per case (four per texture stratum), totaling
720 training references. This trades per-context board coverage for more range
contexts; do not describe the individual targets as exact all-flop values.
Retain the original 24 training cases and the two N01 development cases. The
final candidate has 62 training contexts. Keep the original shape encoder and
ridge penalty 0.1 fixed: this isolates data coverage from model selection.

All references use the unchanged zero-rake HU menu, 50%-pot bets, one 100%-pot
raise per street, no extra all-in action, and both GPU and full CPU stopping
criteria at 0.1% pot. The immutable night2 reference executable is reused.
Range cleanup and tiny probe additions are recorded identically for reference
solving and prediction. Inverse inclusion, suit multiplicity and compatible
hand-pair mass remain in the label aggregation.

## Training eligibility and prospective evaluation

Fit four family-held-out models on the augmented data. Evaluate eligibility on
the **original 24 training cases** with their family excluded, against the
original shape/0.1 family-CV results. This keeps the compared validation cases
fixed while testing the additional training data. Require at least 5% lower
equal-family mean error and no family worse by more than 5%. Report new-case CV
results separately, without using them to redefine the gate.

If eligible, freeze the shape/0.1 candidate fitted on all 62 contexts, then
generate the reserved 400 evaluation references: all eight historical held-out
source cases, each on 50 new boards (ten per stratum). Their two source families
never enter fitting, and all evaluation boards are disjoint from training, N01
and previous studies. Case identities are previously evaluated, so this is new
board evidence on held-out source families, not entirely new-context validation.

The fixed evaluation screen requires at least 15% lower equal-case family MAE
than original Balanced in **each** held-out source family, and no individual
case more than 10% worse than the original frozen learned candidate. Report
paired stratified bootstrap uncertainty and per-hand reference quality. If the
candidate fails, do not tune it on this evaluation set. If it passes, proceed to
inference parity, independent action-value checks and repeated matched GPU
timing before any production consideration. The live app remains unchanged.

## Budget and safety

Do not start this runner until the current research GPU job is verified done.
Check live app activity before each bounded batch, validate completed checkpoint
configurations and hashes, and stop launching batches at the night-shift deadline.
An unfinished fixed dataset is a checkpoint, not a passed experiment; never
reduce the sample or accuracy target retroactively to claim completion.
Prepare with `python tools/research/continuation_range_bridges.py`.
