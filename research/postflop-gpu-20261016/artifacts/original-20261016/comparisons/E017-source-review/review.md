# E017 independent source review

Verdict: **PASS for the frozen source; no actionable defect found.** This is a source review, not runtime correctness or performance qualification. The reviewer performed no builds, GPU work, live-server actions, or production edits.

The candidate is based on accepted E015. It changes only `gpu/mod.rs`, `gpu/plan.rs`, and `gpu/continuation_capacity.rs`. The two-graph E015 lifecycle remains; rejected E016 cross-iteration validity state and third graph are absent. The frozen source, archived candidate copies, archived E015 base copies, protected kernel/arena/store/evaluator files and patch were independently hashed. Exact inputs are recorded in `manifest.json` beside this review.

## Numerical and traversal reasoning

E015 already supplies `down_nh1 = 0` only to the second sweep of an uninterrupted pair. In the unchanged `down_action` kernel, an actor1 block then has `nh_a = 0`. Both its locked loop and ordinary regret-matching loop perform zero iterations. The remaining operations read immutable metadata or form pointers; there are no writes, atomics, cross-block barriers or counters to preserve. This also holds for specialized and generic action arities.

E017 omits only those actor1 action blocks. Every retained actor0 block receives the same node ID, hand counts, buffers and kernel implementation. Its arithmetic and child-action order remain unchanged. The plan's owner-slot mapping gives distinct children their correct actor-side destinations; same-level filtering introduces no dependency across blocks. Chance work still follows action work on the same stream at the same level, and the complete upward traversal remains unchanged.

The first sweep, standalone `sweep`, research continuation, evaluation down/up, and training up retain aggregate action lists. Selection depends on E015's existing paired-call flag, not merely on traverser identity. An isolated player1 continuation therefore cannot accidentally select the filtered list.

## Plan and pointer coordinates

`actor0_down_worklist` preserves the original action list and spans. If any level contains both actors, every filtered span indexes one separate, stable actor0-only vector. Uniform and empty levels in that mixed plan use that same coordinate system. If all levels are uniform, the optional vector is empty: actor0 spans reuse original coordinates, and actor1 spans have zero count. Thus a mixed-plan offset cannot be applied to the aggregate device pointer.

The constructor uploads the optional vector only when nonempty. Uniform plans receive `None` and perform no extra device allocation/upload. The owned optional `CudaSlice` remains in `GpuSolver` for graph capture/replay. It is immutable, is not replaced by lock updates, and is not among the seven continuation workspace buffers. Lock updates still destroy and recreate the captured graphs through the unchanged E015 path. Fresh and resumed constructors reconstruct their own metadata before use.

## Admission and capacity

`GpuPlan::staging_bytes` now explicitly includes optional ID payload in addition to reach and CFV storage. Its sum and byte multiplication are checked. This semantic expansion keeps existing exact-budget callers consistent without changing their harnesses. Constructor admission uses checked arena-byte sums and includes the resulting traversal total once for both full and compact choices.

Continuation capacity independently includes the optional vector in planned immutable device metadata and actual observed CUDA-slice metadata. Retained host accounting includes the additional spans' capacity. Its seven mutable workspace buffers are still sized directly from reach/CFV/arena dimensions, so the staging-method expansion is not double-counted there. Temporary planning vectors remain within the capacity report's existing documented exclusions.

The optional upload can add initialization cost and allocation pressure on mixed plans; reduced CTA counts do not establish a complete-cycle gain. Uniform plans still perform additional host planning and retain span metadata despite having no extra device buffer. These costs belong inside normal constructor/full-cycle measurements.

## Meaningful runtime obligations

The following focused library tests are present in the frozen source. They must actually execute successfully; this review does not substitute for them.

- `gpu::plan::tests::actor0_down_lists_preserve_order_membership_and_uniform_coordinates`: nonmonotonic IDs, stable order, mixed/uniform pointer coordinates, actor1-only and empty levels, all-actor0/all-actor1 cases.
- `gpu::plan::tests::river_bounds_match_strength_comparisons`: actual flop/turn/river plans with and without isomorphism; filtered membership and exact additional staging bytes alongside existing slot invariants.
- `gpu::tests::paired_reach_reuse_matches_full_sweeps_across_lifecycle`: the existing eight storage/algorithm/compact cases now assert a real mixed list, compare complete raw learning/reach bits against full sweeps, and exercise eager execution, capture/replay, evaluation, profiling, both lock owners, graph recreation and warm reconstruction. Selected launch counts are checked.
- `gpu::tests::uniform_actor_levels_reuse_original_list_across_lifecycle`: F32/DCFR and compressed/CFR+ river cases assert absence of the optional device list, exact-budget admission and one-byte-short rejection, then exact lifecycle comparisons including locks and warm construction.
- `gpu::tests::paired_reach_reuse_preserves_raw_player1_and_standalone_refresh`: unchanged independent full-down dispatch and poisoned-reach checks protect standalone/continuation behavior.
- `gpu::tests::shared_evaluation_matches_independent_sweeps` and `gpu::tests::tight_f32_budget_preserves_warm_and_queried_inactive_state`: retain existing evaluation, admission and inactive-state controls.
- With `preflop-research`, `gpu::continuation_capacity::tests::optional_down_list_matches_observed_metadata_for_mixed_and_uniform_plans`: actual CUDA payload equals planned metadata for both paths. This is necessary because source accounting changed.

If performance qualifies, retain the frozen saved-state, action-menu and resume controls, GPU/CPU accuracy suite and exact benchmark fingerprints/iterations/exploitability bits required by the program. The existing `continuation_paging` integration test (`paging_preserves_resident_trajectories_and_rejects_invalid_inputs`, 160 exact sweeps) is a bounded check of immutable per-game metadata remaining valid across shared mutable workspace swaps. The existing stored-device test can additionally check its 720 passes; it does not force SSD spill and is not a user-save compatibility test. No full preflop research program is required.

## Limits and disposition

The source assertions ensure that a mistaken fixture assumption fails visibly instead of silently missing mixed or uniform coverage. Their runtime validity remains unverified by this reviewer. No fault-injected CUDA failure was tested. Save serialization, storage encoders, kernels and the frozen evaluator are unchanged, but actual save/resume compatibility still depends on the established runtime controls.

Do not infer speedup from the static CTA census or component profile. Qualification must use the unchanged complete-cycle score and fixture-regression guard against immutable accepted E015, with initialization/upload costs included. Preserve all attempts and report any fixture regression. This source PASS authorizes no performance, statistical-significance or deployment claim.
