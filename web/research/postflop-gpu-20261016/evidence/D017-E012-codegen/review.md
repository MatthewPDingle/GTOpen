# D017 E012 integrated code generation

Compilation-only diagnostic; no executable, test, or GPU launch. The sole authorized command completed successfully in 50.86 seconds. All 109 recorded source/input hashes match before and after. Command/environment and logs are saved alongside this note. Frozen benchmark binaries/manifests were not touched.

| Function | rintf call sites | roundps sites | roundss sites |
| --- | ---: | ---: | ---: |
| Integrated host_encode::write_sse41 | 0 | 0 | 2 |
| Integrated portable Store::write_f32 | 2 | 0 | 0 |
| D015 standalone SSE encoder, each type | 0 | 2 | 1 |

The integrated feature helper successfully inlines both original encoders and eliminates the per-element rounding-library call. It does **not** reproduce D015's vectorized quantization. Each I16/U16 quantization loop loads one float, multiplies, rounds with roundss, saturates/converts, writes one 16-bit word, then increments its element index. Its max reductions are scalar too. There is no hidden call to a baseline encoder.

Both compact and full arena paths visibly read the CPU-feature cache, select the SSE4.1 or portable function pointer, and pass the selected pointer into Rayon. Selection remains outside the per-node work. This rules out a missing runtime-dispatch branch as the source explanation; it does not independently establish which path the prior process actually executed, although runtime dispatch tests cover the host.

Source assembly locations: SSE helper 864779-864962; portable helper 584699-584923; compact/full dispatch excerpts 532180-532212 and 532244-532278. Function extracts and the entire 27,913,056-byte generated assembly are preserved. `assembly-review.json` records their hashes and exact counts.

Interpretation: D015's isolated speedups cannot be directly projected onto E012 because integrated code generation differs. This diagnostic alone does not explain all of the weak readback improvement or measure the cost of the function-pointer boundary, scheduling, memory access, or transfer.

Optional subsequent hypothesis, not implemented here: separate private target_feature SSE4.1 encoder functions with typed &[f32]/&mut [i16 or u16] arguments and an explicit no-inline boundary could recreate D015's optimizer-visible slice disjointness. The current Store/raw-arena boundary possibly suppresses vectorization; that is an inference, not a proven cause. Verify its assembly before spending another GPU timing cohort. Keep original arithmetic/encoders, runtime gating and portable fallback.
