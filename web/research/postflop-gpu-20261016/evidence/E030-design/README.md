# E030: fixed fold-card task order

This is one off-tree candidate from exact accepted E020. It is not activated, compiled, numerically qualified, timed or accepted. D055 establishes source feasibility and a structural proxy only; the next decision is a bounded complete-kernel exact/compiler feasibility diagnostic, not automatic primary execution. There is no established native latency saving or 2% complete-cycle headroom.

## Exact scope

Five owned files are archived under `base/` and `candidate/` with repository-relative paths. The kernel's card-task loop maps each task through an immutable 52-card permutation. Each card still starts at the original positive zero, visits the original hand-index list in ascending order and writes the same unique `s[card]`. The thread-index partial-total loop, reduction, floating expressions, barriers, output arithmetic, block width128, shared reservation and launch arguments are unchanged. The other eight CUDA entry points are byte-identical. Both training and evaluation already select the opponent's fold metadata.

The two existing offset buffers contain their original53 u32 offsets followed by52 card IDs. Ordering is fixed descending list length with ascending card ID ties. Every card is assigned once, including empty card lists. The original offset prefix and complete hand-index vectors are unchanged. The helper executes before the constructor's struct moves and borrows no partially moved plan. There is no new ABI, device buffer, mutable workspace, cache validity rule, graph variant or save format.

## Payload and admission

Each offset allocation grows from212 to420 bytes, exactly416 bytes across both players. `game::GPU_FOLD_CARD_TASK_BYTES` is available without the GPU feature. It is added once to `GpuPlan::staging_bytes()` for constructor full/compact admission and existing exact-budget callers, once to the independent public conservative estimate, and once to continuation planned immutable metadata. Observed metadata already sums the actual two offset-buffer lengths. The continuation workspace still derives all seven mutable components directly and does not add staging_bytes, so the new immutable payload is not double counted. Public11-component workspace schema, host/SSD swaps, examples and stored-state payloads stay unchanged. Near-budget admission can legitimately differ by416 bytes.

The staging_bytes callsites are constructor admission/logging, existing unit/test budgets, continuation estimate examples and postflop capacity logging; none constructs a mutable buffer length from that total. Constructor temporary host vectors gain416 bytes before upload and are dropped as before. Sorting, two extra uploads of208 bytes, the new integer lookup, possible shared-bank changes and warp overlap are real costs. Full-range task lengths tie, so their original ordering is retained and the proxy predicts no work reduction.

## Focused tests and checks

One new host-only unit, `gpu::tests::fold_card_order_preserves_offsets_and_permutation`, checks empty, full-deck equal lengths and a concrete asymmetric five-hand set with positive and zero ties. It requires exact offset-prefix preservation, a complete unique52-card permutation and an independently specified expected order. The existing `gpu::plan::tests::river_bounds_match_strength_comparisons` additionally checks the416-byte admission delta and public conservative bound across three boards with and without isomorphism.

Accepted E020's native inventory is84 passed/4 ignored; one added ordinary unit and no removed/changed ignore declarations gives prospective85 passed/4 ignored (89 total). This is an inventory expectation, not a test result. Syntax-only rustfmt and patch applicability are the only external source checks performed here; no Rust typecheck, CUDA compilation or native numerical execution is claimed.

## Direct prerequisite

The separately owned `runs/E030-fold-card-order-exact` preparation reuses D036's17 full scenarios, both player orientations, five fixed block widths and its zero-count cases:180 complete-kernel pairs/360 launches. Width128 is production;16/32/64/256 are explicitly supplemental. Raw-total helper kernels are omitted. Baseline consumes the original53-word offsets; candidate consumes the same prefix plus the fixed52 IDs. All original card indices/reach/input/output data, exact bit comparisons (including any overflow-produced nonfinite bits), poisoned output guards, full device input readbacks and anti-vacuity checks remain required. That plan and eventual package receive independent review and root execution authorization. No alternative sort order, rescue or outcome-triggered matrix change is proposed.

After direct exact/compiler feasibility, root must make a separate decision about any fixed full-cycle primary experiment. Source proof, counts, occupancy or isolated controls cannot establish a speedup. A passing primary would still require the established broader qualification before adoption; this archive does not authorize it.
