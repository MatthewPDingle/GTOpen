# D17: actual learning scan-tile occupancy

Registered before extracting masks or computing intersections. D16's
distribution-independent interval is too wide to admit a GPU prototype. Now
measure actual empty tiles; this is a new information source, not a retuned
lower-bound test. The proposed learning-only writer is unchanged. The original
accuracy-check writer remains selected; no runtime candidate is added here.

Extend the ignored, read-only D10 test with an optional separate witness of
the 169-bit nonzero mask for each newly interned learning distribution, in
identity order. Keep exact bitwise interning and original GPU normalization.
The original D10 identity/terminal witness must be byte-identical, original
JSON must match, and learning arenas/iteration must remain unchanged on both
immutable saves. Build/unit test cap300 seconds; each extraction cap180.

Use D13's verified fixed 1024x169 class order. Partition each sample into
32,32,32,32,32,9 classes, represented as six 169-bit masks. For every distinct
learning distribution count empty intersections across all 6144 tiles. Weight
by its actual per-traverser identity occurrence, not active terminal slots or
globally deduplicated support masks. Aggregate equal support masks only as a
host census acceleration, preserving multiplicity. Reconcile support counts
and unique row counts with D10/D11 and fall within D16's interval.

Two independent methods: NumPy three-word uint64 intersections and Python
arbitrary-precision integer intersections over unique tile masks, both weighted
by multiplicity. Verify every individual pattern's result, all per-seat totals,
no extra high bits, full ID coverage and all per-sample rank permutations.
Host census cap180 seconds. Preserve hashes of protocol, source, executable,
saves, old/new witnesses and rank data. No new benchmark or solver advancement.

Admit a separately registered exact-zero GPU prototype only if actual large
learning empty-tile fraction >=20%. Otherwise reject this shortcut. This count
excludes the costs of loads/votes/carry/stores and is not measured speed, DRAM
traffic reduction, convergence improvement, or a path to 10x by itself. A
prototype must still pass signed-zero/subnormal/exact-state gates, full-work
timings and established retention tests before any recommendation.

One run07-guarded workload at a time. 56708 remains read-only. No Rust/CUDA
source changes while a workload is live. No memory/driver settings changed.
