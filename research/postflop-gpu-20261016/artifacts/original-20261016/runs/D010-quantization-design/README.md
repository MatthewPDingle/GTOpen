# D010: exact compressed GPU readback integration handoff

Status: design only. No solver integration, build, GPU execution, or deployment is authorized by this artifact. A separate agent is preparing the standalone numeric proof; its results are a prerequisite, not assumed here.

## Evidence and limits

D009 is diagnostic, not qualifying performance evidence. Its full-readback spans were:

| Fixture | Full readback, ms | CPU encode/scatter/restore, ms | DTOH waits, ms |
| --- | ---: | ---: | ---: |
| Rainbow | 352.8043 | 241.0185 | 111.5188 |
| Two-tone | 281.6519 | 204.4361 | 76.8444 |
| River | 1.0354 | 0.8263 | 0.0740 |

Source: ../D009/stdout.log. CPU totals include scatter and inactive restoration; the flop total of 445.4546 ms is not a removable-encoding estimate. Moving active quantization to the GPU still leaves CPU scatter, inactive restoration, new kernel work, metadata, allocation, and extra compilation costs. Transfer payload changes from 4*N bytes to 2*Q + 4*B, where N is the current f32 arena length, Q is the sum of encoded block lengths, and B is the encoded block count. It approaches half the old payload, rather than exactly half.

## Bounded source scope

All proposed paths below are relative to X:\Dev\GTOpen-gpu-research-20261016.

- crates/solver/src/gpu/mod.rs: add one optional QuantizedReadback owner to GpuSolver; select it in new_with_budget; dispatch the compressed branch in sync_to_cpu. Keep the current sync_strategy and F32 paths unchanged for the first experiment. Preserve iteration publication, mark_sym_dirty, and current stream ordering.
- crates/solver/src/gpu/quantized_readback.rs (new private module): descriptors, optional resource preparation, typed host/device scratch ownership, encode/download orchestration, and narrow validation helpers.
- crates/solver/src/gpu/arena.rs: expose or construct exact readback block descriptors; add a compressed q/scale scatter entry point. Reuse the existing inactive restoration body verbatim through a small shared private method if necessary. Do not change snapshot creation, the positive-zero sentinel, upload, or compaction policy.
- crates/solver/src/gpu/kernels.cu: after the standalone proof passes, append its two proven encoder entry points to the existing module. Reuse the existing context/module compilation and stream; no second context or separate NVRTC invocation. Verify precise division and no FTZ in the actual integrated compile path; do not change existing solver arithmetic flags.
- crates/solver/src/store.rs and gpu/plan.rs: retain as numerical/layout oracles. No quantizer rewrite, save-format change, or plan-policy change is needed.
- Tests: add private GPU-module tests for raw arena access and layout tests beside arena.rs; keep the frozen complete-cycle evaluator unchanged.

Proposed experiment switch: POSTFLOP_AUTORESEARCH_GPU_QUANTIZED_READBACK=1. It is disabled by default. Eligibility requires the expected I16 regret and U16 strategy stores for both players. Record whether the optional path was actually selected; a fallback run is not evidence that GPU encoding improved performance.

## Descriptors and layout coverage

For each player build a CPU record with node id, host offset, source device offset, packed output offset, and length. Prefix-sum lengths with checked arithmetic to obtain Q. Device metadata needs only source offsets (u64), packed offsets (u64), and lengths (u32); reject unsupported length/range conversions before launch. One descriptor ordinal owns one scale output and one disjoint packed q range.

- Noncompact: enumerate every tree action node owned by the player, exactly matching write_arena. Do not restrict this list to reached plan.action_nodes: unreachable full-arena blocks are currently re-encoded too.
- Compact: encode only ArenaLayout.active blocks with their device/host mapping. Restore ArenaLayout.inactive through the existing CPU write_f32 calls from saved decoded snapshots or positive-zero sentinels on every sync.
- Scatter q only to each descriptor's host range and scale only to scale[node]. Leave non-owned/unused scale entries and uncovered q ranges untouched.
- Keep inactive snapshot re-encoding even for warm loaded state. Copying original compressed bytes, or leaving current CPU bytes alone, is not equivalent: CPU queries can materialize inactive siblings between downloads.
- Validate zero-length blocks, descriptor bounds, disjoint outputs, and complete intended coverage. Packing the output avoids reading/transferring uninitialized device holes.

## Scratch, budget, fallback, and sequencing

Use a single reusable CudaSlice<u16> wire buffer sized Qmax and a CudaSlice<f32> scale buffer sized Bmax, where maxima are over players. Encode signed results to their 16-bit unsigned representation; scatter to i16 with the exact Rust u16-as-i16 conversion. This avoids duplicate signed/unsigned buffers. Use a small private pinned-u16 owner with matching allocation/free; reuse the existing f32 PinnedBuf type for scale staging. Keep h_staging intact for uploads, F32, sync_strategy, and fallback. Do not reinterpret a live mutable f32 slice as another type.

