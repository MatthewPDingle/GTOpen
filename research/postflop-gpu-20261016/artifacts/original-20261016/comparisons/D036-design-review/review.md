# D036 fold-shuffle independent design critique

PASS_DESIGN_ONLY: the bounded128x1x1 specialization is a reasonable standalone compiler/numerical probe. No actionable mathematical or synchronization blocker was found in the sealed design. Candidate implementation, compilation, numerical equality, resource usage and performance remain unverified. Accepted production source is E015; the three copied/current source hashes and all design checksums match.

The current128-thread tree combines64,32,16,8,4,2,1 with a full block barrier after each step. Retaining64/32 and their barriers leaves every tail operand in warp0. All32 lanes must load their current partial and participate in every full-mask shuffle before only lane<step adds. Nonparticipating lanes retain their prior v rather than adding zero. This produces the same left/right pair at every tail stage. Lane0 publishes total_parts[0]; a full block barrier outside the warp branch is required before any other warp reads T. The original reach/partial publication barriers remain. Four block barriers, not five, are removed.

The shape condition must be uniform and exactly128x1x1. Other supported1D shapes retain the original source loop. Do not generalize warp width, move shuffle inside lane<step, read T before the final block barrier, or change the initial per-thread strided accumulation/card sums. The existing whole-CTA b>=count return is uniform and therefore does not strand partial warps at a shuffle.

Same source operand pairing is necessary but not sufficient for a broad bitwise claim. Shuffle transfers bits; finite arithmetic, signed zeros and subnormals still depend on matching actual compiled additions. Accepted PTX visibly orders an add's registers differently from the source compound addition. NaN payload equivalence is not established by source algebra. Keep the production NVRTC architecture plus Default options unchanged: current host source supplies no explicit ftz/fmad/fast-math override. No wider precision, reassociation, artificial additions, or changed contraction setting belongs in this hypothesis.

## Required standalone proof

Use the complete actual accepted kernels.cu and candidate differing only in up_fold's reduction branch, loaded in separate modules under the same context/compiler/options. The authoritative result is raw full up_fold CFV output equality. A narrow copied/extracted partial-total kernel is supplementary: it exposes the intermediate total but cannot by itself establish full-kernel code generation or downstream arithmetic equality.

Freeze concrete serialized corpus/seed/card mappings and expected case counts before execution. Required opponent counts should include0,1,31,32,33,63,64,65,127,128,129,255,256,257,319,1326. Cover current128 plus original fallback16/32/64/256, comparing each candidate to baseline at the same shape. Never compare different block sizes as an exact oracle because the initial partial grouping changes.

Construct valid card lists in original hand order and exact same-combo mappings. Exercise both traversers, both fold-owner outcomes, asymmetric player counts, nonzero mixed-pot amounts, nontrivial reach/CFV slots, start/count offsets and extra out-of-range CTAs. Include output guard words/gap regions and bitwise input immutability. Keep a deliberate mismatch self-test that must fail. Zero-pot/all-zero-only cases cannot expose an incorrect total, so include nonzero outputs and correction cases whose total contribution remains visible.

The required finite corpus should cover positive/negative zero, minimum and larger subnormals, tiny+large mixtures, bounded random exponents, ordinary nonnegative reaches, rounding boundaries and finite cancellation, with required outputs finite. Preserve every input/output bit pattern. Any optional NaN/Inf or overflowing-finite cases must be separately labeled and retained; no silent tolerance comparison or later favorable case removal. A finite-domain proof does not establish NaN payload behavior.

Compile both complete sources and preserve exact NVRTC/DLL/toolchain/source/PTX identities. Inspect baseline/candidate up_fold barrier paths and floating operand roles, and verify unrelated kernel entries/source remain unchanged. Query registers, local spills, static/dynamic shared bytes, launch limits and occupancy at128 with actual and maximum opponent-hand dynamic shared sizes. Resource changes are feasibility evidence, not a speed estimate; an unchanged occupancy count does not prove the change useless.

## Integration and qualification limits

A successful probe only permits a bounded E019 candidate. Production edit scope can remain one CUDA kernel; host buffers, admission accounting, launches, traversal/graph ordering and signatures remain unchanged. Training and evaluation both dispatch up_fold and therefore both require exact testing. Existing frozen primary fixtures, raw/full-state fingerprints, stopping iterations and exploitability bits remain unchanged, with F32/compressed, menu/lock, saved-state/resume and pertinent continuation controls before acceptance.

Keep the existing complete-cycle boundaries and at least three alternating baseline/candidate repetitions against accepted E015, sum of fixture medians, reproducible>=2% aggregate improvement and repeatable>3% fixture-regression guard. Do not alter workloads or move setup outside timing. A barrier or isolated-kernel gain alone is insufficient. Preserve failed attempts and numerical/resource failures without favorable retries.

The dense D033 event totals do not justify native shares or a quantitative speed upper bound: its outer batches inflated about69-72%. The fold hypothesis is grounded in the concrete source synchronization pattern. The shared showdown-card-index cache is a distinct hypothesis and should not be combined.

No source edits, builds, GPU calls, profiler invocation or live server action were performed by this reviewer. Prepared standalone source/protocol will receive a fresh review before parent-owned execution.
