# D030: precomputed action-child CFV addressing

Status: source-only hypothesis, not an implemented candidate or a performance result. Recommend a compiler/resource diagnostic first; evidence does not establish a likely 2% complete-cycle gain. No build, CUDA call, timing or production edit was performed.

The immutable accepted source is commit `e868cfbb125002216f25046af2d88b22a697b2fd` (E015). Source copies and hashes are adjacent. The evolving E017 checkout was not used for this design.

## Why investigate this one

D029 independently verified all nine exact final states from the preserved E015 executable. In every flop profile, synchronized eager host ranks are up_action > up_show > down_action. Median up_action spans are 8.8736ms rainbow and 5.0736ms two-tone. These include host launch/wait overhead, exclude evaluation/init/readback, and are not ordinary graph device-time shares or a performance upper bound.

`kernels.cu:358,380,387,400` reads child CFVs through `cfv_slot[children[cs+a]]`. Archived D021 PTX, generated from the byte-identical accepted CUDA source, confirms two dependent metadata loads: lines119→122 and277→280 for common two-action paths, and352→355 for a three-action path. Replacing the child-ID-to-slot indirection with a precomputed slot removes one dependent u32 load/address step per child lookup while retaining the same final CFV address.

Counterevidence: that PTX already hoists common-arity child addressing before the hand loop (e.g.277–291 before label292). This is not removal of one lookup per hand in every common path. The arrays are read-only/cacheable, so saved PTX instructions may save little time. E005/E014 already showed that favorable register/occupancy evidence alone need not improve a complete solve. No numerical speed prediction is justified.

## Minimal candidate boundary

1. In `GpuSolver::new_with_budget`, after the final plan is selected, form a temporary `Vec<u32>` in the **original tree.children order**: `child_cfv_slots[e] = plan.cfv_slot[tree.children[e] as usize]`. Do not reorder action nodes, children, CFV slots or levels. The simplest table has exactly `tree.children.len()` entries, preserving existing `node_children_start` indexing.
2. Allocate/upload one immutable `d_up_child_slots` slice before graph capture. In the training up launch only (`mod.rs:965–986`, child argument at974), pass this mapped slice instead of `d_children`.
3. Change the up_action implementation/wrapper child parameter meaning/name and exactly its four nested expressions to `child_cfv_slots[cs+a]`. Keep `cfv_slot[n]` for writing the parent, the arbitrary-menu path, common NA specializations, 128-thread launch, lock path, discount reads, float expressions and order unchanged.
4. Down, evaluation and chance kernels keep original child-ID arguments. No cross-iteration state validity, extra graph, arity partition, new kernel entrypoint, precision/algorithm or quantization change. Evaluation does not need to adopt the mapped array for this bounded experiment.

Likely production targets if a later experiment is authorized: `gpu/mod.rs`, `gpu/kernels.cu`, `gpu/continuation_capacity.rs`. A new GpuPlan field is unnecessary for the simplest constructor-local table; CPU source mapping tests can use the existing plan.

## Exactness and lifetime obligations

- `plan.rs:214–241` assigns immutable physical CFV slots, reusing action/chance slots by level parity. The mapping must use the selected plan's physical slots, not node IDs, arena data offsets, or child index. Preserve every kernel/level dependency; slot reuse itself stays untouched.
- Unreached nodes may carry u32::MAX. Preserve that representation for unused entries. Assert every child actually consumed by every visited action maps to a valid slot; do not make sentinel entries valid accidentally or skip a live child. Cover iso off/on and direct/full versus compact action arenas (`use_full_action_arenas` changes node_data_off only at plan.rs486–490).
- Locked traversal, ordinary update, generic menus >8, and opponent-child sum all must read the exact same ordered addresses. Removing integer addressing leaves signed-zero/NaN float operation sequence unchanged at source level, but compiler changes still require bitwise state validation.
- Immutable per-GpuSolver metadata remains outside the seven swapped mutable continuation buffers. Build/upload before capture, retain it for graph lifetime, and never swap it with parked workspace. New/warm construction and lock-triggered recapture use the same mapping.
- Device payload is exactly `4 * tree.children.len()` additional bytes plus one allocation/upload; constructor temporary host payload is the same. Count it in admission and `continuation_capacity.rs:27–39/43–55` predicted/observed metadata. Do not claim it is retained host payload if the constructor vector is dropped. Record actual peak/added bytes; do not charge only visited edges when using full child indexing.

The existing census gives visited action edges 1,163,503 rainbow;708,022 two-tone;32 river, corresponding to 4,654,012/2,832,088/128 bytes for those edges alone. These are **not exact full-table allocation sizes**, because original children also includes other/unvisited edges. A later CPU-only plan diagnostic can report actual lengths without solving.

## Smallest evidence step

A separate D021-style compiler/resource probe can take the exact accepted CUDA source, transform only the four expressions/parameter semantics, and compile baseline and candidate with identical architecture/default NVRTC options. Save both PTX files and query up_action registers/local/shared/128-thread occupancy. No solver integration or launches are necessary for this first check. Inspect whether dependent metadata loads disappear, whether floating arithmetic instruction/order remains consistent, and whether register/spill/code-size changes introduce countervailing cost. Resource improvements are not performance evidence; unchanged resources do not prove zero possible benefit either.

Only if that source/codegen check is useful should a production candidate be implemented and compared with the retained baseline using the frozen full cycle. Require mapping invariants, all exact arena/EV/stop records, full/compact/F32/locks/warm/resume and continuation workspace coverage. Include added initialization and river effects. Reject if complete-cycle/fixture gates fail; do not optimize the benchmark or accept from PTX, synchronized ranks, or one favorable component.

## Novelty check and exclusions

Read current E001–E016 evidence plus the accepted older GPU-pass report/handoff/milestones and deduplicated postflop results.tsv descriptions. No equivalent up-only child-slot precomputation experiment was found in that searched set. This is a bounded search, not proof that no historical experiment exists anywhere. A peer source critic likewise knew of no equivalent experiment and emphasized mapping/capacity correctness.

E005/E014 changed arity dispatch and node grouping; E006/E007 capped registers; E008 changed showdown prefix storage; E009–E013 changed quantized readback; E015/E016 changed reach reuse. This proposal changes only integer addressing of existing up-action child CFV data. Older CFV compaction/level scratch reuse established the current indirection but did not test this separate precomputed address table. It does not revive rejected card-run/reduction topology or cross-iteration caching work.

No stronger follow-on claim is warranted from source and D029 alone. If the compiler probe is unhelpful or added allocation cost dominates, move on rather than forcing this hypothesis.
