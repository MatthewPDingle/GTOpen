# Next proposal: lossless CDF run compression during learning

Not implemented or benchmarked yet. This follows C03's failed retention gate.

## Evidence and scope

D02's large current-play unique distributions average 19.39 nonzero hand classes;
80.44% have at most 32. Average-play unique distributions all contain 169 classes.
The code independently separates learning terminal calls (gate=1) from average
checks (gate=0, see `queue_evaluation`). A memory optimization should therefore
leave the dense accuracy-check path unchanged.

## Mechanism to test

Keep the original CDF scan, all 1024 particles, arithmetic order and batch32.
For learning only, encode the exact resulting prefix values as runs: compare
each emitted prefix's bits with the preceding prefix; store a change bit and
append only changed f32 values to the existing per-distribution CDF allocation.
A six-u32 mask per particle covers the 169 ranks. Derive the compressed value
index by popcount of preceding mask bits. Decode logical CDF(0) as +0. The
terminal's subtraction, Gauss products and accumulation remain unchanged.

Do NOT infer runs solely from zero normalized entries. Hillis-Steele prefix
rounding can change the stored prefix even where no new nonzero hand enters.
Run boundaries must compare actual output bits after the original carry+value
operation. Use ballot/shuffle within the existing particle warp to construct
masks and packed indices, preserving the original CDF mathematics.

C01 aliases select the same representative for both values and masks. All six
mask words must be written for every produced row. Gate=0 keeps the existing
full CDF kernel/reader; no dense-check decoding penalty. A fresh mask allocation
adds roughly 298 MB on the large fixture, with a hard prototype cap of 512 MiB
and explicit budget headroom. Do not shrink particle batch or displace caches.

## Required checks before timing

1. Directly compare all 170 logical CDF prefixes bit-for-bit against the original
   writer over dense, sparse, all-zero, one-hot, subnormal and varied-magnitude
   normalized inputs, permutations, sample offsets, compact/partial batches,
   changing masks, and poisoned unused capacity. Include a case where scan
   rounding creates distinct adjacent prefixes despite zero added mass.
2. Original/C01/candidate full terminal and arena comparisons, all 2..8 opponent
   counts, locks/frozen seats, own/live/folded zero reach, recovery, graph replay,
   alternating learning and average checks, and stop/resume boundaries.
3. Only then use the same first-pair 1% admission screen and three-pair 3% large
   complete-runtime retention gate, small nonregression and full regressions.

The risk is that popcount/mask decoding costs more than the reduced global
writes and tighter value reads save. No performance claim exists yet.
