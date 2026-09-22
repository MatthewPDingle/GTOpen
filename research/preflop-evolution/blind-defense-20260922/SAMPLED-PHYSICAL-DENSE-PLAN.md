# More fresh hands per training update

## Question and fixed candidate

Does eightfold fresh-deal coverage per update improve the physical BB-versus-BTN
prototype? The old 78-iteration bank failed the fresh-deal root-deviation test.
This experiment keeps the same complete incoming support and betting tree.

Train from the uniform initialization for **78 iterations, 512 fresh deals each:
39,936 deals and 79,872 verified updater traversals**. This matches the number of
completed updates in the old pilot, with eight times its fresh deals. Each update
uses eight 64-deal subbatches. All eight and both player passes use the same frozen
model pair; only after all subbatches are ingested are both models refitted.

Keep the same 269-64-64-4 networks, 512 full-gradient Adam steps per fit, 0.003
learning rate, 4,096-row gradient accumulation chunks, target normalization and
262,144-example reservoir capacity per player. The new fitter reuses prepared GPU
inputs; its full 512-step outputs matched the old fitter exactly in the control.
Keep original chance, action, reservoir and fit seeds. This shares a chance-stream
prefix with the old pilot; these are not independent replications. Reservoir
replacement will occur sooner as data increases. This is more data with the same
bounded retention algorithm, not eightfold guaranteed retained examples.

The candidate is the own-history-reach-weighted, equal-iteration average of all
played generations 0 through 77. Generation 78 is unplayed and excluded. No
checkpoint, hand, action or averaging scheme is selected from observed quality.
If fewer than 78 iterations finish, preserve the prefix as incomplete evidence;
do not substitute it as this experiment's candidate or extend automatically.

## Execution and assessment

Hard execution ceiling: **three hours**. Reserve 20 GB host RAM, 3 GB GPU memory
and 40 GB SSD space; cap this run's store at 40 GB. Fail closed on activity in
production preflop, postflop or Reports. Terminate only owned research processes.
No production deployment or preview update is part of this experiment.

After completion, independently replay all chance draws, action seeds, reservoir
insertions and bank/checkpoint progression. Check every native traversal's direct
reference comparison. This readback will not rerun neural optimization.

Then use a separately registered frozen-candidate evaluation: **8,192 response-
training deals (seed 59101), 16,384 test deals (seed 59102)**, minimum 16 class
observations, the same trained root responder and four constant-action controls.
Freeze the responder before drawing test deals. Preserve the original bounded
paired-interval method, five comparisons and one final look. The previous
49101/49102 outcomes are inspected historical evidence, not a fresh test.

A tighter root-deviation result would support progress on this weakness, not
prove a joint equilibrium or agreement with Wizard. A passed execution control,
lower fitting loss, or visually plausible ranges cannot replace strength testing.
No individual hands are patched to match the earlier evaluation.
