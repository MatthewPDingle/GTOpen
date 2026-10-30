# D011: quantized constructor diagnostic (not applied)

This artifact targets the preserved E010 quantized_readback.rs only. It does not modify the repository, kernel arithmetic, device layout, readback, tests, benchmark, or live server. Root may apply it after timing is complete and source is frozen.

## Hypothesis

The persistent roughly 100 ms river initialization penalty after removal of the extra pinned allocations suggests fixed setup cost. The two module.load_function calls are the leading source-based suspect: cudarc 0.19.7 maps them directly to cuModuleGetFunction, where deferred CUDA loading can occur. This is a hypothesis, not a measurement of those calls. NVIDIA reference: https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/lazy-loading.html .

Other candidates are optional device allocation/driver work, the existing pre-prepare wait draining earlier base setup, and context/module work before try_new. E010 no longer allocates pinned buffers here, and its first-use zeroing is in readback rather than initialization. River has only 33 tree nodes, so about 100 ms of CPU descriptor construction would be surprising and should be measured before changing it.

D009's earlier baseline river trace measured context/stream/device-info host calls at 91.2218 ms, module load at 1.5146 ms, and final function lookup/metadata/workbuffer submission at 0.8075 ms. Those older diagnostic numbers do not locate the E010 excess. If this patch's entire quantized_try_new trace is small while outer initialization remains slow, instrument the enclosing context/PTX/module/base-constructor stages next. Do not attribute the difference to quantization merely because it appears in the same benchmark.

## Trace and interpretation

Enable only for an isolated diagnostic run:

    $env:POSTFLOP_AUTORESEARCH_QUANTIZED_INIT_PROFILE = '1'

The flag is off by default. Each completed try_new call emits one best-effort JSON stderr line prefixed QUANTIZED_INIT_PROFILE. The record explicitly includes the enabling flag and requested CUDA_MODULE_LOADING environment value; null means unset, not a verified driver loading mode. The runner's standard environment block may omit this custom flag, so retain raw stderr and the diagnostic manifest.

The single trace covers eligibility; per-player descriptor building; staging-capacity/budget checks; existing pre-prepare stream wait; signed and unsigned function-load calls separately; words and scales allocation calls separately; descriptor allocations per player; CPU upload-vector preparation; descriptor upload host calls; and the existing per-player completion waits. Fallback cleanup wait is marked only on that existing path. Error exits retain their elapsed tail and outcome=error.

All reported times are finite host wall durations. Host-call spans can include driver blocking or asynchronous submission and must not be labeled completed GPU work. An existing stream-wait span may include earlier pending base work. No CUDA events, new synchronization, mode queries, cache changes, or warmups are introduced. Both successful and failed submissions keep their original completion/error order. Best-effort locked stderr writes ignore I/O errors and do not add an output panic path.

The typical selected two-player path has 18 marks, about 20 host clock reads, one small reserved span vector, one JSON serialization, and one stderr write. Disabled mode performs one environment lookup and no clock reads, trace allocation, or output. Logging can block; no numerical overhead estimate is claimed. Constructor totals include diagnostic disturbance, so these runs are excluded from performance qualification. Do not switch CUDA_MODULE_LOADING during this diagnostic.

## Application and removal

1. Verify the repository target SHA256 is 9ed3b74710399f921a7fd4a648ed30304d6f5c983970f42c57a138e11d7e3038 and retain the immutable E010 source/evidence.
2. From X:\Dev\GTOpen-gpu-research-20261016, check then apply the patch:

       git apply --check S:/GTOpen-research/postflop-gpu-20261016/runs/D011-design/quantized-init-diagnostic.patch
       git apply S:/GTOpen-research/postflop-gpu-20261016/runs/D011-design/quantized-init-diagnostic.patch

3. Root freezes/hashes sources, builds a separate diagnostic binary, enables the custom flag, and runs the unchanged suite with GPU serialization. Preserve the binary hash, exact flag, logs, and fingerprints. This handoff did not build or run anything.
4. Before removal, verify the repository target still equals candidate_sha256 in manifest.json. Then reverse-check and reverse-apply this exact patch; if it drifted, review the difference instead of overwriting it:

       git apply --reverse --check S:/GTOpen-research/postflop-gpu-20261016/runs/D011-design/quantized-init-diagnostic.patch
       git apply --reverse S:/GTOpen-research/postflop-gpu-20261016/runs/D011-design/quantized-init-diagnostic.patch
       Remove-Item Env:POSTFLOP_AUTORESEARCH_QUANTIZED_INIT_PROFILE -ErrorAction SilentlyContinue

5. Confirm the target hash returned to the preserved E010 base before subsequent candidate edits. Rebuild without the diagnostic patch for qualifying comparisons.

Source construction verified equal counts of all existing CUDA wait/allocation/copy/function-load/launch call sites and byte-identical download/tests suffix. Syntax-only parsing and patch applicability are recorded in manifest.json. These checks are not compilation, execution, or a performance result.
