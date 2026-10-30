# D036 prepared probe independent source review (R1)

PASS_SOURCE_AND_CORPUS_ONLY for the frozen R1 probe, with one disclosed resource-query coverage gap: max_threads_per_block was promised by the design critique but is not emitted yet. Root is preparing an additive R2 single-field correction before execution. No mathematical, guard, launch-argument or runner control-flow blocker was found. This record does not assert compilation, GPU execution, numerical equivalence, resource sufficiency or performance.

Prepared manifest SHA256 aa00b819764e2693d5c37c63f0c668308851b249d130274b6ad567d325ebadfa. Candidate CUDA SHA2569eff0e598c69bafcf4dc8a04ad116bd25482b06bd9bde34c143d45688ab5505a. Every sealed artifact, two pinned dependency rlibs and five protected checkout inputs were independently hashed. Host-only checks reconstructed card lists, same-hand maps, uniqueness, input bounds, disjoint CFV ownership, finite input classification and case/word counts. No preparation/execution script was run.

## Checks

The complete accepted baseline CUDA matches E015. Candidate bytes before and after up_fold are unchanged. The sole body change implements exactly the reviewed128x1x1 tail: shared64/32 reductions retain block barriers; all32 warp0 lanes shuffle before guarded additions; lane0 publishes before a full block barrier. Fallback loop is unchanged except indentation. The raw supplemental partial/reduction bodies are exact substrings of their corresponding full kernels.

Full-kernel CUDA arguments match all21 accepted up_fold parameters in order and type. Separate baseline/candidate modules share the same context/options and each pair uses the same block shape. Resource calls use existing cudarc0.19.7 APIs; occupancy method signature matches128/u32, dynamic bytes/usize, optional flags. NVRTC options are architecture only, matching the production default-options construction. Root must still compiler-check Rust and CUDA.

Corpus contains224 raw cases and17 full scenarios. The independent count is1120 raw pairs (1040 finite-domain CPU-oracle pairs),170 ordinary full pairs plus10 zero-count pairs, and370 CUDA launches. Full active output counts per variant are1,771,280 total and1,644,760 required-finite words. All serialized inputs are finite; the overflow domain remains exact-or-fail for every observed GPU bit. CPU same-tree totals supplement rather than replace actual full-kernel GPU baseline authority. No NaN/Inf input guarantee is asserted.

Opponent/own hands are unique legal two-card combinations. Card lists preserve opponent hand order; same_p maps exact hand identities. The physical reach/CFV slot permutations, start2, excess CTAs, zero-count and zero-own-hand cases are bounded and coherent. Both traversers and both owner/payout outcomes execute; asymmetric257/319 counts, signed zeros, subnormals, finite cancellation and nonzero outputs are covered.

Both raw output images are written before comparison. Unwritten guards/gaps/tails and all device input buffers are checked after each variant, preventing unnoticed baseline input mutation from contaminating candidate results. Every active output bit must match, including overflow-derived nonfinite results. Required-finite outputs must remain finite. Required output changes/nonzero results prevent an all-stale/all-zero proof. Fabricated expected-bit and guard mismatches exercise verifier failure paths without being counted as GPU numerical cases.

The runner freezes inputs before and inside the shared GPU/build lock, requires available storage, refuses live solves and verifies again before/after execution. It writes unique evidence files, has fixed600-second stage deadlines and cleans the owned child on exceptions while the lock remains held. No live solve mutation or profiler invocation occurs. Hashes/commands/raw logs/outputs/PTX/resource rows remain preserved; there is no retry or performance-measurement path. The script computes unrelated entry PTX equality for independent audit; it does not silently treat that field as a speed result.

## Coverage gap and limits

Add only max_threads_per_block to resource rows via R2, using CudaFunction::max_threads_per_block() -> Result<i32>, verified at installed core.rs2427. Preserve R1 and its manifest; corpus, candidate, schedule and expected stage counts need not change. A failed resource query must fail the probe. The actual128 and fallback256 launches also remain runtime legality checks.

The fixed corpus is substantial finite-domain evidence, not a proof over all floats or all solver states. Optional overflow outputs still require exact GPU bits and cannot be excluded after failure. Full solver lifecycle, storage/menu/lock/resume/continuation checks and frozen complete-cycle performance qualification remain separate. Static PTX/barrier counts and occupancy are not timings or native device shares.

No source edit, build, GPU call or live server action was performed by the reviewer. The accepted checkout remains E015.
