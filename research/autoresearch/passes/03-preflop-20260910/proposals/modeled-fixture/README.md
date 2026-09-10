# Modeled-seat benchmark fixture proposal

Use `saves/preflop/Measured action sizing 20260909-160232.gtop` as the source.
It is the actual six-seat 100bb user game with UTG/HJ/CO/SB/BB Ignition NL10
Pool profiles and BTN on Solver. Every model uses the measured action-size
distributions and retains `adaptive_from=0.25`. This covers host policy
materialization, forced CUDA policies, adaptive learning, several legal raise
sizes and coupled multiway leaves. It does not test contextual-v1 inference:
this save has no `contextual_reraise` version enabled.

`recommendation.json` records the exact header, policy, config and small cache
hashes. The source has two 311,892,711-float arenas and 2,509,030,035 total bytes.
Only its header and arena length words were read, using a seek across the first
arena. No original saves, live servers or active worktree files were modified.
Obtain the full source-file hash before adopting a frozen benchmark input,
outside timed hardware experiments.

## Proposed native helper

`modeled_fixture.rs` is a standalone solver example proposal. It has been
syntax-checked/formatted by rustfmt; it has NOT been compiled or run. The parent
can copy it into the isolated lab's examples, build it there and invoke:

```text
modeled_fixture SOURCE EQ_CACHE OUTPUT_ROOT OUTPUT MODE
```

Use absolute paths. OUTPUT_ROOT and OUTPUT's parent must already exist.
OUTPUT must be new and beneath OUTPUT_ROOT; an existing output or `.tmp` is
refused. It creates a tiny private `OUTPUT.equity.bin` cache beside the native
save, avoiding the loader's potential writes to the original equity cache.
Run from the pinned lab CWD and set REALIZATION_FIT to the pinned fit.

Modes:

| Mode | Initial state | Payoff model |
|---|---|---|
| fresh-coupled | Rebuild exact config and install existing typed profiles; zero arenas | coupled_deck_v1 |
| fresh-legacy | Same exact config/profiles and zero arenas | legacy_product |
| resume | Native load/save, existing iteration and arenas | Source model unchanged |
| freeze-non-btn | Native load, retain all profile definitions, freeze other seats through set_table_keep | Source model unchanged |

The source for `freeze-non-btn` must already be solved. Native freezing snapshots
forced policy nodes where needed and pins previously adaptive branches to their
existing averages. BTN learning state is retained. This is a derived frozen
control, not the same starting state as its unfrozen source. To create a coupled
frozen control, first solve and save the fresh coupled fixture, then freeze that
save. Never relabel existing learned legacy arenas as coupled.

Fresh modes refuse frozen source seats, hero state or point locks rather than
silently discarding them. All modes require the existing five measured opponents
and unmodeled BTN. Profiles are loaded through the native SeatProfile schema,
never regenerated from statistics or reindexed by a Python converter. The helper
checks typed profiles and configuration before and after native save.

Keep all `.gtop` outputs in a gitignored research directory. Commit only this
proposal and compact manifests/results. First compare fixed initial-state runs
on these same files; use a separately logged save for any converged/frozen run.

## Memory planning caveat

The source tree is 1,845,520 nodes / 861,384 decisions. The existing base-memory
formula is bounded by 4,693.46–5,275.75 MB using leaf-count and node-count bounds
for value blocks. This excludes topology-dependent coupled CDF slots, optional
equity cache, normalization and maps. A native save contains configuration and
arenas, not the rebuilt topology, so exact baseline/compact CDF capacities cannot
be obtained from its header. A host-only build with PREFLOP_MW_SLOT_STATS and
vram_estimate_mb can obtain these before any CUDA launch.

The current constructor also omits materialized `forced.len()*4` from its budget
calculation. This source could add up to 1,247.57 MB of forced policies (actual
payload is smaller because BTN and adaptive nodes are not forced). Fix that
accounting before the modeled GPU experiment; do not merely rely on headroom.

At budget 23,000 MB, record actual baseline and candidate batch width, normalized
cache state, compact/union slots, optional equity-cache state and forced bytes.
Batch width is chosen after fixed allocations and may differ across revisions.
Different batching can legitimately change floating-point accumulation order;
use numerical arena/gap/EV comparisons and time-to-accuracy checks where full
fingerprint identity is no longer the appropriate gate.
