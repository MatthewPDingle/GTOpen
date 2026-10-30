# D036 prepared probe R2 source supplement

PASS_SOURCE_ONLY. No remaining actionable source finding. R2 closes the sole resource-query coverage gap in the independently reviewed R1 probe. Compiler/GPU/resource/numerical results remain untested by this reviewer and parent-owned execution gates.

Prepared manifest SHA256 `c23945d7afbf1364931047f58b41dc2b5460d854d39225fb3cbd86d4e298be18`; probe.rs SHA256 `b22c6552a4dd0ff11c427a8199a9a098291086a5ee877a6deac81f0e02727e51`; R1-to-R2 patch `069de18433b67a85dffdd55f38602989399e29a8a29fa95e1c302e7c5f5b98c9`.

Independently verified the only executable-source change is one resource JSON field: `max_threads_per_block: f.max_threads_per_block()?`. The installed cudarc0.19.7 CudaFunction method at driver/safe/core.rs2427 exists without a CUDA-version cfg restriction, returns Result<i32>, and queries CU_FUNC_ATTRIBUTE_MAX_THREADS_PER_BLOCK. The error propagates through the existing Result path. No reinterpretation, cast or raw ABI call is introduced.

All R1 artifacts remain hash-identical. All R2 artifact hashes and pinned dependency rlibs match. CUDA baseline/candidate/raw kernels, corpus, protocol, numerical checks, runner and case ordering remain byte-identical to R1. Expected8 resource rows,1120 raw pairs,180 full pairs and370 launches do not change. R2 is a sibling artifact directory; run.py derives its working/output location from its own path, and REVISION-R2.md gives the R2 execution command. The original README command is historical R1 text and should not be used to launch R2.

The authoritative full-kernel oracle, signedzero/subnormal/finite-overflow exact-or-fail checks, guards, input immutability, resource interpretation and complete-cycle limits in comparisons/D036-probe-source-review remain applicable. No performance, accepted improvement, native time-share or universal float-domain claim follows from this source pass.

No script execution, compiler invocation, GPU call, production edit or live-server action was performed by this reviewer.
