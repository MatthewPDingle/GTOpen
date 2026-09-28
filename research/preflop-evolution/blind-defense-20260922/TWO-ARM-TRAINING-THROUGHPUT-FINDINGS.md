# Two independent training updates: serial versus concurrent

All four cases reproduced their original archived update-79 results exactly.
The fresh serial pair took **241.030 seconds** in the measured update calls;
the concurrent pair finished in **205.912 seconds**: **14.57% less elapsed time**
(1.171 times throughput for this pair).

The concurrent pair was faster on this fixture. Retain this bounded scheduler as an option for a future prospectively specified study; this single pair does not establish a universal speedup.

| Case | External update seconds | Pipeline seconds | Recorded GPU guard wait seconds |
|---|---:|---:|---:|
| serial-baseline | 56.380 | 56.360 | 0.078 |
| serial-river | 184.651 | 184.625 | 0.376 |
| concurrent-baseline | 83.987 | 83.953 | 0.251 |
| concurrent-river | 205.912 | 205.891 | 0.594 |

Concurrent starts differed by 0.011048 seconds.
The call intervals overlapped for 83.987 seconds.
These externally timed calls include the same initial update guard and final CUDA
synchronization. Setup and readback are excluded from both comparisons. The
readback barrier was verified to follow both concurrent updates.

Whole invocation took 1213.3 seconds, including admission,
storage scans, source loading, all four updates and their verification. This is
not a production-solve benchmark. Serial-first order, OS caching, guard checks
and other system load can affect timing. There is one pair, not repeated trials.
GPU guards can observe the other owned child, so their wait is not classified
as external-only contention. A slower individual concurrent update can coexist
with a shorter overall pair makespan.

## Correctness and resource evidence

Each child checked full checkpoint/restored-state identity, fitted networks and
numeric fitting results, ordered reservoirs, played-model membership, source
deals/action streams and subbatch artifacts against the original saved oracle.
The independent artifact readback checked 2128 referenced artifact hashes
and recomputed timing arithmetic. It did not independently rerun poker inference.

At most two coordinators ran, each with eight physical and four board workers.
Each had a 2GB CUDA allocation/reservation cap. Maximum reported per-child CUDA
reservation was 0.466 GB.
The existing light-desktop sharing checks and production priority were retained.
The coordinator has exited; its final owned-job active-process count was zero.

Retained new evidence: 2.064 GB logical,
0.886 GB allocated. Final global
research allocation: 740.141 GB,
within the 800GB cap. Historical and failed evidence was preserved.

## Next research step

Return to evaluation precision before another large training run. The proposed
reach-weighted design passed exact-rational finite-domain checks, but its poker
adapter and floating error bounds are still unqualified. Reuse the existing
6,630-row native preflop holding catalog; it covers every preflop decision in
this context, unlike the smaller first-action catalog. Reconstruct and verify
own-action histories before extracting all complete-bank preflop policies.

This scheduling result supplies no evidence of more accurate ranges, stronger
play, cross-stack transfer or multiway accuracy. No production changes,
deployment or GitHub push were made.

Result SHA256: e6b0b0e6cc835c1aace7737e627a6396fe932170326f1c020c2dd879ae74f782.
Registration SHA256: e164546be2e6f0c06e66eb86b6a487103167f85a83d0647555e487f19a0872e1.
Readback: two-arm-training-throughput-control-v1-readback-v1.json.
