# D037: cache showdown card-position indices

**GO for one bounded experiment, subject to source/resource review.** This is a source-only design from accepted E015. No production edit, compilation, GPU call or performance measurement occurred. E019's independent fold work is not included.

The narrow candidate copies the current river slot's immutable `o_card_pos` u32 indices into per-CTA shared memory, then changes only the integer lookup inside the original two card-removal loops. Keep every float load value, addition order, predicate, scan, hand order, payout expression, zeroing store and barrier unchanged. No new persistent buffer, device upload, constructor allocation or graph node is needed.

## What is actually redundant

In accepted kernels.cu:268–285, each own hand loads its lower/upper prefix values once, before the two own-card runs. The emitted PTX also does this before the two unrolled runs. There is no supported hypothesis here that simply hoisting those float prefix reads removes duplicate work.

Each run repeatedly reads `pos = o_card_pos[t]`, followed by `r = reach_sh[pos]`. Across many own hands, the same opponent-card positions recur. Accepted PTX retains `ld.global.nc.u32` in those loops; it has not cached the complete list in shared memory. This instruction uses a non-coherent read-only cache, so repeated source reads are **not evidence of repeated DRAM transfers**. The proposed mechanism is cheaper/reused integer lookup latency and load instructions, with one cooperative copy per CTA. [NVIDIA PTX reference](https://docs.nvidia.com/cuda/archive/12.4.1/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-ld-nc).

`census.py` performs only combinatorial host counts from the frozen rainbow range strings. Its expansion matches accepted range.rs semantics and reproduces257/319 base hands. For each of1176 unordered future runouts, it counts the exact card-list requests without needing hand-strength evaluation. Across both players, direct position requests range5792–8035 words per CTA. A full shared cache copies438–628 words depending on player/runout. The median direct/copy count ratio is12.2443 for P0 and15.2705 for P1. These are unweighted mathematical lookup counts, not canonical GpuPlan visitation counts, cache misses, speedups or native-time shares. All2352 player/runout rows are retained.

## Exact layout and proof

Plan.rs334–354 emits each sorted valid opponent hand once into each of its two distinct card lists. Therefore, for a river slot:

`base = o_card_off[slot*53]`, `end = o_card_off[slot*53+52]`, and `end-base == 2*m_o`.

The existing shared regions are `ro_sh[nh_o]`, `reach_sh[m_o]`, and `prefix[m_o]`. Place `u32 card_pos_sh[2*m_o]` immediately after `prefix[m_o]`, at byte offset `4*(nh_o+2*m_o)`. The existing float-aligned shared base and all offsets are4-byte aligned; these regions are disjoint. Cooperatively copy `o_card_pos[base+j]` to `card_pos_sh[j]` for `j<2*m_o`, before the existing first block barrier. No new barrier is required. Replace only `o_card_pos[t]` with `card_pos_sh[t-base]` in the original inner loop.

For each consumed t, the original offsets guarantee `base<=t<end`; the cache therefore returns exactly the same integer pos. The unchanged reach lookup returns the same float bits. All c0/c1 loops and their t order remain intact, so the same arithmetic operands are presented in the same source order. This still requires actual exact-state checks because changed codegen can affect registers/scheduling/FMA decisions; source reasoning alone is not a runtime accuracy pass.

Do not assume base is0 or derive it from a node ID. Do not overwrite/reuse prefix storage, cache floats, merge the two card lists, split lower/tied/higher runs, alter the prefix scan, or cache across CTAs/iterations. Cache lifetime is only the current CTA. With m_o0 the copy is empty and every card run is empty; no cache dereference occurs. Own-hand count0 remains a valid but potentially wasteful copy case. All threads retain every original barrier.

## Shared-memory cost and integration scope

Both training and evaluation compute `show_shared` in mod.rs:854 and627. Both must change from `8*riv_max_cnt[opponent]+4*nh_o` to `16*riv_max_cnt[opponent]+4*nh_o`; all other launch dimensions/arguments/order remain unchanged. Allocation remains at the global plan maximum even when a particular slot is smaller.

The closed D033 actual graph descriptors report the following rainbow allocations. The independent census reproduces their existing maxima:

| Traverser | Opponent base hands | Max valid opponent hands | Existing dynamic bytes | Proposed dynamic bytes |
|---|---:|---:|---:|---:|
| P0 |319|314|3788|6300|
| P1 |257|252|3044|5060|

Archived D005 reports up_show40 registers,0 local bytes/thread and1040 static shared bytes. Treat these as prior diagnostic values, not proof of candidate residency. The candidate adds2512/2016 dynamic bytes in these rows. Conservative nh_o=m_o1326 would increase dynamic storage15912→26520 bytes, before static shared/driver granularity. Query actual baseline/candidate resources, max threads, shared limits and occupancy with each relevant dynamic size before qualification. Do not infer occupancy from the old register count or assume the capacity increase is free.

This shared memory is per-SM launch storage, not an allocation in global VRAM or a solver-owned arena. No `staging_bytes`, public VRAM estimate, continuation global-capacity accounting, storage ownership or paging swap changes are justified. Continuation training/evaluation uses these same GpuSolver launch sites and must inherit the increased shared reservation. Hardware launch-resource feasibility remains an admission concern distinct from the global byte budget.

## Minimal falsifiable experiment

Start from exact accepted E015; only kernels.cu and the two `show_shared` expressions in mod.rs should change. Preserve full base/candidate bytes and patch. First compile/query both sources under identical production options and query up_show resources at the actual fixture dynamic sizes plus wide-range capacity. PTX should show cooperative integer copy and shared integer lookups in the card loops; inspect for spills/register or occupancy loss and unchanged floating-operation structure. PTX/resource results are diagnostic only.

Use small host invariants on real/constructed flattened metadata: slot length2*m_o, nonzero base, exact position-copy identity, cache offsets/regions disjoint, empty slots, asymmetric counts and both player directions. Existing immutable full-state comparisons provide the first actual kernel/solver screen; a second large standalone corpus is not required merely for this integer address relocation. If promising, complete the existing independent F32/compressed raw/control, tie/same-hand blocker, iso/full-layout, menu/lock, evaluation and saved/resume/continuation checks before acceptance. A tiny full-up_show differential is useful only if a concrete coverage gap remains, especially nonzero-base and empty/tie cases; avoid duplicating a large harness without a reason.

The registered native complete-cycle gates and fixture regression guard still decide retention. Falsification is straightforward: added copy/register/shared cost may erase any lookup savings, reduce occupancy, or push the full-cycle result below the existing2% threshold. The existing read-only cache may already make position loads cheap; shared bank conflicts may worsen them. No speed claim follows from lookup counts, resources or D033's heavily perturbed event intervals.

## Novelty boundary

Current E008 changed only thread0's serial prefix carry to a register. Its three-pair compressed screen was exact but rejected at1.6963097%, below2%; broader F32/control validation was not run. Its preserved patch and comparison are inputs here. D037 leaves that entire prefix block byte-identical and does not revive E008.

Older postflop E034 split sorted card-removal loops into lower/tied/higher runs and was discarded. D037 preserves those loops/predicates and relocates only immutable integer positions. The scoped historical search found no same cache experiment; this is not a claim of global novelty. If the shared-position cache is resource-infeasible, stop this candidate. A separately authorized53-offset shared cache would be a different, smaller fallback hypothesis, not an automatic rescue or combined optimization.

Independent source critic menu_change_review found the layout/identity argument coherent, emphasizing nonzero-base subtraction, both launch reservations, empty lists, increased occupancy pressure and actual-state validation. Source and census artifacts are sealed by the adjacent manifest; closed prior evidence is untouched.
