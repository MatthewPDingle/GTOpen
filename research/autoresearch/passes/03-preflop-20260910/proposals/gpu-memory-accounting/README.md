# Preflop CUDA buffer accounting audit

Source-only review of optimized `9333943729e87addc74ff489f67e115c06413d8c` (compatibility planner from b7e8583) and frozen original wrapper under `proposals/original-modeled-budget-baseline/gpu.rs`. No builds, CUDA calls, hardware measurements, active edits, or server access.

## Finding

No gigabyte-scale uncharged application buffer was found in either constructor. The baseline per-node bookkeeping formula is incomplete, but its64MB allowance more than covers those omitted buffers for the modeled six-seat fixture. The **latest optimized compatibility logs do not show the reported1.2GB excess** once the before-constructor driver usage is subtracted. The approximately1.1GB excess appears in the original union-cache controls and remains unexplained runtime/driver/allocator usage after this source audit.

There is a real maintainability issue worth correcting separately: `minimum_vram_mb` uses `N*(12P+44)` bytes for scalar tree metadata. Actual corresponding buffer payload is `N*(12P+64)-4`, assuming the constructed tree hasN−1 edges. That is20N−4 additional payload bytes, not1.2GB atN=1,845,520. The planner then adds64,000,000 bytes of allowance. Below approximately3.19million nodes, the allowance also covers all other small fixed arrays listed below. At larger trees this formula can understate payload and should become an explicit ledger rather than rely on a fixed cushion.

## Exact allocation ledger

Notation: N nodes, P seats, C=169 hand classes, R=N+P−1 reach blocks, V compact value blocks, A arena elements, U union multiway source slots, K compact CDF slots, B batch particles, S=1024 particles, T multiway terminals. Every listed buffer element is4bytes.

| Actual CUDA buffer(s) | Bytes | Planner accounting |
|---|---:|---|
| d_reach, d_reach_mass | 4R(C+1) | Exact first term of minimum_vram_mb |
| d_val | 4VC | Exact value-block term |
| d_regrets, d_strat | 8A | Exact two-arena term |
| d_inv, d_rw, d_reach_src | 12NP | Exact NP term; rw is only one scalar per seat/node, not169 values |
| d_kind, d_actor, d_na, d_off, d_cstart, d_live, d_winner, d_potf, d_pots, d_potg, d_calib, d_src, d_foff, d_val_slot | 56N | Part of incomplete44N scalar allowance |
| d_children | 4(N−1) | Same scalar allowance |
| d_act_nodes + d_terms | 4N | Their node partition is disjoint/exhaustive; same scalar allowance |
| d_eq | 4C² =114244 | Small fixed payload covered implicitly by64MB allowance |
| d_cbase + d_cprob | 8C =1352 | Small fixed payload, same allowance |
| d_eval_roots | 8PC | Same allowance |
| d_forced | 4max(forced.len,1) | Corrected forced_storage_bytes/reserve_forced_vram_mb, before other caches |
| d_eq_slots, d_eq_blocks, d_eq_work, d_eq_cache | 4(slots+blocks+work+blocks*C) | Exact EquityCachePlan::bytes when HU cache enabled |
| d_mw_slots, d_mw_blocks, d_mw_work | 4(slots+blocks+work) | Exact mw_plan.metadata_bytes |
| d_mw_order, d_mw_lower, d_mw_upper | 12SC =2076672 | Exact fixed term with active coupled terminals |
| d_mw_terms + d_mw_prob | 8T | Exact optimized fixed term |
| d_mw_active | 4U | Exact optimized fixed term |
| d_mw_compact | 4PU if compact | Exact compact.bytes; union placeholder4bytes otherwise |
| d_mw_cdf | 4K(C+1)B | Exact selected plan.cache_len charge, including compatibility batch |
| d_mw_normalized | 4KC when used | Exact plan.normalized_bytes; placeholder4bytes otherwise |

Disabled HU caching uses one element each in slots/blocks/work/cache:16bytes total is uncharged explicitly, covered by the allowance. A non-multiway game uses tiny dummy multiway buffers; if the solver has the coupled model but no multiway terminal, the three rank tables are still uploaded (~2.08MB) despite no active fixed-term charge. This is also small and covered at the present fixture sizes, but an explicit ledger should count it. Union-map and non-normalized placeholders similarly add4bytes each.

