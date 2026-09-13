# C17: four independent terminal warps per block

Registered before implementation/measurement. Reference: retained C14/R03 at
9c242ce. GPU only, read-only port 56708, serial guarded workloads.

Assign one 32-thread warp to a terminal and four consecutive terminals to a
128-thread block. Each lane evaluates hands lane, lane+32, ... in order. Use
warp-private shared metadata and a warp barrier after lane 0 initializes it;
no cross-warp sharing or barrier. Partial final blocks and non-live terminals
return warp-uniformly. Preserve first-batch zero clearing and exact existing
sample, quadrature and opponent arithmetic for every hand.

Only the exact-reuse and cohort terminal wrappers change. Keep CDF construction,
classification, all global arrays, sample/batch counts, cohort groups, wide-byte
address safety, solver logic and all buffers unchanged. Compile the selected
variant once at construction; use separate PTX caches. Research flag only.
Four warps is the single registered configuration; do not search block sizes
retrospectively. This is different from C08/C16 staging or D10 tiled producers:
no table copying, rebuilding, compression, queue or extra launch is introduced.

Hypothesis: more efficient terminal scheduling and less metadata synchronization
may outweigh processing six hands serially per lane. No source-level traffic,
occupancy or speed claim substitutes for complete-work timing.

Before timing, directly compare both terminal entry points against C14 with
1,2,3,4,5,7,8,9 terminal tasks, mixed active/non-live/zero-probability warps,
all 2–8 opponents, zero/recovery, guarded output and full/partial sample batches.
Cover repeated launches and nonzero sample offsets. Check exact bits. Record
compiled registers/shared/local memory and source/PTX. Expanded cohort tests
must still check all terminal/prefix values, full arenas, roots, gaps/EVs,
3–9 players, locks/frozen seats, batch5/32, capture and stop/sync. Assert the
candidate constructor actually selected the packed variant. Compare saved
small/large allocation plans with C14 before measurement.

First large fixed six-sweep pair rejects at complete ratio >=0.99. If admitted,
three alternating pairs per fixture, >=3% median large complete gain and <=3%
median small regression are required. Include initialization/compile/sync;
all paired checkpoints and full-arena fingerprints must match C14. Native GPU,
default solver and relevant server/selection regressions required for retention.
Build/tests capped300s, each timing180s. Preserve failures, source/input hashes
and frozen executables; restore only candidate runtime if rejected. No deployment
or time-to-convergence claim; the broader convergence goal remains outstanding.
