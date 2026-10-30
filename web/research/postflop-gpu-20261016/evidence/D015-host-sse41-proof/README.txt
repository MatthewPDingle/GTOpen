D015: host SSE4.1 encoder specialization proof

Hypothesis: allow SSE4.1 only inside runtime-guarded private host encoder wrappers. The specialized function body calls the original baseline::encode_i16/u16, byte-extracted from store.rs. No hand intrinsics, new maximum reduction, casts, quantizer math, fast-math, global CPU target, GPU work, or checkout edits.

Inputs and provenance
- baseline.rs, corpus.rs and corpus_constants.rs are byte-identical D014 copies. manifest.json records original full source hashes and byte ranges; source-store.rs and source-proof.rs preserve those complete original inputs.
- d014-prototype.rs, d014-run.py, d014-manifest.json and d014-report.json preserve the prior protocol and proof. D015 retains the exact corpus seed, extra random inputs, lengths, warmups, nine alternating pairs, input/output black-boxing, allocation exclusion and noinline public boundaries.
- candidate.rs contains target_feature(enable="sse4.1") wrappers and portable guarded dispatch. The CPU feature is checked before the proof and on each unsafe specialized invocation. Unsupported hosts exit with status 3 before proof/timing. Generic fallback source is present but not exercised by this supported-host run.
- Compile: rustc prototype.rs --edition=2021 -C opt-level=3 -C codegen-units=1 -C lto=thin --emit=link=prototype.exe,asm=prototype.s. This matches checked repository release settings and empty recorded solver rustflags. No target-cpu=native.

Observed validation
- 11,348 cases and 10,240,417 input values per type. Compared 20,480,834 q words, 22,696 scale bit patterns, 136,176 guard words; source float bits unchanged.
- Proof JSON exactly equals D014, including input/output/case hashes. Injected q-bit mismatch exits 101 before an exact-success record or any timing output.
- All 56 median timing groups improved. This is one standalone single-thread process, small reused blocks, with no affinity/power-state control. Each group has nine pairs; it is not a solver benchmark.

Median timing-group gains by mode (each range spans 14 block lengths)
- i16, finite: 53.4946% to 55.3432% reduction; median of group reductions 54.1841%.
- i16, positive_zero: 22.4045% to 26.8835% reduction; median of group reductions 25.2500%.
- u16, finite: 51.0868% to 54.0595% reduction; median of group reductions 51.9156%.
- u16, positive_zero: 27.6980% to 34.1384% reduction; median of group reductions 31.0602%.

Assembly evidence
- assembly-review.json and d015_*.asm.txt contain exact function excerpts. Each generic encoder has five static rintf call sites (four-element unroll plus scalar tail). Each specialized encoder has zero rintf sites, two roundps sites and one roundss site. Baseline maximum reduction already vectorizes; max4 is not included.

Integration handoff
- If pursued, add a private gpu/host_encode.rs dispatcher that wraps unchanged store::encode_i16/u16 under the feature attribute. Detect SSE4.1 before every unsafe call or once before selecting a reusable function pointer. Non-x86 and unsupported x86 use original Store::write_f32. Do not alter process-wide MXCSR, target CPU or shared CPU CFR paths.
- Route full write_arena and compact active/inactive host writes through the existing disjoint Store q/scale slices. Preserve per-node ownership, scale indices, compact inactive restoration, F32 copies, uploads, device state and current Rayon partitioning. Any strategy-only host write sharing these helpers needs explicit coverage.
- Require exact store q+scale bit comparisons for full/compact, cold/warm, inactive materialization, locks and repeat synchronization; unsupported/forced generic dispatch tests; unchanged device f32 images; existing CPU/server suites and serialized GPU equivalence.
- Then compare paired complete cycles against frozen E004 with exact fingerprints/exploit bits and all registered fixtures. Do not infer acceptance from these component timings. D009 CPU stage includes encoding, scatter, and inactive restoration, so applying this percentage to the entire stage would overstate predicted savings.

Reproduction and preservation
- Completed source, report, stdout, executable and assembly are frozen. run.py refuses to overwrite report.json. To repeat, copy its source inputs/scripts/manifest and d014-report.json to a new evidence directory, then run python run.py there; the script revalidates original source byte ranges. Keep the original evidence intact.
- commands.json records actual commands, UTC start times, elapsed seconds and exit codes. Final checksums are in checksums.json. No standalone result is an accepted/deployed solver gain.
