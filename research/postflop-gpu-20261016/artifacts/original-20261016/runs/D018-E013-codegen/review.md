# D018 E013 library code generation

Source review passed: only the private GPU host-encoding module changed from D017/E012. The cfg/runtime gate and portable fallback are unchanged; the SSE writer now obtains the same disjoint destination slice and calls a private, typed, target_feature(sse4.1), inline(never) function delegating the original encoder. Original Store code, math, tests and lifecycle call sites are unchanged.

The sole authorized cargo rustc --release -p solver --features gpu --lib -- --emit=asm command completed successfully in 55.046 seconds. All 109 input hashes match before and after. Only host_encode.rs differs from D017. No tests, GPU calls, or benchmark binaries were run; frozen E012 binaries/manifests were not touched.

| Function | rintf call sites | roundps sites | roundss sites |
| --- | ---: | ---: | ---: |
| E013 SSE writer | 0 | 0 | 0 |
| E013 typed I16 encoder | 0 | 0 | 1 |
| E013 typed U16 encoder | 0 | 0 | 1 |
| Portable Store::write_f32 | 2 | 0 | 0 |

The writer calls the two distinct typed encoder symbols, confirming the no-inline boundary survived. The typed encoder loops remain scalar in this library assembly; packed rounding was **not demonstrated**. The portable function extract is byte-for-byte identical to D017 (SHA256 c869e1d2271d131988115009499f84a6b6d75db19d8c723e2abc73669d73a8d5). No rintf calls remain in the specialized encoder chain.

The compiler-only hypothesis has not obtained its expected evidence at the requested library-assembly stage. This source adds a per-block function call, and no vectorized loop is visible here. Complete assembly (27,914,451 bytes), extracts, source manifests and command logs are retained; assembly-review.json records symbols, exact line positions and hashes.

## Important stage limitation

D017 and D018 are **library** assembly outputs. D015 was a standalone executable built with thin LTO. Final executable link-time optimization can differ from this library artifact; therefore neither D017 nor D018 alone proves the exact instruction sequence in a frozen benchmark executable. The robust conclusion is 'no packed loop demonstrated in the requested library artifact', not 'final executable vectorization conclusively failed'. Confirm the final executable or its post-LTO assembly before treating vectorization absence as the established explanation for E012 timing. This limitation also narrows D017's earlier interpretation.

No additional compilation or disassembly attempt was performed. No objdump/dumpbin tool was available on PATH when checked. Whether to proceed to executable codegen inspection or abandon E013 remains with the root coordinator; this diagnostic records no performance acceptance or rejection.
