# C12: predicated CDF scan addition

Registered before implementation. Retained baseline is C09 at 0855b89.
D07 rejected source-vector terminal reordering. Current CDF PTX (archived in
C10 exact-2.ptx) already unrolls all six rank tiles, but each shuffle scan step
uses an add followed by a select. Test using the shuffle's own validity
predicate to guard the addition, eliminating the explicit select. Preserve
the five scan steps, six tiles, float addition operand/order, carry arithmetic,
170-entry output, batch32, 1024 particles, launches, allocations and terminal
code. Do not add fast math, shared staging, packing or source-order changes.

NVIDIA specifies that the optional shuffle predicate indicates a valid source
lane: https://docs.nvidia.com/cuda/archive/12.1.1/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-shfl-sync
With up-shuffle clamp0 and steps1/2/4/8/16, this is the existing lane>=step
condition. Use inline PTX with explicit round-to-nearest float addition.
Inspect compiled PTX and loaded function resources; intent alone is insufficient.

Install the separately compiled CDF function only on a fresh C09 engine,
rejecting warmed/captured state. Both ordinary exact-reuse learning and C07
cohort checks already call the same CDF function. No base production API change.

Before timing: compare every CDF float/untouched sentinel with the baseline
writer for compact/noncompact indexing, gate0/1, inactive/zero-mass rows,
aliases, dense/sparse/subnormal/signed-zero inputs, sample offsets0/37/992
and counts1/3/4/5/31/32. Expand whole-solver cohort comparisons to original,
C01,C07,C09,C12 across3-9 seats, batch5/32, locks/frozen seats, capture/replay,
zero-mass clearing/recovery and every terminal value. Run existing exact-reuse
tests. Archive baseline/candidate PTX and function register/local/shared bytes.
Verify small and large allocation plans unchanged before timing.

Freeze the qualified executable; benchmark the same six sweeps, first two
warmup, all checks, initialization and synchronization. First large paired
complete ratio >=0.99 rejects. Otherwise run three alternating pairs per
fixture, retaining only >=3% median large gain, <=3% small median regression,
exact checkpoint/arena agreement, full native GPU and default regressions.
Use run07 ownership/live-status guards, immutable logs/hashes, 240s build/test
caps and180s fixture caps. No edits during workloads; no concurrent GPU work.
Port56708 stays read-only; no deployment. CPU speed is outside scope.

If rejected, archive and remove only C12 runtime code. Do not interpret a
smaller PTX instruction count as a measured speedup or convergence result.