`clip_lo`, `clip_hi`, use_* flags, spans, source plans, static-seat/BR masks and host Vec capacities are host fields or scalar kernel arguments, not further device-array payload. Constructor finalizes h_snapshot=None and graphs=None. The pinned CPU snapshot is allocated later at sync and is host-pinned storage; captured graphs are created later during iteration/check replay. Neither explains an excess already measured immediately after construction. Profiling events are test-only and not active in these constructor controls.

## Modeled-six payload versus plan

N=1,845,520, P=6; both caches enabled, compact+normalized path active.

Actual payload minus planned payload is:

```
20*N - 4 + 4*C*C + 8*C + 8*P*C - 64,000,000
= -26,965,896 bytes
```

Thus the declared plan is approximately26.97MB **above** the explicitly requested buffer payload. Missing calibration/realization metadata cannot account for a gigabyte discrepancy. With disabled HU cache add16bytes; this does not alter that conclusion.

## Reconciliation with existing logs (decimal bytes)

Driver allocation delta below is `(total-free after constructor) - (total-free before constructor)`. Do not compare absolute process/device used memory directly to the application's planned buffers: before the constructor there is already1,333,264,384bytes in these logs.

| Existing raw log | Planned bytes | Driver delta | Delta minus plan |
|---|---:|---:|---:|
| budget-compatible-19000-a | 12,712,124,392 | 12,719,226,880 | +7,102,488 |
| budget-compatible-23000-a | 14,769,872,392 | 14,766,047,232 | −3,825,160 |
| budget-original-19000-a | 18,866,759,680 | 19,987,640,320 | +1,120,880,640 |
| budget-original-21000-a | 20,852,030,748 | 21,983,866,880 | +1,131,836,132 |
| budget-original-23000-a | 22,894,462,240 | 24,014,106,624 | +1,119,644,384 |

The original wrapper requests the same baseline arrays. Its multiway fixed term correctly includes its source metadata, three rank tables and terminal list; it does not allocate the optimized active/probability/map/normalization buffers. Its larger union CDF is explicitly charged. Its corrected forced-policy allocation is explicitly charged. Therefore that original-only approximately1.12GB excess is **not a missing explicit CUDA buffer found in the source**.

Under the ledger, optimized19000's driver delta exceeds actual requested payload by approximately34.07MB; optimized23000 by23.14MB. Original19000's unexplained driver delta beyond actual payload is approximately1.148GB. These are useful observations, not an attribution to a specific CUDA mechanism.

## What remains unknown

Installed cudarc0.19.7 `driver/safe/core.rs:1530` allocates exactly len*sizeof(T) as requested, through CUDA async allocation if memory pools are supported, otherwise synchronous allocation. clone_htod calls that once; alloc_zeros allocates once then memsets. Source does not expose a duplicate backing array in either call. CudaContext::new retains the device primary context, so the probe and constructor are not intentionally creating separate independent contexts.

CUDA's actual pool reservation/granularity, module/JIT loading, context-local backing/storage, and other device users can contribute to driver free-memory changes. The constructor loads its module/functions before buffer allocation. Which mechanism produces the original-only delta cannot be identified from these aggregate snapshots. A large kernel-local stack reservation is a possible runtime mechanism, not a proven diagnosis. These snapshots neither prove WDDM paging nor establish pure kernel-throughput speedup.

After the frozen convergence queue, a separate opt-in diagnostic could sum actual CudaSlice len*size_of<T>() for every field and record driver free bytes after module load, after the large CDF allocation and after the remaining buffers. If async pools are supported, record reserved-versus-used pool attributes too. No measurements or instrumentation were run/added during this audit. Keep any allocator-accounting correction separate from the compatibility planner because changing its baseline budget arithmetic changes historical reference batch selection.

## Public estimate versus constructor

`vram_estimate_mb` is a full32-particle approximate estimate, not the constructor's final bounded allocation plan. It intentionally adds the HU cache and, for multiway metadata, charges N*8 instead of actualT*8; that overestimates rather than hides the terminal arrays. The constructor's chosen plan and actual allocated slice lengths are the appropriate quantities for this audit.
