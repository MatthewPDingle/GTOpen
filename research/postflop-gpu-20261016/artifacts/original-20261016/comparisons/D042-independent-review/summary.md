# D042 independent diagnostic review

**PASS_SCOPED_DIAGNOSTIC.** All six fixed runs completed in the prescribed order from the correct immutable executables. All18 complete non-timing results and138 convergence checks match. All36 instrumentation markers (12 per instrumented run, none in ordinary runs) have the expected fixture/player/store order, positive-zero outcome, one predicate call and no extra CUDA synchronization. Quantized/scalar counts match the full-state arena descriptors; all timings are finite and nonnegative.

The independent ordinary/instrumented sum of fixture medians is **9736.4349 / 9787.7434ms**, a **+0.5269742%** outer change. This passes the prespecified absolute10% usefulness guard. All pairs and fixtures remain reported; no sample exclusion or extension occurred.

Each table entry sums both players per run, then takes the median of the three instrumented runs. Units are milliseconds.

| Fixture | I16 predicate | U16 predicate | I16 alloc/submit | U16 alloc/submit | I16 existing wait | U16 existing wait |
|---|---:|---:|---:|---:|---:|---:|
| rainbow | 88.6886 | 88.4903 | 10.9333 | 3.4195 | 17.6162 | 16.1080 |
| two-tone | 30.5843 | 61.6945 | 2.2816 | 2.1513 | 10.9978 | 10.1463 |
| river | 0.0023 | 0.0014 | 0.1311 | 0.0374 | 0.8430 | 0.0778 |

The sum of U16 predicate fixture medians is **150.1862ms**, **1.5425174%** of the ordinary total. It includes scale scanning and existing snapshot checks, so it upper-bounds only the measured direct U16 quantized-word scan span. Even deleting that entire observed span is below the2% primary threshold (194.7287ms). It does **not** bound cache effects or the complete-cycle result of a hypothetical implementation. The10% outer guard does not remove component bias. Allocation spans include host allocation/submission, and existing waits are not isolated GPU durations.

Fresh Cargo terminal/artifact identities, linked accepted CUDA plus diagnostic marker, authorization/review/script pins and raw report/log provenance verified. The complete162-entry source map matched the frozen D042 build before cleanup, with only arena.rs instrumented relative to E020. Root was notified that the owned instrumentation may be restored. The original predicate, evaluator and CUDA arithmetic remain unchanged.

No speed optimization is accepted, and no2% headroom is established by this diagnostic. Review used file reads and additive audit artifacts only: no build, native rerun, GPU work or checkout mutation. The independent audit passed its first execution.
