# Terminal sample-loop partial unrolling

Two independent source-only candidates: apply unroll-2.patch OR unroll-4.patch to the shared pf_multiway_sum local/sample_count loop. There is currently no loop pragma. Each affects preferred and pending minimal entries through the same helper. Test2 first, then separately4; do not layer pragmas or combine with inclusive CDF storage.

The recurrence `sum += share` remains a single sequential accumulator, preserving source arithmetic order. No second accumulator, vector reduction, fast-math flag, layout, sample count, or batch change. The compiler can overlap independent next-sample CDF loads with current sample arithmetic. This is only an ILP hypothesis: NVRTC may already unroll, may decline runtime unrolling, or may increase live registers and spills. Examine generated PTX/register allocation as well as timing. Compiler-produced f32 bits, not source intent alone, are the correctness gate.

Run existing every-O2..8 exact terminal bits at identical batch metadata, plus odd counts23/31 and partial counts1/7 to exercise unrolled remainder handling. Run preferred/minimal, direct/normalized, compact/union, gated zero-reach poison, graph replay, and whole-arena controls. Require exact old/new outputs at each same batch and no material end-to-end regression. Retain sequential sample accumulation; reject any compiler change causing bit differences. Benchmark paired independent processes; report CDF unchanged, terminal and end-to-end phases separately.

Prepared only: no compile, hardware job, or active source edit.
