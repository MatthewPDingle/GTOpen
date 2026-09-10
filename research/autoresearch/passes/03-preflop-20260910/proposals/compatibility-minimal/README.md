# Exact low-memory metadata fallback

Proposal only, layered on `compatibility-batch/compatibility.patch` (the parent's applied b7e8583). `minimal.patch` changes gpu.rs and kernels.cu; full copies are included. Source-only `git apply --check` passed against b7e8583. No compilation, GPU execution, server interaction, or active source editing was performed. `generate.py` uses the frozen compatibility proposal and optimized739c68d kernel as sources.

## Why a fallback is needed

Let T be multiway terminals, U union reach slots, C compact capacity, and M compact-map bytes. Holding the original batch B and HU-cache mode fixed, optimized mandatory memory minus original memory is:

    delta = 4*T + 4*U + M - 680*B*(U-C)

Optional normalized reach has already been removed when needed. For union layout C=U and M=0, delta=4(T+U)>0. Therefore budgets within delta bytes above an original grouping/cache boundary can reject even when the old GPU layout fit. This can occur at every B boundary, not just at B=1. There is no evidence to attach a real-world frequency to this; it depends on scenario structure and the user's budget. With cache off and B below32, delta/(680*U) describes the fraction of each continuous idealized budget interval potentially affected, not the frequency of real workloads or integer-MB budgets. Cache-on boundaries have their own reserved bytes.

The compact selection condition compares map bytes against one particle's CDF savings but does not include active/probability storage. It cannot alone prove old minimum-fit preservation. However, the measured fixtures below have so much compaction that even replacing T by *all* terminals gives a negative upper bound on delta at B1, hence no new mandatory-memory rejection for those layouts at any B>=1:

| Fixture | U | C | Upper-bound delta at B1, bytes |
|---|---:|---:|---:|
| three | 30 | 20 | -6,088 |
| six-small | 10728 | 5890 | -2,940,784 |
| seven | 473277 | 228562 | -149,156,712 |
| eight | 760578 | 388082 | -222,693,912 |
| modeled-six | 846156 | 432300 | -253,793,168 |

These bounds use counts from the existing compact/budget logs, not new hardware runs. Arbitrary union-like fixtures still need protection.

## Implementation

- The compatibility planner first tries the preferred optimized metadata exactly as before. If mandatory allocation cannot preserve reference B/cache, it chooses **the original union CDF/direct layout** instead of returning CPU fallback.
- This layout has no active-mask, probability-table, normalized-reach, or compact-map allocation. `CudaStream::null<T>()`, supported by installed cudarc0.19.7, gives zero-length buffers without changing field types. CUDA runtime handling of those zero-length pointers is explicitly covered by the proposed GPU tests and remains unverified until they run.
- Skip clear/prepare/normalize. Force CDF gate=0 and compact=0, so the existing direct CDF kernel never reads null active/map buffers. Preserve the exact scan, source order, particle count, batch size, and launch shape.
- Select a separate `pf_multiway_terminal_minimal` entry. Its body is copied from the preferred terminal, with only the probability input replaced by reach_mass and the original ascending-q product recomputed in thread0 for every terminal/batch. It includes folded opponents and excludes own reach. Remaining opponent/sample/quadrature/payoff arithmetic is identical. The preferred kernel is unchanged.
- Preserve the original HU-cache mode. Keep the capacity-extension path unchanged when the old union plan cannot fit even one particle. Overflow/nonfinite budget errors still fail explicitly.
- The fallback has static allocation and branch choices established at construction, so graph capture/replay follows the same invariant. No dynamic launch counts or reads of host masks are introduced.

The direct fallback deliberately gives up gating/normalization/compaction only at otherwise unsupported boundaries. It preserves the older GPU capability rather than falling to CPU. It does not attempt a second optimized compact-without-active path, which would add layout combinations for marginal gain. Actual allocator/device fragmentation failures remain possible, as in the old path.

## Tests included, not yet run

- Update the two host rejection assertions to require the same B/cache with original-layout fallback and no normalization. Other reference-planner, cache, overflow, and capacity-extension tests remain.
- `coupled_minimal_metadata_preserves_graphs_and_counterfactual_values`: use a private test force switch to compare preferred versus minimal at identical budget/B/cache. Three iterations exercise eager launches and learning/evaluation graph replay, with exact full arena/gap/EV comparisons. Then poison CDF/value storage and test positive, zero-own, zero-live-opponent, zero-folded-opponent, and positive ungated recovery, against each other bitwise and the existing CPU terminal tolerance.
- Ignored `coupled_minimal_metadata_retains_former_union_budget_fit`: search bounded4-6seat fixtures for a real integer-MB union boundary, allowing no forced minimal switch. Construct automatic union fallback and normal compact path at the identical reference B/cache and compare an iteration/check exactly. It requires a small fixture crossing an actual integer-MB boundary; discovery is source-designed and has not been executed. Keep this supplementary test separate from frozen benchmark fixtures.
- `coupled_hu_cached_and_direct_terminal_bits_match`: fixed non-unit sparse reaches and every seat, toggling only the existing HU-cache dispatch while its allocation remains present and before graph capture. Compares every two-live terminal's bits. This independently tests the source arithmetic assessment below.

## HU cache numerics review

The cached `pf_equities` and direct path in `pf_terminal_impl` both accumulate j=0..168 as `d += eqtab[j*169+h]*reach[j]`, then divide by the same reach-mass value. Cache loading into shared memory does not intentionally change precision. The direct terminal loop excludes nonpositive mass before using equity; the cached kernel writes0 there. On valid finite inputs, there is no intended mathematical or operation-order difference. Nevertheless CUDA compiler contraction/register choices and future edits are reasons to retain the new direct-vs-cached test and not claim universal bitwise identity from source alone. Production compatibility continues to preserve cache mode regardless of that test outcome.

## Integration gates

Run the new host tests and focused GPU tests, then the supplementary actual boundary. Verify zero-sized allocations and graph replay on the target CUDA driver. Re-run existing direct/normalized, compact/union, active-zero, modeled/frozen/point-lock controls and the six-iteration exact native comparator. No tolerance changes are proposed. The natural union boundary should stay GPU at original B/cache; normal high-memory compact cases should keep preferred metadata and their current allocations. Benchmark preferred fixtures after the extra kernel is compiled; source-identical preferred math is not a promise of identical machine-code placement or timing.
