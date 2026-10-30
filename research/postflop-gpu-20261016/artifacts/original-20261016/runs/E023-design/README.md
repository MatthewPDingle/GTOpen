# E023 prospective candidate: opponent-only training-up actions

Base: accepted E020. This outside-checkout archive changes only five files: gpu/plan.rs, gpu/mod.rs, gpu/kernels.cu, gpu/continuation_capacity.rs, and game.rs. Root owns activation, compilation, native tests, GPU timing and acceptance. No evaluator, configuration, convergence target, arithmetic tree, down/evaluation dispatch or live server is changed here.

D043's exact appended CUDA is retained byte-for-byte: original up_action remains unchanged, while up_action_opponent preserves +0 accumulation, ascending original child order, CFV addressing,128-thread launches and NA2/3/4/generic specialization. The compiler-only probe found40 registers/0 local bytes/12 theoretical blocks versus66/64/7; it did not establish native exactness or speed. No compiler-resource result is counted as performance acceptance.

## Routing and lifetimes

The original action_nodes/action_spans remain byte-identical for down and evaluation. If any action level has both actors, GpuPlan constructs one extra list that stably partitions each level into actor0 then actor1, with two host span vectors indexing this single new coordinate system. If all levels are uniform, no extra device list is allocated and both span vectors use original aggregate coordinates, including empty/other-actor spans. No original IDs, child arrays, offsets, reach layout, CFV slots or action-menu order change.

At each training-up level, the traverser p uses the unchanged heavy entry and the opposite actor uses the new small entry. Empty spans produce no launch; both nonempty sublaunches are counted/timed in existing profile bucket6. Full/generic/continuation training uses the same ownership split; accepted E015 paired-down reuse behavior is otherwise untouched. There is no E016 cross-iteration reuse, and the down/eval paths remain aggregate.

The extra list and function are constructed before capture, immutable for the GpuSolver lifetime and excluded from continuation workspace swaps. Existing Drop synchronizes before field destruction. New list ownership mirrors other immutable work lists; graphs and all seven mutable workspace buffers keep their existing semantics. Same-level CFV outputs are disjoint and child inputs reside on the next level/terminal cache; stable actor partition therefore introduces no within-level dependency. The existing real-plan test independently retains those CFV aliasing invariants.

Both function loading and optional list construction/upload occur inside initialization and full-cycle timing. The recorded flop census has10 mixed levels, so each paired iteration adds20 launches. The all-uniform river avoids the extra device ID allocation/extra launches but still pays planning, spans and function setup. Complete-cycle benefit is unknown.

## Payload accounting

`training_metadata_bytes()` counts exactly4 times optional ID length, zero for all-uniform plans, with checked multiplication. `staging_bytes()` now explicitly denotes traversal working storage: mutable reach/CFV payload plus these immutable training IDs. Existing constructor admission and frozen exact-budget helpers consume that total once; no workload edits are required. Public game VRAM estimation conservatively adds4 bytes per original action exactly once, covering either isomorphism selection and optional allocation.

Continuation capacity does not use staging_bytes(): its seven mutable workspace arrays are individually counted. Planned metadata adds training_metadata_bytes once, observed metadata adds the actual optional CudaSlice payload once, and retained host payload adds both span capacities. The list is not part of StoredWorkspace/PagedContinuation's seven-buffer swaps. Additional n*4/n*12 terms in symmetry examples/tests refer to distinct stabilizer/public-orbit tables (continuation.rs::build), not this new list. `staging-callers.json` inventories all current callers; diagnostic labels such as staging_mb now represent the documented traversal total, not mutable-only staging.

## Tests to execute after activation

GPU-only library inventory is expected86 passed/4ignored, adding two host tests:
- gpu::plan::tests::training_actor_partition_preserves_stable_coverage_and_coordinates
- gpu::plan::tests::training_actor_metadata_bytes_are_exact_and_checked

The first covers empty, uniform actor0/actor1 and mixed levels, nontrivial node order, exact stable per-actor slices, disjoint coverage and the original-coordinate fallback. The second covers zero, realistic byte count and overflow rejection. The existing river_bounds_match_strength_comparisons test now proves both actual uniform and mixed plan selection, exact partition identity and metadata totals across full/iso plans while retaining same-level/parent-child CFV slot checks.

The existing paired_reach_reuse_matches_full_sweeps_across_lifecycle matrix exercises actual mixed device-list selection, F32/compressed, full/compact, both algorithms, capture/replay, profiling, evaluation, both-actor locks and warm reconstruction. Its test-only legacy_iteration now routes each player's whole original aggregate list through the unchanged heavy kernel, with no small-entry launch, rather than sharing the new upward routing. It retains the optional buffer owner locally and restores metadata afterward. Raw regrets/strategy/reach bits are compared; inactive CFV scratch remains excluded. Profile bucket6 must count both sublaunches.

Conditional broader qualification must explicitly run feature-gated gpu::continuation_capacity::tests::training_actor_list_matches_observed_metadata_for_mixed_and_uniform_plans with preflop-research. It checks actual optional device upload, preserved aggregate IDs, planned versus observed metadata and stored-capacity equality for mixed turn/uniform river. Existing filtered continuation processes do not imply this test ran.

Root's separate prospective primary plan fixes86/4 unit screening then B074/E023R1, E023R2/B075, B076/E023R3 against immutable E020; all18 full non-timing states and138 convergence checks must be exact. The unchanged>=2% aggregate/fixture-regression gates and no extensions remain. Primary qualification alone cannot adopt: original broader state/menu/resume controls, full-F32 checks, GPU/continuation controls including the new capacity test, prospectively fixed wide-turn holdout, fresh original cumulative cohort and independent audits remain required. No primary outcome exists at source freeze.

## Preparation evidence and limits

All five base hashes match the immutable E020 build manifest. Candidate CUDA matches D043. Source-region checks prove graph/evaluation/generic wrapper, training-down/fold/show/chance prefix, sync/locks/Drop and continuation bridge unchanged. git apply --check succeeds without writing checkout files. The source and tests have not been compiled or run. An early draft used the Windows default text decoding; unrelated mod.rs/game.rs em-dash text was restored byte-for-byte before freeze and never activated. Future repairs must preserve this frozen archive additively.
