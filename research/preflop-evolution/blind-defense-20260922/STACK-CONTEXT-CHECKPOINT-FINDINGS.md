# Complete multi-context save/resume contract implemented

`stack_context_training_checkpoint_v1.py` gives each fitting context its own
physical-deal sampler, action RNG, two weighted visit reservoirs, BB root
accumulator and exact BTN-response accumulator. The shared model and all local
states must agree on the completed cycle number.

Configuration binds the registry, input representation, objective units,
explicit context weights and order, source identities, fitter/initialization,
optimizer lifecycle, local sampling budgets and random seeds, target method,
all-in cache identities and root configuration. Existing single-context
checkpoints are not silently migrated.

A completed cycle requires every context to name the same frozen played model.
It constructs both shared networks' complete policy and checks all local state
before publishing a complete checkpoint. The caller's previous state is not
mutated. The final newly fitted but unplayed model remains outside the played
model bank. Immutable orphan objects from interrupted writes are not by
themselves selected resume checkpoints.

Four CPU integration tests passed in10.034 seconds:

- Both input formats save and restore initial and completed states, then replay
  identical subsequent physical deals, action draws and reservoir replacement
  draws beyond capacity.
- Interruptions before model publication or before checkpoint publication leave
  the previous checkpoint usable. Completing from the restored state reproduces
  the same model and checkpoint references as uninterrupted publication.
- Missing contexts, mixed frozen-model identities, stale samplers and swapped
  local states are rejected.
- Changed settings/source identities/context weights, inclusion of the final
  unplayed model, and held-out fitting state are rejected.

These tests use real native context/catalog fixtures with synthetic accumulator
and target updates. They test serialization and transaction boundaries, not a
real complete training cycle. Worker integration must still establish native
target provenance against the actual frozen model; the recorded identity alone
does not prove how a target was calculated. Whole-run progress-marker selection
and recovery also remain the responsibility of the forthcoming runner.

Next connect the native query, board and posterior64 workers to the full shared
policy, then qualify an actual full cycle and restart. The current board-target
and river-worker implementations still assume the old302-input single-context
model. Their trained-target logic must be preserved, not replaced with uniform
opponents or a terminal Fold/Call surrogate. No learned-range accuracy claimed.
