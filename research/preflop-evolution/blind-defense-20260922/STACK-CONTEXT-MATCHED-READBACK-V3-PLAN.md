# Independent review of the matched stack comparison

Prepared before the fresh evaluation. This is a read-only review of the
registered comparison, not another experiment or a checkpoint-selection step.

The reader requires successful terminal four-arm training and evaluation v2,
released research ownership, and its passed CPU implementation check. It keeps
the original failed matching check and authenticates the explicit continuation
correction. The old comparison incorrectly required model-dependent parent
hashes to match; this review reconstructs matched chance independently while
requiring every board plan to belong to its own authentic parent model.

## Evidence reviewed

- All four completed 64-cycle trajectories and all 65 immutable model files
  per arm. The played generations remain 0 through 63, with weights 1 through
  64 per player; generation 64 remains excluded. Test outcomes never select
  models or weights.
- All 256 cycle chance receipts. Reconstruct PCG64/SeedSequence draws directly
  from registered seed and generation, validate the sealed own-parent state,
  and authenticate original board bytes through their archive manifests.
  Preserve the original 75 source identities per cycle, replacing only the
  five model-dependent board-plan identities for cross-arm chance comparison.
- All 896 evaluation archives, their recorded byte identities, the complete
  registered physical draw/commit chains, exact all-in labels, eight profile
  crossings, native payoff records, and their committed summaries.
- CPU reference policy replay for the first and last 32-deal batches at each
  of seven depths: 14 batches, four full 64-model banks each. Starts are fixed
  at 0 and 4064. This does not independently replay every postflop policy row.
- All 28 preflop range exports against the full physical holding catalogs and
  full model-bank reference, with independently reconstructed own-action
  ancestry, card compatibility, reach and action masses.
- Independently computed means, uncertainty bounds, tails, all 56 contrasts,
  equal-depth stack-normalized comparisons and the predeclared final criterion.

Training uses depths 20, 40, 100, 200 and 400 bb; 60 and 150 bb remain held out.
Fresh evaluation uses 4096 physical deals per depth and the registered seeds.
Those draws are independently seeded, not guaranteed disjoint boards: chance
collisions are not filtered after the fact.

## Implementation qualification

The CPU check reuses authenticated existing native integration artifacts at
20/60 bb and two-generation routing models. It checks all crossings, legal
actions, reference probabilities and corrupted-input rejection. A synthetic
64-generation policy exercises full preflop range and reach binding. Actual
immutable A-baseline cycle-two evidence checks independent board reconstruction
and archive transport; only its not-yet-published receipt transport is mocked.
This does not qualify actual completed 64-model performance or show a
scientific improvement. That remains subject to the separate actual-bank
resource gate and completed evaluation/readback.

## Resources and boundaries

The final reader uses four CPU Torch threads, requires 28 GB free RAM at
admission and 24 GB while running, yields to active production work, and has a
12-hour bound. It performs no GPU/native solve, new deal draw, fit, journal
mutation, archive retirement, deployment or push. One started reader/check is
not automatically repeated; failures retain their evidence.

This authenticates a restricted fixed-entry heads-up BB-versus-BTN full
continuation comparison. It is not an independent native poker-payoff oracle,
an all-position or multiway test, an equilibrium certificate, or proof of full
preflop accuracy. A separately targeted prediction diagnostic remains distinct.

## Version 3 qualification correction

The first CPU check (v2) stopped at the synthetic range fixture because it
passed an in-memory tuple-containing export directly to a reader which
correctly expects JSON lists from disk. Version 3 serializes and parses that
fixture exactly as the actual export transport does. The failed check and its
source are preserved. Scientific data, reader analysis, selection, tolerances
and comparison criteria are unchanged. The reader changes only its versioned
output, plan and check paths; its evaluation input remains v2.
