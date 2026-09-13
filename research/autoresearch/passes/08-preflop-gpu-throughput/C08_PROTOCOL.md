# C08: cooperative CDF staging in terminal evaluation

Registered after D06, before implementation/measurement. Baseline is retained
C07 with diagnostic tracing off. Terminal evaluation is 54% of learning and
64% of accuracy checks in D06. Test one memory-access mechanism there.

For each terminal and original particle, cooperatively load each opponent's
170-value CDF row into shared memory using coalesced loads. All 192 threads
participate in staging and barriers. Only the 169 valid hand threads evaluate
the existing quadrature. Preserve q/t/sample loop order, constants, fmax,
weighted additions, probability/pot/investment operations and batch boundaries.
Use block-uniform early return for zero-probability terminals, retaining the
original first-batch zero clearing. Do not read lower/upper for inactive threads.

Apply the same helper to C01 learning terminals and C07 cohort-check terminals
through an explicit opt-in research constructor. Compile variants directly at
construction with separate PTX caches, not by replacing live graph pointers.
Keep all global arrays, cohort groups, cache budgeting and allocation sizes
identical to C07. Shared storage is at most 8*170*4 = 5,440 bytes per block;
record this cost, and do not assert hardware traffic reduction from source-level
load counts. New barriers, shared bank conflicts or occupancy loss can hurt.

This is NOT the previously rejected shared normalized-input staging inside
the CDF producer. CDF construction and identity classification remain unchanged.
No lower precision, fewer samples, reordered arithmetic or changed policy work.

Extend C07 full-arena/roots/capture/frozen/stop and all-terminal/zero/recovery/
prefix tests to compare original, C01, C07 and C08; cover 3–9 seats, opponent
counts 2–8 and batches 5/32. Require exact output bits. Keep original C01 tests.
Allocation metadata must match C07 on both frozen saves. Build/test cap 240s.

First large six-iteration paired screen (two warmups, check each sweep) rejects
at complete-time ratio >=0.99. If it passes, three alternating-order pairs per
fixture are required, >=3% median large complete gain in a consistent direction,
and <=3% median small regression. All checkpoints and arena fingerprints exact;
native GPU and default solver regressions required for retention. Constructor,
compile/allocation and synchronization costs are included. Cap each run 180s.

Use run07 guard and immutable source/input/executable hashes, one workload at a
time, no edits while timing. Archive failures and revert only this prototype if
rejected. No CPU performance work and no writes/restarts/deployment on port 56708.
This tests throughput, not full conditional-convergence qualification.
