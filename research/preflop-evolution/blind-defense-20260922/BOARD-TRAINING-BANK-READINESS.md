# Board-root policy bank: CPU layout checked, CUDA qualification pending

The next matched study needs to evaluate the complete played policy history,
including the new board-root decisions. These helpers prepare that path without
changing the running evaluation, production server, training rules or samples.

`board_training_bank_layout_v1.py` validates every typed model and its generation,
packs the saved float32 network parameters into float64 arrays, and composes the
weighted preflop tables with the exact BTN response and board-root overrides.
Overrides must be applied before calculating the probability of a player's
earlier actions. Otherwise the final average can describe a different policy.

`board_training_gpu_bank_v1.py` passes that layout to the existing shared-query
CUDA evaluator. It is an unqualified candidate: the new adapter has not run on
CUDA. The existing numerical evaluator's prior tests do not qualify this new
combination automatically.

`board_completed_bank_v1.py` is a prepared loader for the eventual complete
study. It requires both arms' registered 78-generation training result and
independent complete readback, verifies the selected arm's progress and model
chain, and excludes the unplayed final model. The intended average is played
generations 0 through 77 with weights 1 through 78, weighted by each player's
own earlier action probabilities. No completed board-root bank exists yet;
the loader has not been qualified on one.

## Completed CPU check

`board-training-bank-layout-control-v2-result.json` passed in 17.906 seconds.
The fixture contains 29,031 native observations and two synthetic saved models.
Three cases cover the saved fixture, varied float32 network parameters, and a
later policy with zero probability of reaching many histories. Actor-specific
weights also differ to check that each observation uses the correct player.

For all three cases, packed-layout policies, averaged policies and own-action
reach matched the existing scalar/CPU reference exactly (maximum error 0).
There were 104 table overrides per case. The later model had zero reach on
7,380, 19,971 and 27,942 rows respectively and correctly contributed no weight
there. The complete average had positive reach everywhere because a valid bank
includes the positive-weight uniform initial policy.

Eight invalid inputs were rejected: a nonuniform initial model, reordered
models, incomplete history, an unplayed model, nonpositive weights, a changed
board seed, root ancestry and a different game context.

This check used no GPU or model fitting. It validates representation and
averaging on these fixtures; it is not evidence of stronger poker play, faster
GPU execution or validity of a future complete study. The feature encoder,
model validator and table implementations are shared with the reference.

## Preserved failed fixture

Version 1's source and registration are retained. That attempt stopped during
model validation with `ValueError('Initial model must be uniform')`: the test
had incorrectly randomized generation zero. It produced no passing result.
Version 2 varies only the later model and adds an explicit rejection check for
a nonuniform initial model. The production model validator and adapter were
not weakened or changed to make the fixture pass. This paragraph is a
retrospective failure record, not an automatically captured runtime result.

## Remaining qualification

After the queued genuine GPU training/restart control and its independent
readback finish, compare this adapter against the CPU reference on those saved
played models and native queries, using model chunks 1, 2 and 8. Check both
probabilities and own-action reach at the existing 1e-10 tolerance. Include the
root overrides and exact BTN responses in that comparison. Wait for spare GPU
capacity and the research locks; do not compete with an active user workload.

A two-model control will not qualify loading and evaluating the eventual
78-model bank. After admitted full training and complete readback, check those
actual banks before the prospectively specified fresh 65,536-deal evaluation.
The storage admission, fixed study endpoint and eight planned contrasts remain
unchanged. No new GPU job, full training run or deployment was launched here.
