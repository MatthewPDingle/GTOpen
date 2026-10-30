# D012: outer GPU constructor diagnostic

Artifact only; not applied. Base is the preserved E010 source at ../E010-source/mod.rs, SHA256 81f60658d7b9087b7c003499fc32a553c8cf0f9a11239087edcc5e23d7a316cc. Only gpu/mod.rs is patched. No kernel, allocation policy, numeric path, evaluator, or readback changes.

## Why this diagnostic

D011 measured river QuantizedReadback::try_new at 0.1468 ms, including signed/unsigned function-load calls totaling 0.0600 ms, while outer GPU initialization was 167.7424 ms. The proposed expensive optional-function-loading explanation is ruled out for that run. Rainbow/two-tone optional setup was 26.1699/15.7886 ms. Source: ../D011/stdout.log, hashed in manifest.json. These are diagnostic observations, not accepted performance gains.

The remaining river cost must be located in the enclosing initialization path or measurement boundary. D012 separates context/stream setup, PTX acquisition/compilation, module loading, pinned staging, layouts/uploads, base metadata/function/buffer work, optional quantized setup, and final return. An effect of the larger PTX/module earlier in initialization remains possible; D011 did not measure it. No further optimization is justified until this trace locates the excess.

## Output and scope

Enable POSTFLOP_AUTORESEARCH_CONSTRUCTOR_PROFILE=1. Every successfully completed new_with_budget emits one best-effort locked stderr JSON line prefixed GPU_CONSTRUCTOR_PROFILE. The record explicitly includes this custom flag, requested CUDA_MODULE_LOADING (null means unset, not queried driver mode), node/arena sizes, and whether quantized readback was selected. Preserve raw stderr because the runner's usual environment metadata does not include the custom flag.

Ordered spans:
1. plan_and_budget_cpu
2. context_create_host_call
3. stream_create_host_call_with_existing_context_wait
4. context_configuration_and_device_info_host_calls
5. ptx_acquire_or_compile_cpu
6. module_load_host_call
7. pinned_staging_allocation_host_call
8. arena_layouts_cpu
9. arena_upload_calls_with_existing_waits
10. locks_log_and_fold_tables_cpu
11. function_lookup_metadata_upload_and_basebuffers_host_calls
12. quantized_readback_try_new_with_existing_waits
13. final_return_cpu

Spans are finite host wall times. Host calls can block or submit asynchronous work; they are not isolated device durations. The optional setup span includes its existing stream waits, which can drain earlier base work. The base-buffer span measures host calls without adding a wait. cudarc 0.19.7 new_stream already performs a context synchronization when creating the first stream while event tracking is enabled; stream creation is separated from context creation to distinguish that existing wait. No new context wait is added. The existing original gpu: stdout message remains included in the locks/log/fold-table span.

The trace covers initialization only. It does not instrument caller synchronization, iteration, readback, destructor work, or the whole benchmark. Logging happens after the recorded total, but is included in the enclosing benchmark initialization time. Constructor errors propagate unchanged and emit no completed trace; use the original error output for failures.

With the flag absent there is one environment lookup, no clock reads, no span allocation, and no trace output. Enabled success adds 13 marks, approximately 15 clock reads, one small reserved vector, one JSON serialization and stderr write. Logging can block; no measured overhead bound is claimed. All diagnostic runs are excluded from performance qualification.

## Apply after reverting D011

From X:\Dev\GTOpen-gpu-research-20261016:

1. Reverse the already-preserved D011 patch after checking it, then verify quantized_readback.rs returns to SHA256 9ed3b74710399f921a7fd4a648ed30304d6f5c983970f42c57a138e11d7e3038. Verify mod.rs has the base hash above. D012 is intended to run alone on E010.
2. Remove the D011 environment flag and check/apply D012:

       Remove-Item Env:POSTFLOP_AUTORESEARCH_QUANTIZED_INIT_PROFILE -ErrorAction SilentlyContinue
       git apply --check S:/GTOpen-research/postflop-gpu-20261016/runs/D012-design/constructor-init-diagnostic.patch
       git apply S:/GTOpen-research/postflop-gpu-20261016/runs/D012-design/constructor-init-diagnostic.patch

3. Root freezes/hashes the diagnostic source, builds separately, and runs the unchanged serialized suite with:

       $env:POSTFLOP_AUTORESEARCH_CONSTRUCTOR_PROFILE = '1'

4. Preserve source/binary hashes, the flag, raw logs and exact fingerprints. Do not change CUDA_MODULE_LOADING, compiler options, workload order, or cache policy during this diagnostic.

## Remove

Verify mod.rs still has candidate_sha256 in manifest.json. Reverse-check then reverse-apply this exact patch. If it drifted, inspect rather than overwrite.

    git apply --reverse --check S:/GTOpen-research/postflop-gpu-20261016/runs/D012-design/constructor-init-diagnostic.patch
    git apply --reverse S:/GTOpen-research/postflop-gpu-20261016/runs/D012-design/constructor-init-diagnostic.patch
    Remove-Item Env:POSTFLOP_AUTORESEARCH_CONSTRUCTOR_PROFILE -ErrorAction SilentlyContinue

Verify the preserved E010 base hash again. Rebuild without diagnostic instrumentation for subsequent qualifying comparisons.

Source validation requires byte-identical recovery of the original file after stripping only the inserted helper/timer statements; equal CUDA call/wait counts; an exactly unchanged suffix after the constructor; syntax-only parsing; and patch applicability. No build, GPU execution, or repository mutation was performed while preparing this artifact.
