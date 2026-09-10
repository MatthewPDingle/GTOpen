# Compact slot implementation proposal

Proposal only. No source/worktree edits, compilation, GPU jobs, or server interaction. `combined.patch` includes implementation, focused tests, and updates to existing tests that inspect storage or reproduce the budget calculation. `implementation.patch` and `tests.patch` are separate alternatives; complete proposed sources and source SHA256 are included.

Generated against the isolated source after the parent added/fixed the boundary test (`083d478`, following the requested423f58a base). Patch applicability passed. The generator reads current sources but writes only this proposal directory.

## Layout

Global source-to-slot maps, work spans, source blocks, and active flags remain unchanged. `MultiwayCompactPlan` creates an immutable per-seat union-to-local map and uses `max(spans[p].count)` as scratch capacity, excluding the trailing union span but including every player for evaluation.

Normalization and both CDF kernels store using their block's index within the traverser's work span. Terminal metadata converts each global opponent slot through the per-seat map once, preserving the original ascending opponent order. CDF scan order, division precision, quadrature, samples, and terminal arithmetic do not change. The compact/union layout flag is uniform across a launch, and all map/buffer addresses remain fixed for graph replay.

Constructor and preferred VRAM estimation include the map bytes before selecting normalized/direct mode and particle batch size. Compaction is selected only when the map plus one compact CDF particle uses strictly less memory than one union CDF particle; otherwise union layout is retained. Thus compact mapping cannot worsen the old minimum fit capability. Existing normalization fallback remains independently applicable within either layout. Legacy games do not use either compact multiway kernels or their scratch.

For the measured eight-seat counts, capacity falls from760,578 to388,082 slots. At32 particles with normalization, the previously measured projection is about8.33GB saved after accounting for the24.34MB immutable map. This is a projected allocation reduction, not a speed claim. Full constructor measurements must confirm actual allocation and optional HU cache changes.

## Tests and integration

- New pure mapping test checks every present/absent slot, local bijection, exclusion of the trailing union span, byte accounting, and union fallback when minimum fit would worsen.
- New CUDA test builds a small actual four-seat tree and verifies every coupled terminal's live-opponent mapping against the original reach-source/work-span lookup.
- The same test constructs union and compact engines from identical initial states at the same32-particle batch and normalization mode, then compares complete arena/gap/EV bits through three learning/check cycles including graph replay.
- It subsequently drops captured graphs, poisons scratch, and alternates differently sized traverser spans with gated/ungated terminal evaluation, comparing all output value bits between layouts.
- Existing non-unit normalization test now indexes normalized storage through the compact map when enabled; its direct-division bit checks remain unchanged.
- Existing actual GPU minimum-budget test now computes budgets using the chosen compact capacity and includes map bytes. It therefore still tests actual constructor-selected direct1 and normalized1 paths rather than stale union-size estimates.

The private `new_with_layout` helper permits forcing union layout only for internal regression controls. Public `new` always performs normal safe layout selection; no user-facing model or configuration option is added.

Tests have not been compiled or run. Before retention, run the pure mapping test, new union/compact parity test, existing active-slot/normalized-input tests, coupled all-hand parity, the explicitly ignored one-particle boundary test, and the broader GPU equivalence suite. Benchmark the exact same particle batch first, then measure actual memory and end-to-end solve/checkpoint time on the user's frozen eight-seat fixture.

Potential costs: one extra global-to-local metadata lookup per opponent and uniform compact-address selection in normalization/CDF kernels. The preferred VRAM estimate currently constructs the immutable map while calculating the estimate; this is approximately24MB temporary host allocation for the measured eight-seat tree. A later planner-only counts helper could eliminate that allocation if it matters; it is not mixed into this correctness-focused candidate.
