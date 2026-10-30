# Board estimator integration: model transport and native targets checked

The new estimator now has a distinct saved-model/checkpoint format, inference
reader and native board-target provider. These are research components only.
A complete training update with network fitting has not yet been qualified.
The existing stratified study and its fresh-data evaluation are unchanged.

## Model, checkpoint and policy control

`board_training_checkpoint_v1.py` and `board_training_policy_v1.py` preserve
the weighted physical postflop reservoirs and sampled preflop tables, then
apply the board-root and exact BTN overrides. The saved state includes the
board configuration and completed draws, physical sampler, action RNG,
reservoir RNGs, both networks and ordered played-policy history.

The v2 CPU control passed on 29,031 native observations with synthetic target
values and network parameters. It tested two generation transitions, three
checkpoints, table/override ordering, independently reconstructed own-action
reach averaging and exclusion of the unplayed final model. Maximum policy or
average discrepancy was zero. Physical sampling, action sampling, reservoir
replacement and subsequent board planning agreed after restoration. Seven
negative admission checks passed. Unpublished interrupted work did not change
the last immutable checkpoint. Runtime was 7.922 seconds, CPU only.

The first control attempt stopped at synthetic reservoir insertion because
the fixture supplied only the legal-action slots; storage correctly requires
four slots with illegal actions padded by zero. Its source, registration and
failure record are retained. V2 fixes the fixture padding. The checkpoint and
inference implementation were unchanged between attempts.

## Actual native board targets

`board_training_targets_v1.py` reads the new model explicitly, reconstructs
all physical preflop policies, verifies the original BB class population and
builds exact preflop terms separately from sampled public-board contributions.
It keeps the original pair and class denominators and binds each draw to its
board, model, native tree, policy recipe and value matrix.

The target control used the recovered synthetic-policy fixture and its actual
next four planned public boards. Native trees retained complete legal private
support. Four CPU workers ran while the separate GPU evaluation continued.
The complete control took 26.515 seconds; workers took 23.61, 15.36, 16.53 and
15.34 seconds. The first worker also performed an independent dense forward
cashflow check, which explains its additional work.

For that first board, the maximum difference from the explicit hand-pair
cashflow calculation was 7.461e-14 bb. All four boards then fed a real root
accumulator update across 169 classes; its maximum difference from scalar
reconstruction was 5.684e-14. Detached-model evidence was rejected without
mutating the root, and recovery preserved its next chance plan. No network
was fitted and no learned-range claim follows from this synthetic-policy test.

## Remaining integration

Wire the provider into a complete generation: freeze the played model, start
bounded CPU board work, process the existing stratified physical targets, fit
both networks, update exact BTN responses and publish only the complete
checkpoint. Recovery must start from the preceding complete boundary if any
part fails. Then qualify native target readback and CPU/GPU policy agreement
for the new format before registering a matched training experiment.

Use measured phase times to choose worker counts and board batches. The
current evidence supports concurrent CPU work but does not justify occupying
the GPU with another experiment while the main evaluation is running.

Evidence: board-training-checkpoint-control-v1-failure.json,
board-training-checkpoint-control-v2-{registration,result}.json and
board-training-targets-control-v1-{registration,result}.json. Raw small control
artifacts remain in their registered S:/GTOpen-research directories. Native
80 MiB tree transports were hashed in memory rather than repeatedly retained.
