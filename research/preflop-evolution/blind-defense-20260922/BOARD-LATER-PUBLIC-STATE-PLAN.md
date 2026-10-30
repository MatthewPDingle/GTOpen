# Prepared next study: explicit public betting inputs

The six-budget comparison favored the existing 512 steps in all four datasets.
Do not spend a full training run on longer fitting. The next test changes the
input representation while leaving targets and fitting duration fixed.

## Completed preparation

- `hu_sampled_public_state_features_v1.rs` exports 450 postflop public decision
  templates from the original native state transitions. Five synthetic stack/pot
  fixtures exercise 1,716 additional templates and independently known half-pot
  bet/call/turn values. Original state and observation code were not changed.
- `board_later_public_state_features_v1.py` adds 12 normalized public inputs to
  the existing 302 columns. Normalization uses public pot/stack bounds, not
  labels, opponent cards or future cards. Preflop additions are zero because
  the current trial overrides preflop neural outputs with separate tables.
- `board_later_public_state_control_v1.json` binds sources, binary, context and
  catalog. All 815,799 retained rows map to the expected native legal menu.
  Identical public histories get identical added values regardless of cards.
  Wrong menus are rejected. Added input weights start at zero; the initial
  function matches the original on the tested public-template representatives.

## Fixed comparison to implement next

Compare the 302/64/64/4 baseline with the 314/64/64/4 public-input candidate on
the same four generation-77 reservoirs, keeping the original input-disjoint
split, training-only target scale, weighted loss, Adam 0.003, original fit seeds,
4,096-row gradient chunks and 512 steps. Keep the original 302 input columns.
Initialize the candidate by copying the original model and zeroing the 12 new
columns. This is a representation change with 768 additional weights, not an
isolated proof that parameter count cannot matter.

Reuse the qualified ordered CUDA gradient. First compare captured versus eager
training for the new representation on a small real-input, multichunk fixture.
Then repeat the original baseline and require its saved weights and validation
loss to reproduce. Register source/control/catalog hashes before the full run.

Primary comparison: equal-dataset mean postflop validation MSE. Report each
dataset and each street, training loss, runtime, memory, and relative changes.
Score validation only. The final-test partition has already been used for the
original baseline; do not reopen it as if it were a new independent test.
Do not alter the feature list, seeds, learning rate or fit budget after looking
at outcomes. No target rescaling, architecture search or new deals in this test.

A mean reduction of at least 1%, with improvement in all four datasets, is a
practical threshold for proposing a separate full-policy training comparison.
It is not a significance test or a guarantee of stronger poker play. Preserve
mixed or negative outcomes and do not promote based on chart appearance.

Use at most 30 minutes, 100 MB retained outputs, 8 GB device allocation, and
two CPU preparation workers. Respect the 800 GB research storage cap and the
user's light-desktop GPU sharing preference. Production and other workloads
retain priority. No process was left running at the end of preparation.

## Next authoritative evidence

The new feature *fit* has not been implemented or qualified yet. The latest
completed experiments are `board-later-fit-holdout-v1-result.json`,
`board-later-fit-early-budget-v1-result.json`, and
`board-later-fit-training-phases-v1-result.json`. The final interpretation is
`BOARD-LATER-FIT-BUDGET-SUMMARY.md`. The broad research goal remains active:
robust preflop ranges across positions/stacks/multiway situations are unproven.
