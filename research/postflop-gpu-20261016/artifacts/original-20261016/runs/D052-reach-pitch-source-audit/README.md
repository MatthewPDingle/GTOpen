# D052: physical reach-row pitch source audit

**GO for source feasibility of one bounded E027 experiment, if separately authorized. No speedup or >=2% headroom is established.** Accepted E020 is the base; all 162 pinned source files were verified unchanged. This audit executed no compiler, solver, GPU job or live action and prepared no candidate.

Use `pitch[p] = ceil(nh[p]/8)*8` floats only for physical reach rows. Keep logical hand counts, root slot zero, owner/slot maps, all floating operations and order, learning arenas, CFV stride, launch dimensions and graph semantics unchanged. Five production files suffice: `gpu/plan.rs`, `gpu/mod.rs`, `gpu/kernels.cu`, `game.rs`, `gpu/continuation_capacity.rs`. The kernel ABI can stay unchanged by deriving pitch from each existing logical count only at reach row addresses. There is no need for element-offset maps, host reach packing or a save-format change.

NVIDIA documents 32-byte coalescing units for compute capability >=6; a full warp of adjacent floats spans four aligned units or five if misaligned. That supports eight floats as the smallest row multiple for this mechanism, rather than E025's 32-float CFV proposal. Driver/runtime allocation bases are sufficiently aligned. Caches can amortize overfetch; this is not a DRAM-byte or speed prediction. [Best Practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#coalesced-access-to-global-memory), [Programming Guide12.9.1](https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-programming-guide/index.html).

| Archived fixed fixture | Logical hands | Proposed pitches | Extra floats per row |
|---|---|---|---|
| Rainbow |257,319|264,320|7,1|
| Two-tone |258,320|264,320|6,0|
| River |233,280|240,280|7,0|

These counts come from the pinned D027 structural census, not new execution. The full-range turn holdout's1128 hands are already divisible by8. Exact additional device bytes are `4*sum(reach_blocks[p]*(pitch[p]-nh[p]))`; no preserved total reach-block census was found, so no total is asserted. The existing two allocations, memset work, retained workspaces and cache footprint grow. Near-budget admission or full/compact selection may change, especially for narrow ranges. The number of allocations and root weight upload bytes need not change.

## Complete address and lifecycle scope

- `kernels.cu:55,65,91`: down-action parent and locked/unlocked child reach rows. `:131-136`: down-chance source/destination rows. `:158-159,225,368`: fold/show opponent rows and action traverser row. Only row multiplication changes; hand loops, action/regret offsets and shared arrays remain logical. `copy_root:18-23` is slot zero and unchanged. Up-chance and up-action-eval have no reach-row address.
- `plan.rs:495-498`, `mod.rs:365-368`, `game.rs:419`, `continuation_capacity.rs:67`: central staging/admission, actual two reach lengths, public conservative estimate and stored workspace component must agree. Count mutable reach bytes once. Existing capacity metadata checks do not by themselves compare workspace component estimates with actual reach lengths.
- `mod.rs:545-616,763-846`: both evaluation and training share the modified down kernels. The accepted E015 second paired sweep passes `down_nh1=0`; derived pitch0 is safe only while those hand loops remain empty. Upward consumers use true counts. Do not substitute padded pitch for any logical loop bound.
- `mod.rs:184-194,520-533,997-1038`: continuation root weights, returned/evaluation CFVs and CPU learning-store synchronization remain logical and unchanged. Reach is transient device scratch, not a persisted arena.
- `continuation_paging.rs:69-128` and `continuation_storage.rs:164-172,301-314`: actual buffer lengths drive workspace checks/swaps and are drained before returning. Four learning arrays are transferred/parked, not reach rows. Keep pitch immutable per solver; borrowed workspace capacity may exceed that solver's requirement without changing its addressing.

The report contains the complete line-addressed audit and hashes. A separate menu_change_review read-only lifecycle audit found no blocker and confirmed these caveats.

## Minimum useful verification and decision boundary

Extend existing plan/raw lifecycle assertions rather than inventing a large new harness: multiple8 geometry, logical-row separation, unchanged slot/root ownership, exact byte delta and padding boundaries; preserve locks, captured/eager/profiled/evaluation, warm F32/compressed and E015 reuse behavior. Candidate-shared whole-buffer comparisons alone are insufficient as an independent old/new oracle: padded physical vectors differ in length. A small logical-row comparison of accepted/candidate raw reach before evaluation/quantization, plus padding guards, is required before adoption.

After bounded units, run the unchanged fixed three-pair primary first, requiring all18 states/138 checks exact, >=2% complete-cycle improvement and the existing fixture regression guard. No arbitrary non-worse register/occupancy gate, variant rescue or extension is proposed. Only a qualifying primary justifies the existing original/F32/state/menu/resume/continuation controls, unchanged holdout and cumulative qualification. Include actual padded workspace versus planned component equality, budget boundary and changing-board swap checks in that conditional work.

No direct reach-pitch duplicate was found in the scoped ledger/design/source search; this is not an exhaustive historical assertion. E025's CFV-only padding lost0.9378% in its fixed cohort. D049's integer pointer change increased registers40->48 and lost its resource prerequisite. E026's width change was5.5832% slower. None is a mathematical blocker or a rescue avenue; all caution against inferring complete-cycle benefit from address/layout arguments. Accepted E020 cache and E015 paired reuse remain intact. No performance result, acceptance or deployment follows this audit.
