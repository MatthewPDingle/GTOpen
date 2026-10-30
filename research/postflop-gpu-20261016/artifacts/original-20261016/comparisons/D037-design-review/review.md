# D037 independent source-design review

PASS for preparing one bounded two-file integer-cache candidate and a resource-only probe. No actionable design defect remains. This review does not establish compiled feasibility, runtime numerical equivalence or performance. No builds, CUDA calls, solver execution or production edits were performed.

The reviewed frozen README is37c28a9b14ab49a3f7e7d78621ed3d845a890dc7ed3bac52515c623eb3c35fc2; design manifest82075db7cd76f5b37b3db17ab081bb5b018bebd51d6f6db2a22da747a7340158. All15 sealed artifact hashes and7 input hashes verify. The archived source matches accepted E015; E019 fold changes are absent.

## Bounds, layout and synchronization

Accepted plan.rs334–354 adds each valid sorted opponent hand position to its two distinct card lists and flattens those lists contiguously. Therefore end-base=2*m_o; each copied pos is in[0,m_o), and every original consumed t lies in[base,end). Subtract the slot's first global offset, not zero or a node/slot ID. A cache beginning at4*(nh_o+2*m_o), after ro/reach/prefix, occupies8*m_o bytes with no overlap and the same4-byte alignment requirement already imposed by float storage. The host reservation4*nh_o+16*riv_max covers every slot's4*nh_o+16*m_o layout.

The cooperative copy before the existing first block barrier initializes every cache entry before use. Existing b>=count early return is CTA-uniform; no new per-thread return or barrier is introduced. For m_o=0 all card offsets equal base, so neither copy nor card-removal loop dereferences the cache. For m_p=0 the copy may be unnecessary but remains valid. Both directions and nonzero bases need the planned small host invariant checks. These are proof obligations for the forthcoming candidate bytes, not grounds to alter stored plans or add runtime branch policy.

## Exactness and lifecycle

Only integer address resolution changes. The original card loops, their iteration order, pos predicates, reach values, prefix scan, same-hand correction and payout expression remain identical. No float cache, scan carry, split lower/tie/higher loop, reduction tree or extra launch belongs in this candidate. Source arithmetic identity supports feasibility, but compilation may affect code generation; the first native screen must still enforce original complete-state/exploit/stopping equality. No universal NaN-payload or accuracy claim is inferred.

Exactly two postflop up_show launch sites exist: training and eval_up. Both require8*riv_max+4*nh_o to become16*riv_max+4*nh_o. Their ABI, grid/block shape, graph capture/replay order and persistent pointer lifetimes remain unchanged. Generic/continuation execution reaches these same methods. Existing unit/evaluation, original F32/compressed, saved/menu/lock/resume and selected continuation controls are sufficient if performance qualifies. No new graph/lifetime harness or second broad numerical corpus is justified for this delta; add a tiny differential only if a concrete uncovered case appears.

## Resource and performance limits

There is no added global allocation or ownership, so staging/admission/global VRAM estimates should not change. Per-block shared-memory feasibility and occupancy do change. Query the compiled baseline/candidate resources, max block threads, dynamic/static shared limits and occupancy at actual registered-fixture launch sizes plus the conservative full-range bound. Preserve identical architecture/options. No resource-only probe kernel launch is needed. Reject an infeasible cache instead of silently adding a threshold or offset-cache fallback.

The verified census arithmetic gives rainbow dynamic allocations3788→6300 bytes for P0 and3044→5060 for P1. Wide-range nh_o=m_o=1326 bounds dynamic storage at26520 bytes before actual static storage and driver allocation granularity. Prior1040-byte static shared and40-register values are historical, not a candidate capacity claim. Added register pressure, prefetch work, shared-bank conflicts or reduced residency may erase the hypothesized gain.

The census is an unweighted1176-runout/2352-direction logical lookup census. It is not a canonical visitation count, DRAM traffic estimate or timing result. The NVIDIA PTX specification describes ld.global.nc as accessing global data through a non-coherent read-only cache, so repeated source requests cannot be equated to repeated DRAM transfers. [NVIDIA PTX8.4 ld.global.nc](https://docs.nvidia.com/cuda/archive/12.4.1/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-ld-nc).

## Novelty and next gate

E008's preserved patch changes only thread0 prefix carry; D037 leaves that block unchanged. Old E034 split card-removal loops; D037 retains them. Thus this is a distinct bounded hypothesis within the inspected history, without a global novelty claim. D033's perturbed event percentages are not used as native shares or causal evidence.

Next: freeze only kernels.cu plus two host shared-size expressions outside checkout; review exact diff; run the parent-owned resource probe. If feasible, the unchanged complete-cycle primary and exactness gates decide whether broader qualification is warranted. All failed preparation/build/resource/native evidence must remain preserved.
