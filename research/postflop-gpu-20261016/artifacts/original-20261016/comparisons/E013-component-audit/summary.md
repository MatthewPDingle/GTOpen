# E013 independent component audit

E013 remains rejected. The frozen score is reproduced exactly: **10990.0495 to 11026.1506 ms (0.328489% slower)**. Component analysis does not replace or reinterpret that score. No GPU execution, build, repository edit or dashboard change was performed.

All six report/stdout/binary/build-manifest checks pass. Across the 18 fixture results, every non-timing field matches the fixture reference exactly, including the complete state-fingerprint object, exploitability bits, configuration, storage, algorithm and stopping iteration. Each cohort uses one unchanged frozen binary, with the same RTX 5090 identity/driver and runtime environment. Kernels, plan, Store encoders, CFR source, fixture input and frozen evaluator hashes match between cohorts.

## Paired complete-suite component savings

Positive values below mean baseline minus candidate (milliseconds saved).

| Pair | Build | Init | Solve/checks | Readback | Full cycle | Full-cycle gain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B029 / E013 | +66.6668 | -55.5880 | +283.0641 | +30.6881 | +324.8524 | +2.7714% |
| B030 / E013R2 | -29.7255 | -35.5423 | +113.6416 | +42.6197 | +91.0018 | +0.8298% |
| B031 / E013R3 | -8.8868 | +2.2377 | -56.8458 | -4.0924 | -67.5965 | -0.6168% |

The first pair saved 324.8524 ms, of which **283.0641 ms (87.14%) was solve/checks** and **30.6881 ms (9.45%) was readback**. This host-readback change does not change GPU kernels or the frozen solve settings. Therefore the first-pair gain cannot be attributed to faster CUDA solving on this evidence. The later solve deltas shrink and reverse; three pairs do not identify the cause or establish statistical significance.

## Per-fixture component medians

Each cell is baseline → candidate in milliseconds. These medians are selected independently and **must not be added to explain the median full-cycle change**.

| Fixture | Build | Init | Solve/checks | Readback | Full cycle |
| --- | ---: | ---: | ---: | ---: | ---: |
| rainbow | 84.8401 → 83.9125 | 681.5388 → 679.8210 | 5342.8831 → 5346.4176 | 351.9761 → 345.8179 | 6461.5186 → 6434.2685 |
| two-tone | 420.9918 → 431.0358 | 460.9668 → 493.9974 | 3249.6288 → 3302.4319 | 283.8491 → 270.8182 | 4408.4971 → 4483.3628 |
| river | 0.2359 → 0.2195 | 99.8829 → 90.0427 | 18.8962 → 17.1240 | 0.8270 → 0.8621 | 120.0338 → 108.5193 |

Readback summed fixture medians improve **636.6522 → 617.4982 ms**, saving **19.1540 ms (3.0086%)**. That saving is only **0.1743%** of the primary baseline complete-cycle score. Rainbow readback improves 1.7496%; two-tone 4.5908%; river changes from 0.8270 to 0.8621 ms, a 0.0351 ms increase. Rainbow improves readback in all three pairs; two-tone improves twice and regresses in the third. No fixture triggered the frozen repeatable-regression guard; rejection was the aggregate <2% gate.

For an additive diagnostic only, the mean paired suite deltas are build +9.3515 ms saved, init −29.6309 ms, solve +113.2866 ms, readback +23.0718 ms and unassigned wall remainder +0.0068 ms, totaling +116.0859 ms. This mean is a different statistic from the required sum of fixture medians and does not change the rejected result.

## Why the isolated encoder result is insufficient

- D015 times a single-threaded encoder over eight reused source blocks and one reused destination (prototype.rs:102–145). Its finite cases measure about 51–55% encoder speedup; zero blocks differ. This excludes device-to-host copying, synchronization, Rayon dispatch and large scattered arena writes.
- E013 full readback includes those additional operations. Its timers do not separate encoder time from transfer, scheduling and memory costs, so their proportions and the dominant bottleneck remain unmeasured. Memory bandwidth, working-set size, scheduling, GPU clocks or incidental system variation are hypotheses, not established causes.
- D019 proves the intended packed-rounding code generation in a matching-source final ThinLTO diagnostic build; complete typed encoder assembly matches D015 after symbol/label renaming. It is not disassembly of the separately frozen measured E013 executable. D017/D018 library assembly is not final-executable evidence.
- The observed full-readback improvement is much smaller than the isolated encoder improvement, and it cannot explain the first-pair solve swing. A fresh component profile is justified; another acceptance statistic or extrapolated microbenchmark gain is not.

Raw pair/fixture timings, ranges, source differences, exact comparison keys and input hashes are in report.json. Original evidence remains unchanged.
