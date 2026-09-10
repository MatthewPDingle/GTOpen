# Per-traverser compact slot feasibility

No broad layout rewrite proposed yet. The required maximum per-seat fraction is not present in the existing benchmark output, and I have not run a planning executable, compiler, or GPU job to obtain it. `instrumentation.patch` is an opt-in source-only proposal to obtain the exact counts already computed by `EquityCachePlan`. Patch applicability passed against the current isolated source. No worktree/main source edits occurred.

## Exact counts without new analysis machinery

`EquityCachePlan::build_for` already constructs:

- `blocks.len()`: union slot count U.
- `spans[p].1` for p in0..n: exact statically needed slot count Kp for each traverser.
- `spans[n]`: the union work span used by the generic plan machinery.

The multiway terminal path currently consumes `spans[p]` even for ungated average evaluation; it does not consume the union span as one simultaneous workload. Therefore one scratch allocation of capacity `K = max(Kp)` suffices if terminal references are remapped correctly. Fixed/static seats do not justify omitting their Kp from the maximum: evaluation still visits every seat.

Set `PREFLOP_MW_SLOT_STATS=1` when running the frozen planning harness or next diagnostic benchmark. A single uniquely prefixed JSON line reports U, every Kp, K/U, and projected net memory savings for batch1/7/32 with or without normalization. The same instrumentation works through `vram_estimate_mb(&solver)`, so a planning-only call need not construct a CUDA context. Because that method and the constructor both build plans, callers may produce duplicate identical lines. Unset the variable for measured timing runs.

The calculation includes extra mapping storage and preserves existing union metadata/active flags. It reports both immutable per-seat mappings and a reusable dynamically rebuilt mapping; negative net savings are reported explicitly. `gpu-instrumented.rs` is the full proposed source and `build_instrumentation.py` reproduces the patch.

## Minimal viable layout if counts justify it

Start with an immutable map `compact[p * U + global_slot] -> local_slot`, initialized to a sentinel for absent slots. For each p, enumerate its existing work span in its current order, assigning local slots0..Kp. This costs n*U*4 bytes: at U760,578 and eight seats, about24.3MB.

Retain all existing union maps, work lists, source blocks, and active flags. Changes would be narrowly scoped:

1. Normalization and CDF kernels still retrieve global slot = `work[start+blockIdx.x]` for the source block and active guard. Store normalized/CDF data at compact slot = `blockIdx.x` instead of the global slot.
2. In terminal preparation of `opponent_slots`, resolve the source to its existing global slot and then the traverser's immutable compact slot. Do this once per opponent in the existing metadata setup, not in the hand/particle inner loop.
3. Allocate normalized/CDF scratch using K rather than U. Pass the original U as map stride; include mapping bytes before selecting batch size or the optional-normalization fallback.
4. All other arithmetic and evaluation ordering stay unchanged. In particular, preserve ascending opponent-seat order; sorting opponents by compact slot for locality would change float product order.

The matrix is immutable, so CUDA graphs can retain it safely. A later, lower-memory variant could rebuild one U-entry global-to-local map on device from the active work span before each traverser. That adds only U*4 bytes but needs a reset/scatter policy and more stale-map tests. It should be a separate candidate, not mixed into the first mapping change.

## Acceptance decision

Current normalized32-particle scratch uses U*(170*32*4 +169*4) bytes. The immutable-map candidate uses K times the same per-slot cost, plus n*U*4 mapping bytes. Compute the actual net saving before implementing.

If K is almost U, there may be little benefit despite smaller average per-seat counts; peak capacity determines allocation. Favor implementation if measured net savings are material (for example at least10% of scratch or roughly1GB on the large fixture). Lower VRAM alone is not guaranteed to improve throughput when both layouts already fit32 particles.

Also inspect the batch1 projection. The mapping allocation can increase minimum VRAM if K/U is too high: for eight seats the immutable matrix needs roughly4.7% fewer CDF slots merely to break even at one particle without normalization. Preserve an original union-layout fallback if compaction would worsen the minimum fit boundary.

## Proposed correctness checks for an eventual implementation

- Pure planner tests for synthetic overlapping/disjoint per-seat slot sets: every work entry maps bijectively to0..Kp, absent slots stay sentinel, K excludes the trailing union span, and projected byte budgets are correct.
- For actual3/6/8/9-seat trees, inspect every coupled terminal: for each live traverser and each live opponent, the resolved compact slot must be in that traverser's span and map back to the same reach source. Folded opponents remain in probability calculations but do not need CDF slots.
- Existing all169-hand CPU/GPU comparisons and exact before/after arena/gap/EV hashes with the same particle batch size. Moving storage alone should not change results.
- Poison compact CDF/normalized scratch between traversers, especially switching from large Kp to small Kp and back; exercise gated and ungated evaluation, zero-own/zero-opponent cases, and graph replay.
- Memory-boundary tests at one particle and full32 particles, including optional-normalization fallback. Account for the new map in constructor and public estimates.
- If freed memory changes particle batch size, first validate the same-batch layout change separately; batch-dependent summation differences must not be misattributed to the map.
