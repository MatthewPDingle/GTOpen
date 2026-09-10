# Frozen module/function resource inspection

`preflop_module_resources.rs` adapts the previous coupled-terminal resource inspection into a standalone example. Proposal only: not compiled or run by the proposing agent. It launches **zero kernels**, allocates **zero solver arrays**, and does not load a game, calibration fit or equity cache.

Usage after the frozen convergence queue:

```
preflop_module_resources LABEL
```

Compile the identical example twice: once with literal `1b8fc3f:crates/solver/src/preflop/kernels.cu`, once with the final optimized kernels. The harness uses include_str on that source and the solver's exact NVRTC options (detected compute capability, other CompileOptions default). Source changes are embedded at Rust compile time; swapping a `.cu` beside an already-built executable will not change it. Keep separate frozen executable paths and archive SHA256 hashes of the harness, literal CUDA source, executable and logs.

## Collected observations

- CUDA device-global free/total/used bytes after primary context creation.
- Snapshot after NVRTC compilation, before loading the PTX module.
- Snapshot after module loading.
- For every function, one snapshot immediately after function loading and another after attribute/occupancy inspection.
- Snapshot after all functions, then after dropping function handles and module.
- Register count, local bytes per thread, static shared memory, constant memory, maximum threads, PTX version, binary version, and occupancy upper-bound queries at128/192/256threads with zero dynamic shared memory.
- Timings of context creation, compilation, module/function load and attribute inspection. These are diagnostic stage timings, not kernel throughput.
- Architecture, multiprocessor count, warp size, maximum threads perSM, async-allocation support, source/PTX FNV fingerprints, and relevant CUDA loading/cache/JIT environment settings.

Snapshot calls synchronize the context to keep observations ordered, but do not enqueue kernels. The function attribute APIs and occupancy query likewise do not execute the inspected kernel. Missing optional optimized-only functions are logged as absent; a missing common function or failed compile/module load fails explicitly and retains earlier log output.

Functions inspected in fixed order:

1. Common six-seat constructor prefix: pf_init_root, pf_down, pf_terminal_6, pf_reach_mass, pf_equities, pf_multiway_cdf, pf_multiway_terminal, pf_up, pf_discount_nodes.
2. Remaining shared terminal specializations: pf_terminal, pf_terminal_2, pf_terminal_8.
3. Optimized-only helpers when present: pf_multiway_cdf_direct, pf_multiway_normalize, pf_multiway_clear_active, pf_multiway_prepare.

All function handles are retained until after the final snapshot, as in the solver. Common functions are inspected before optimized-only helpers so a helper absent in original cannot contaminate the common prefix. This is a controlled shared load order, not a promise to replay the optimized constructor's precise order. The first pf_terminal_6 observation corresponds to the actual modeled six-seat selection. Generic and other terminal variants are additional diagnostics and should be interpreted at their later stage.

## Paired protocol

Use separate sequential processes on the same device. Start only after the parent's frozen GPU queue is complete; do not run alongside its solves. Keep CUDA_MODULE_LOADING and other listed environment settings identical across the pair. Do not force eager loading, alter JIT flags or disable caches in just one candidate. The first comparison should preserve the benchmark environment; an explicit EAGER/LAZY experiment, if later useful, is a distinct pair and must use the same setting for both sources.

Suggested bounded sequence is original, optimized, original, with labels that distinguish repeats. Each run only compiles/loads/inspects the small module. Do not interpret a warm disk-JIT-cache timing advantage as execution speed. Extra processes elsewhere can change device-global free memory; record the parent guard's usual state and treat unstable baselines as inconclusive.

The diagnostic starts with a new primary-context reference and reports its initial device-used value; it cannot report memory before CUDA initialization through mem_get_info. Subtract that within-run baseline when comparing stage deltas. The final context itself is still alive during the module-drop snapshot.

## Interpretation limits

The source audit found original-constructor driver usage about1.12GB above its planned buffers, whereas optimized compatibility controls matched planning within8MB. This harness asks whether some of that difference appears during module/function loading **before solver array allocation**.

If a difference appears at a load/attribute stage, that localizes when it becomes visible; register/local/shared attributes do not independently prove the allocation's cause. In particular, local_size_bytes is a compiled per-thread property, not measured global backing/residency. Do not multiply it by guessed concurrency and call that the missing allocation. Higher register usage alone is not a VRAM allocation measurement.

If the difference is absent, that does not refute the original constructor snapshots: it may arise during large buffer allocation, later lazy loading, allocator pool reservation or first execution. This harness deliberately has no CDF allocation, kernel launch or graph capture, so it cannot discriminate those stages. It does not measure WDDM budget, page migration, eviction or paging and should not be cited as proof of any of them.

## Integration

`add-module-resources.patch` adds only this example and a gpu-required Cargo example entry. No production source changes. APIs were checked against installed cudarc0.19.7 source. The parent must compile and verify the harness after the current queue; the proposing agent ran only the text-generation script.
