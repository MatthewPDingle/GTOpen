# Prefer deployed arithmetic while accurately accounting memory

Proposal only, layered after `compatibility-minimal/minimal.patch`. `deployed.patch` changes only gpu.rs; the minimal proposal's CUDA source is unchanged. Full gpu.rs is included. Four pure host tests and the existing planner/GPU tests cover the new selection policy. No active source edits, compilation, hardware work, or frozen-protocol changes.

Apply in order to the corrected-reference candidate: (1) minimal.patch, (2) deployed.patch. The deployed patch was source-checked against an extracted LF-normalized minimal source. Full source copies use CRLF for review; repository patches use LF. Generator inputs are frozen proposal files, not the moving active checkout.

## Policy

The constructor captures the original pre-pass base immediately before the existing accurate forced-policy reservation. It does not subtract forced bytes from an already-rounded total. The literal base is used only to reproduce the old numerical B/cache target. Physical budgeting always uses the accurately accounted base.

Selection order:

1. Literal deployed B/cache with preferred optimized metadata; normalization remains optional at that exact target.
2. The same literal target with minimal/original metadata if necessary. Its real cost includes forced bytes, so this cannot reintroduce the budget bug.
3. If the literal target is physically unsupported, use the corrected-budget reference through the same fit choices, labeled `corrected_budget_fallback`.
4. If no corrected union reference fits one particle but optimized compact storage fits, use the existing explicitly labeled `capacity_extension`. Otherwise return no fit/CPU fallback.

`batch_policy` now names the selected reference source: `deployed_prepass`, `corrected_budget_fallback`, `capacity_extension`, or `not_applicable`. Layout diagnostics include literal requested B/cache and selected reference B/cache. Fallback logging states that deployed grouping could not fit safely. Preserved choices include HU metadata costs and cache-off states; new free memory does not arbitrarily toggle a cache.

The underlying corrected-only wrapper remains under cfg(test) for independent host/oracle tests. The physical fit helper returns None for a target that exceeds the real budget; overflow and invalid accounting still return errors. This separation lets the caller try a safer target without confusing an arithmetic overflow with a capacity limitation.

## Measured-cost host controls

| Budget MB | Literal target | Corrected target | Candidate accurate physical MB retaining literal |
|---:|---|---|---:|
|19000|B24 / HU off|B23 / HU on|12689.815140|
|21000|B27 / HU on|B27 / HU off|13887.980392|
|23000|B31 / HU off|B30 / HU on|14747.563140|

Costs derive from existing modeled-six logs: accurate base+original fixed5316606588B, literal base+fixed4902313904B, HU316273252B including13564508B metadata, U846156, C432300. Tests fold original fixed costs into the bases and pass optimized extra25837752B separately. All four-byte and integer-MB budget assertions use actual planned physical bytes, not old under-accounted totals.

Additional host tests require corrected fallback only when the literal target cannot fit even minimal storage, preserve the literal B by dropping normalization, distinguish capacity extension from both references, reject complete no-fit/invalid bases, and retain the pre-pass B1 across a four-byte empty-forced-placeholder edge when compact storage permits it.

## Required validation

Do not change or relabel the frozen corrected-accounting convergence binaries/protocol. Keep those results and add a separate literal-deployed compatibility matrix. Compare the literal1b8fc3f constructor targets and this candidate at19/21/23GB, then full native arenas/effective policies at identical iterations. Include the previous deep low-reach outliers; do not use weighted averages to dismiss avoidable local differences.

Run all host, low-memory/minimal, graph replay, direct/normalized, compact/union, active-zero, modeled/frozen/point-lock, all-solver, and HU-cache tests. The private force-minimal constructor constrains layouts only in tests; it may choose corrected reference if the forced union layout cannot fit the literal target even though normal compact construction could. Production always tries the preferred layout first.

Native saves still do not record their historical B/cache choices. This targets literal pre-pass behavior at the same supplied budget/configuration, not arbitrary older devices, budgets, or solver versions. Accurate budget refusal and capacity extension can necessarily change grouping when the literal target cannot fit safely; logs make that limitation explicit.
