# Literal deployed grouping versus corrected-accounting reference

Read-only assessment; no source edits, GPU work, or protocol changes. Sources: literal `1b8fc3f:crates/solver/src/preflop/gpu.rs`, corrected-control `budget-original-{19000,21000,23000}-a.log`, and optimized `modeled-opt-batch30-a.log`.

## Quantified modeled-six choices

The literal code creates `need = minimum_vram_mb(...)`, fills forced policies, but does not add their allocation before choosing the union CDF batch or optional HU cache. The pass's corrected control adds that allocation first. For this fixture, forced storage is **414,292,684 bytes**, union CDF particle size **575,386,080 bytes**, accurately accounted base plus original fixed metadata **5,316,606,588 bytes**, and literal pre-fix base plus metadata **4,902,313,904 bytes**.

HU allocation planning includes both the equity entries and their metadata: **316,273,252 bytes total**, consisting of **302,708,744 equity bytes + 13,564,508 metadata bytes**. The JSON field `hu_equity_cache_allocated_bytes` records the equity array only; it is not the full planner cost. The reduced compatibility test fixture folds these costs algebraically for selected cases and should not be treated as the exact component breakdown.

| Budget MB | Literal deployed B / HU cache | Corrected reference B / HU cache | Literal reported need MB | Literal need including forced bytes MB | Accurate compact+normalized need retaining deployed B/cache MB |
|---:|---|---|---:|---:|---:|
| 19000 | 24 / off | 23 / on | 18711.579824 | 19125.872508 | 12689.815140 |
| 21000 | 27 / on | 27 / off | 20754.011316 | 21168.304000 | 13887.980392 |
| 23000 | 31 / off | 30 / on | 22739.282384 | 23153.575068 | 14747.563140 |

These are source/log arithmetic results, not fresh constructor measurements. The chosen integers are far from floating-point byte-boundary ambiguity. The literal original overran its specified budget by125.9–168.3MB, although actual allocator overhead/available VRAM decides whether a run succeeded. Compaction creates ample space for exactly those arithmetic choices while correctly reserving all forced-policy bytes.

## Recommendation

Prefer **literal pre-pass batch/cache choices as a numerical compatibility target**, separately from accurate physical memory accounting. This does not preserve the allocation bug. It preserves the arithmetic grouping chosen by the old code only when a safe current allocation can implement it.

For the modeled fixture, the currently validated corrected-reference compatibility path still introduces an avoidable deployed-policy change at19/23GB, because B differs. At21GB B matches but cache dispatch differs; source arithmetic and dedicated tests may show cache identity, but corrected-reference parity alone does not establish deployed full-run identity. The existing corrected-baseline results remain valid comparisons to that baseline and should not be relabeled as literal-deployed parity.

A bounded candidate selection order:

1. Record the literal reference base before reserving forced bytes, preserving the original floating-point operation sequence. Do not recreate it by subtracting bytes from the already-rounded corrected total.
2. Independently reserve actual forced storage and validate the accurate base budget. All candidate physical fits use this corrected base.
3. Obtain the literal pre-pass union B and HU-cache decision. Try the optimized layout at this exact B/cache, dropping optional normalization if needed. If mandatory metadata still prevents fit, try the minimal-metadata/original-layout fallback with the same target and *accurate* base. Do not let either choice exceed the real budget.
4. Only if this target cannot fit with any supported exact layout, try the current corrected-reference B/cache. Label this as a safe grouping fallback, not deployed parity. If preserving B while dropping a formerly enabled cache is considered later, require independent full-run parity before treating it as compatibility; preserving both is simplest now.
5. If even the corrected old union planner has no one-particle fit but compact does, retain the existing explicitly labeled capacity extension. If no safe layout fits, CPU fallback remains appropriate.

Layout diagnostics should identify the selected reference source (`deployed_prepass`, `corrected_budget_fallback`, or `capacity_extension`) and both requested/selected B/cache where they differ. No historical save contains GPU batch/cache metadata, so same-current-budget compatibility cannot prove identity to an arbitrary earlier budget/device/run.

## Tradeoffs and gates

- This adds one fallback layer and additional boundary tests, but does not alter the model, precision, particle count, or algebra. The memory correctness fix remains mandatory.
- Retaining deployed B may change measured throughput relative to the corrected-reference candidate; this is expected. Both deployment compatibility and frozen research performance evidence must be reported with their actual baselines.
- Keep the frozen corrected-accounting convergence queue and acceptance protocol unchanged. Add a distinct literal-deployed compatibility matrix; do not replace or reinterpret controls mid-run.
- For19/21/23GB, require the literal old source's observed constructor B/cache and the candidate's selected B/cache to match the table, with accurate physical allocation within budget. Then compare full saved arenas and effective policies at matching iterations, including deep low-reach nodes.
- First use bounded matching checkpoints (e.g. the already-used six-iteration fixture). Literal original23GB may be slow or encounter memory pressure because of its budget overrun; if an execution guard fires, report that control as incomplete. A modified diagnostic control can test arithmetic choices but should not be presented as a literal original production run.
- Preserve all-solver, fixed-policy, frozen, point-lock, low-memory/direct, graph replay, and zero-reach controls. For no forced policies the only missing allocation is the four-byte placeholder; arithmetic choices almost always match, but host tests should deliberately exercise byte-boundary cases.
- Do not claim that a very small weighted strategy difference excuses an avoidable large conditional policy difference. Preserving the deployed batch where physically feasible addresses its demonstrated source rather than changing tolerances.