Keep per-player device descriptor arrays resident and share them between regret and strategy downloads. Extra persistent device data is:

    2*Qmax + 4*Bmax + 20*(B0+B1) bytes

Extra pinned host data is 2*Qmax + 4*Bmax, plus ordinary host descriptor vectors. Count actual allocated lengths and checked padding/minimum-allocation rules. Include this increment in new_with_budget in addition to the existing needed estimate and 512 MiB slack; do not spend that slack twice or alter the base solver admission rule. With an insufficient optional budget, keep the original readback route so a previously fitting solve remains available. Optional allocation failure must clean up partial resources before falling back; CUDA execution/context errors must propagate rather than silently retry after a failed launch. Zero-block players skip launches and copies.

Prepare optional resources inside measured initialization, after eligibility and budget checks, and amortize them across syncs. For each of the four arenas, queue encode -> q DTOH -> scale DTOH on the existing stream, wait for completion, then scatter and perform existing inactive restoration. Never reuse scratch before its copy completes. Keep the existing initial sync and final publication ordering. Do not alter or quantize the original d_regrets/d_strat f32 allocations, lock buffers, graphs, or evaluation state.

## Exact arithmetic contract

CPU encode_i16 / encode_u16 in store.rs remain the oracle. Filter NaNs before unsigned-bit maximum reduction; I16 uses absolute-value bits and U16 ignores negative values. Zero or infinite maxima produce zero integers and positive-zero scale. Otherwise preserve the exact positive maximum bits and evaluate C/max then value*k with distinct binary32 nearest-even rounding (C = 32767 or 65535). U16 clamps negative/NaN input to zero first. Guard NaN and saturation before nearest-even integer conversion.

Tiny positive maxima can overflow k to infinity: I16 negative values then saturate to -32768, positive values to 32767, and zero*infinity/NaN to zero. Do not clamp signed output to a symmetric -32767 minimum. Preserve subnormal arithmetic; no fast division, reciprocal reassociation, FTZ, or float-to-int undefined-range behavior.

References: https://doc.rust-lang.org/std/primitive.f32.html ; https://doc.rust-lang.org/reference/expressions/operator-expr.html#numeric-cast ; https://docs.nvidia.com/cuda/cuda-math-api/cuda_math_api/group__CUDA__MATH__INTRINSIC__SINGLE.html ; https://docs.nvidia.com/cuda/cuda-math-api/cuda_math_api/group__CUDA__MATH__INTRINSIC__CAST.html .

## Required proof and qualification

1. Standalone numeric proof must compare every q element and scale.to_bits against the actual Rust encoder. Cover half ties and adjacent floats, saturation endpoints, normal/subnormal boundaries, reciprocal overflow, both zeros, signed infinities, quiet/signaling NaNs and payloads, mixed blocks, empty blocks, and seeded random bit patterns. Preserve mismatch evidence.
2. From the same downloaded raw GPU f32 image, compare old CPU encoding with the optional path for all q bytes and every scale entry, including deliberately seeded unused scales/q gaps. Test full and compact layouts, both players and store kinds, fresh/warm/load/resume, inactive query materialization, locking, repeated full sync, and interleaved unchanged sync_strategy.
3. Snapshot/hash original device f32 arenas before and after optional readback and require exact identity. Continue GPU iterations afterward and compare control results. Require identical CPU full-state fingerprints, iteration, exploitability bits, and query results; retain F32, tight-budget fallback, and descriptor-failure coverage. Use existing saved-state/action-menu/resume, GPU library, and CPU/GPU suites.
4. Remove diagnostic instrumentation for qualification. Alternate immutable baseline/candidate binaries at least three repetitions each on the unchanged registered rainbow/two-tone/river suite. Score the sum of per-fixture median complete-cycle wall times. Runtime NVRTC/JIT, descriptor construction, scratch allocation, encoding, transfer, scatter, and restoration all remain included; Cargo compilation and correctness hashing stay outside.
5. Follow program.md: reproducible aggregate reduction >=2%, no repeatable material per-fixture regression >3%, exact arena fingerprints/exploitability bits at identical stopping iterations, and required controls before acceptance. Report component timing separately. Research validation is distinct from deployment; this design authorizes neither solver integration nor a live restart.

The likely first rejection modes are exactness at exceptional values, incorrect inactive/unused-state coverage, cold compile/allocation overhead exceeding savings, and extra VRAM reducing fit. Preserve rejected/invalid evidence instead of weakening the evaluator.
