# Bounded physical-poker training storage

The physical bridge's advantage visits now feed fixed-capacity per-player
reservoirs. The registered storage control passed. This is a prerequisite for
physical neural self-play; it neither trains a strategy nor establishes better
calling ranges.

## What is retained

Each retained visit contains its 36 active visible-feature indices, four signed
advantage values, legal-action count, canonical observation key and iteration.
The key and iteration are audit metadata, not neural input. Repeated visits to
the same observation remain separate training examples. Positive-tag records
are advantage samples; negative-tag opponent-policy records are validated but
not inserted into the advantage buffers. Average strategy still requires the
separate bank of actually played networks.

The sampler is Algorithm R with an independent seeded generator per player.
After capacity is reached, each new visit has the appropriate chance to replace
a retained visit. Every visit has equal inclusion probability, matching ordinary
CFR's equal iteration weighting. This replaces the finite control's priority
reservoir implementation with the same uniform sampling law, not the same random
trajectory. Chance/opponent reach is already represented by external sampling;
the storage layer applies no additional importance or reach multiplier.

The allocation is **129 bytes per slot**: 72 feature-index bytes, 32 target bytes,
16 key bytes, 8 iteration bytes and one arity byte. At 262,144 slots that is
33,816,576 bytes per player, or 67,633,152 bytes for both buffers. These figures
exclude query batches, Python/runtime overhead, models and fitting workspaces.
The buffer contains no growing global information-set dictionary. Dense training
features should be materialized only within a bounded fitting operation.

## Verified behavior

The source fixture supplies 444 BB and 32 BTN advantage visits. Seven repeated
ingestions saw 3,108 and 224 visits while retaining exactly 17 per player, with
unchanged 2,193-byte payload allocations. The small capacity deliberately forces
replacement; it is a test fixture, not a proposed training budget.

- Retained slots, keys, visible features, legal menus and signed targets match
  an independent Algorithm-R oracle.
- Whole-batch and 37-record chunks give identical arrays, counters and RNG state.
- Checkpoint reload followed by six more ingestions exactly matches uninterrupted
  storage, including the random state and iteration metadata.
- A buffer large enough for three fixture copies preserves all duplicate visits.
- Exhausting all 60 equally likely draw sequences for five visits and capacity
  two yields all ten possible retained subsets exactly six times each.
- Six invalid transports and one stale-context checkpoint are rejected. Invalid
  transports, including errors at the final record, leave both buffers unchanged.

The registered control took 0.84 seconds on CPU, uses no GPU and changes no
production state. Seven input hashes are frozen. Checkpoint hashes are recorded;
the regenerable checkpoint files live under `target/research-sampled/`.

## Remaining integration

Storage checks do not qualify the actual neural fitting process, sampling
coverage, model-bank averaging or poker strength. Complete training resume also
requires the deal/action RNGs, played model bank and iteration state; reservoir
checkpointing alone is not a full training checkpoint. The current batch bridge
checks context and batch identity before generating updates; the controller must
keep each query/update pair together and record their hashes.

Next connect these bounded retained examples to the physical fitter, execute the
combined CUDA bridge when the GPU comparison releases the device, and run a
bounded physical self-play pilot after reviewing the strategic-method gates.
Independent evaluation and fresh boards remain necessary before preview changes.

Evidence prefix: `sampled-physical-reservoir-v1`.
