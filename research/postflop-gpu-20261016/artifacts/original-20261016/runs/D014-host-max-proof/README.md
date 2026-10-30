# D014: four-lane host maximum reduction

**Decision: rejected as an integration candidate after the CPU screen.** Exact output checks passed, but the proposed max loop was slower at all four registered block lengths. This is a standalone CPU diagnostic, not an end-to-end solver performance result. No checkout source, CUDA code, GPU state, or live application was changed.

## Preserved evidence

- `report.json`: exact-check counts/hashes, all 56 timing groups and nine alternating pairs per group, command records, provenance, and artifact hashes. Its `diagnostic_pass` means the diagnostic executed and exactness checks passed; the separate candidate decision is rejection.
- `decision.json`: explicit rejection and scope.
- `stdout.jsonl`, `stderr.log`: complete execution output.
- `injected-failure.*.log`: deliberate q-word corruption caused exit 101 before any proof-success or timing record.
- `manifest.json`: exact source byte ranges, SHA256 hashes, compiler identity, flags, and checkout revision.
- `assembly-review.json`, `d014_*.asm.txt`: compiler observations and complete function excerpts. All original Thin LTO `.s` outputs remain preserved.
- `prototype.exe`, `prototype.rs`, `candidate.rs`, `baseline.rs`, `corpus.rs`, `corpus_constants.rs`, `prepare.py`, `run.py`: executable and reproducible source/tooling. Do not rerun preparation over this frozen evidence directory; reproduce into a fresh directory.

The unchanged production `store.rs` SHA256 is `ff329f9c6dd48dd746b567104f9b67bf980889b8c640c01e87bc0dcf336c4eb7`. `baseline.rs` is its exact byte range `[5404, 6773)`, containing both encoders and both quantizers. The candidate only regroups maximum selection into four independent lanes, combines them, and processes the tail. It calls those same original quantizers.

## Exactness screen

11,348 cases per type contain 10,240,417 inputs per type. Checks compared **20,480,834 q words and 22,696 scale bit patterns**, checked **136,176 guard words**, and verified unchanged input bits. The corpus contains all 2,212 original D010 cases plus explicit lane/tail placement and 4,096 additional seeded raw-bit cases. It covers empty arrays, positive/negative zero, finite extrema, infinities, quiet/signaling NaNs, subnormals, reciprocal overflow, rounding ties and adjacent floats, random inputs, and long tails. Seed: `5eed20261016f00d`; case manifest FNV64 `cda1aae5f0ee1ffd`; input FNV64 `b99895a395c3727c`; output FNV64 `6404e82b1faee180`.

The source argument is that positive-zero-seeded maximum selection ignores NaNs and preserves the same positive finite maximum or infinity under regrouping. I16 uses absolute values. A possible U16 zero-sign tie is normalized by the unchanged nonpositive-max quantizer branch. Multiplication, division, rounding, casts, saturation, and invalid-max behavior are unchanged. Independent source critics found no arithmetic defect. This finite corpus is substantial evidence, not exhaustive enumeration or a formal proof; floating-point status flags are not part of the tested output contract.

## CPU timing screen

Compile flags match the release optimization profile: `--edition=2021 -C opt-level=3 -C codegen-units=1 -C lto=thin`, using rustc 1.98.1 / LLVM 22.1.8 on `x86_64-pc-windows-msvc`. No native-target or fast-math flag was supplied. `commands.json` preserves exact commands and timestamps.

The benchmark uses `black_box`, equal non-inlined call boundaries, warmups, reusable destination buffers, eight input blocks, and nine pairs with alternating baseline/candidate order. Fourteen lengths cover hundreds of hands times two to four actions, including registered lengths **514, 638, 771, 957**. Finite I16 data includes both signs; finite U16 data is nonnegative. Positive-zero blocks are measured separately.

At those four registered lengths, candidate median time was **4.50–5.89% slower for finite I16**, **0.37–1.68% slower for finite U16**, **14.82–22.00% slower for zero I16**, and **9.70–13.47% slower for zero U16**. Preserve raw ranges/pairs; these single-process microbenchmark results are not statistical proof of production regression. There is no promising measured gain warranting solver integration.

The original source already compiles to two SSE `maxps` accumulators over eight values per max-loop iteration. The manual four-lane source is further vectorized over 32 values with deinterleaving and spills: the maximum loop grows from 23 to 126 static instructions for I16 and 21 to 119 for U16, with eight stack-access instructions in each candidate loop versus none in the original. Stack allocation grows from 184 to 264 bytes. These are static observations, not equal-work instruction ratios. Both variants retain five static `rintf` call sites in the unchanged rounding stage (four unrolled, one tail).

Limitations: one process, hot small input blocks, one CPU thread, no affinity/power-state controls, no Rayon scaling, no GPU/complete-cycle measurement. Allocation/layout and full solver performance were not tested. No additional timing runs were performed after this rejection.

## Executed commands

From this artifact directory:

```text
python prepare.py
rustc prototype.rs --edition=2021 -C opt-level=3 -C codegen-units=1 -C lto=thin --emit=link=prototype.exe,asm=prototype.s
prototype.exe --inject-failure --proof-only
prototype.exe
```

`run.py` issued the last three commands and captured all output. Thin LTO emitted multiple assembly files, so rustc warned that the requested single `.s` path was ignored; `prototype.prototype.1ab0bb7343479e38-cgu.0.rcgu.s` contains the inspected functions.
