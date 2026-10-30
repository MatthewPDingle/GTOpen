# D033 R2 conditional-binding and ABI supplement

PASS_SOURCE_ONLY for frozen R2. No actionable finding remains in this one-identifier correction. Compilation and installed-driver execution remain parent-owned validation steps; no build or GPU call was performed by this reviewer.

R2 module SHA256 `10a0bc1f5836a63bb507e888af55e309245bfb4efe618700e8a9917827fa0c75`; full patch `03ee2b153fbe508e1bd27ef24fa94a393d04df2b96eaae9ff7233c8bf93d93a4`; incremental patch `7481149c021257dce8ec2e0791ef28bff269095630e80b1192539b18aa20408e`. mod.rs remains `981304658cfaa4b7feb5f03a102bfd3ab9dfcdf00f9be0de7db03bd14b365a54`.

Independently verified exact byte transformation: replace the sole `cuGraphKernelNodeGetParams(` with `cuGraphKernelNodeGetParams_v2(`. Current source equals the R2 archive. All R1/R2 archive checksums and eleven protected inputs remain valid. No workload, schedule, event placement, helper, comparison, arithmetic, ownership or cleanup change exists.

The first build's E0425 is a real missed conditional-binding issue in the R1 precompiler review. In cudarc0.19.7 driver/sys/mod.rs, lines10276-10292 expose the unversioned getter only for CUDA11 feature sets. Lines10293-10309 expose `_v2` for cuda-12060 and load that exact dynamic symbol. Lines318-324 select `CUDA_KERNEL_NODE_PARAMS = CUDA_KERNEL_NODE_PARAMS_v2` for the same feature. Lines5884-5900 define the repr(C) v2 layout, including trailing kern and ctx fields. The corrected function takes `*mut CUDA_KERNEL_NODE_PARAMS` directly, matching the existing zero-initialized variable: there is no cast, buffer-size assumption or v1/v2 reinterpretation.

NVIDIA's CUDA12.6.3 [v2 parameter reference](https://docs.nvidia.com/cuda/archive/12.6.3/cuda-driver-api/structCUDA__KERNEL__NODE__PARAMS__v2.html) corroborates the added kern/ctx members; these are ignored when func is set. E015 captured kernels originate from CUfunction launches. The diagnostic reads function/dimensions/shared-memory only and never modifies the returned arguments. The [graph API reference](https://docs.nvidia.com/cuda/archive/12.6.3/cuda-driver-api/group__CUDA__GRAPH.html) supplies the getter semantics; the exact Rust cfg/symbol selection is established from the installed dependency source.

This supplements `comparisons/D033-source-review`, preserving its historical source-only PASS and subsequent compiler failure. All numerical, runtime and interpretation limits in that review still apply. No native device-time-share, significance, causal speedup or acceptance claim is made.
