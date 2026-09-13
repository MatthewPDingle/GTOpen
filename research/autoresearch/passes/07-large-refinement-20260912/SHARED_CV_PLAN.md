# Shared-reference GPU control variate: registered numerical and storage screen

Research only. Port 56708 stays untouched; hardware work runs serially through
run07's read-only live-work guard. Do not claim a speedup from storage savings.
The old CV baseline duplicated range/mass snapshots per learning player and
required 12.197 GB extra on the large fixture; it also ran eager GPU sweeps.

## Distinct representation and update order

Keep ONE range/mass snapshot, captured before the first alternating sweep of
an epoch. Replace zero reference range mass with the existing fixed class prior
so the control function is defined everywhere. This is a control reference,
not a changed player policy. Compute canonical 1,024-particle unit-probability
payoffs for every learning traverser against that shared snapshot. Cache only
multiway terminals at which the traverser is live; folded/fixed entries use an
invalid-offset sentinel. Preserve f32 precision and native particle grouping.

An epoch lasts a configured 16, 32 or 64 complete iterations (numerical tests
may use 1 or 2). For each normal alternating update, use the existing sampled
current payoff plus actual opponent reach probability times (cached full
reference payoff minus reference payoff for the IDENTICAL sampled particles).
Do not clip the correction. Keep native counterfactual regret units, current
opponent policy timing and the selected DCFR averaging schedule. This reference
can be older than a traverser's latest opponent update; unlike old per-traverser
refresh-one, shared refresh-one need not reproduce the full gradient per sweep.

Refresh and table selection occur outside learning graphs. Capture stable
sampled correction/update operations separately for each traverser. Refreshes
must not replay a graph that still refers to current buffers as reference, nor
change canonical evaluation. All ordinary scalar/HU/folded values stay native.

## Gates before any convergence experiment

1. Exact read-only inventory on the saved 1,567,754-node geometry. Include shared
   reach/mass, packed full payoffs, offsets, and dense current-terminal scratch.
   Checked arithmetic; explicit 4 GiB extra-storage cap before allocation.
2. Small CPU plan equals actual GPU allocation. Packed cache round trips every
   live terminal/hand exactly, and rejects invalid kinds/masks/offset overflow.
3. At 1,024 particles, correction cancels exactly against disabled native
   updates: full arenas and full-check values, including a frozen seat and lock.
4. Across all sixteen disjoint 64-particle cohorts, the mean correction matches
   the canonical full current terminal payoff within 2e-4*(1+abs(reference)).
   Exercise a stale snapshot, zero reference/current ranges, and raw/calibrated
   HU continuation. No expectation of per-sample exactness.
5. Captured/eager shared-CV iterations agree exactly for all arenas, reference
   ranges/masses/full caches, and native full evaluation. Evaluation is read-only
   for learning/reference state. Test repeated refresh, stop/admission failures,
   and disabled native/old-CV compatibility.
6. Native GPU equivalence and the full default release solver suite pass.

After these gates, register a bounded variance/cost or convergence screen with
matched seed/schedule controls and the unchanged global/conditional criteria.
The numerical/storage screen does not itself admit a large learning run. Preserve
all failed results; no unrecorded retries or relaxed quality/memory thresholds.
