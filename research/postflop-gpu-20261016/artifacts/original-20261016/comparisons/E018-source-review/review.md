# E018 independent frozen-source review

**PASS for source; no actionable finding.** The review covers the four frozen implementation files and their in-file tests. No build, GPU execution, live-server action or production edit was performed by this reviewer. Runtime exactness and performance qualification remain outstanding.

## Scope and numerical contract

The base is accepted E015. E016 cross-iteration validity/third-graph changes and E017 actor-filtered downward lists are absent. `kernels.cu` exactly matches the D031 probed candidate, SHA-256 `de0c0b34dbe89005c7a175618c5ece3f187686089f1775a97d781967c8c02ec4`.

The CUDA change replaces four training-up expressions `cfv_slot[children[cs+a]]` with `child_cfv_slots[cs+a]`, plus the corresponding parameter/forwarding names. These four reads cover the locked traverser, ordinary traverser child values, the generic greater-than-eight-action reload, and the opponent accumulation. Action order, floating expressions, arity dispatch, discounts, locks, hand dimensions and output parent slot remain unchanged. Evaluation, downward kernels and upward chance work retain the original child-node arrays.

Integer-address equivalence is established by the plan mapping. It does not by itself prove compiled floating-point equivalence: changed addressing can alter compiler scheduling/resource decisions. D031 measured compiler resources only. Exact runtime comparisons to immutable E015 remain necessary.

## Sentinel-safe mapping

`action_child_cfv_slots` creates a full `tree.children.len()` table initialized to `SENTINEL`, then fills only edge spans of `action_nodes` selected by the existing representative-branch traversal. It never attempts a whole-vector dereference through chance-node sentinels. Each consumed action span is checked, each child indexes the existing CFV map safely, and its physical slot must be non-sentinel and below `cfv_blocks` before upload.

Keeping original child-array coordinates means `node_children_start` and action indices require no changes. Every consumed value equals the original nested lookup. Chance entries and inactive action edges remain sentinel and are not read by training-up action work. Physical CFV slot reuse across levels is intentional; the mapping preserves those existing aliases rather than imposing incorrect global uniqueness. Switching to full action arenas changes learning-state offsets only, leaving these physical CFV addresses valid.

## Wiring, ownership and lifecycle

The only training `f_up_action` launch receives `d_child_cfv_slots`. The separate evaluation launch still receives `d_children`; all down/chance paths and their arguments remain original. The new table is uploaded once using the existing owned metadata-upload helper and remains an immutable `GpuSolver` allocation. It is not one of the seven swapped continuation workspace buffers.

The two captured training graphs use this stable per-solver pointer. Lock changes retain the same plan and use the existing graph-destruction/recapture path. Fresh or warm constructors rebuild their own table. Standalone/research continuation changes reaches or mutable workspace storage but continues to use its owning solver's immutable physical-slot plan. No new cross-iteration validity state or graph dispatch condition is introduced.

## Memory, admission and frozen inputs

The full table's exact additional device payload is `4 * tree.children.len()` bytes, including sentinel entries. `training_metadata_bytes()` reports this amount, and `staging_bytes()` now explicitly includes it with reach/CFV storage using checked arithmetic. Consequently the existing exact-budget helpers account for the new allocation without changing their frozen source inputs. Constructor full/compact admission also uses checked arena sums and includes that traversal total once.

Continuation planning and actual observed CUDA payloads both include the new immutable array exactly once. The seven mutable workspace sizes are still calculated directly from their own shapes, so there is no staging-method double count. The host table is temporary constructor/plan storage; it is not retained by `GpuSolver` or `StoragePlan`. Existing capacity-report exclusions for temporary plans therefore continue to apply.

The extra host fill, CUDA allocation/upload, and changed runtime NVRTC/JIT work belong inside constructor/complete-cycle timing. This source review does not assume they are recovered by fewer metadata loads. The immutable original child array is still required by down/evaluation, so this is additional storage rather than a replacement allocation.

## Required meaningful runtime checks

- `gpu::plan::tests::child_mapping_handles_generic_menus_and_rejects_invalid_physical_slots`: asserts an actual greater-than-eight-action node, exact mapping, empty-action sentinel table, and rejection of sentinel/out-of-range consumed physical slots.
- `gpu::plan::tests::river_bounds_match_strength_comparisons`: now checks actual flop/turn/river plans with and without isomorphism, verifies every consumed original address, requires real chance sentinels and inactive action coverage, and proves full-arena conversion leaves the table unchanged.
- Existing paired lifecycle and standalone-refresh tests must pass. Their constructor helper now downloads and compares the entire device mapping to the plan for full and compact cases, while retaining raw-state, graph, evaluation, profiling, lock and warm-reconstruction checks.
- Existing shared-evaluation and tight-F32-budget tests must pass, including one-byte-short admission rejection and queried inactive-state restoration.
- With `preflop-research`, `gpu::continuation_capacity::tests::child_mapping_matches_observed_metadata_for_turn_and_river` must execute. It checks uploaded table contents, actual versus planned device payload and exact single inclusion of the added bytes.

The paired lifecycle reference calls the same changed training kernel as the candidate. It validates lifecycle/dispatch consistency, but is not an independent oracle for original training-up arithmetic. Before accepting E018, compare the preserved E015 and E018 native binaries on the frozen primary and saved-state/action-menu/resume controls. The frozen action-menu control already contains a ten-bet-size river menu with sufficient stack to exercise greater-than-eight actions, both DCFR/CFR+, and locking. Keep its workload unchanged. Full-state fingerprints, exploitability bits and stopping iterations must remain exact.

If performance qualifies, bounded existing continuation paging/storage controls can additionally check immutable metadata across borrowed workspaces; no full preflop research program is needed. A source PASS alone does not establish user-save compatibility, deployment readiness, universal numerical equivalence or a performance gain.

## Disposition

Proceed through the registered serialized build/correctness/three-pair complete-cycle process with the source frozen. Preserve failures. Require the unchanged aggregate and fixture-regression gates, including all new initialization costs. Do not use static PTX counts, theoretical residency or a component-only speedup as the acceptance score. Exact reviewed input hashes are recorded in the adjacent manifest.
