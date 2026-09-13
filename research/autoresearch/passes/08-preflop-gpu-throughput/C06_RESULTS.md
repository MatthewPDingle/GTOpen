# C06: shared cohort checks rejected on first timing pair

The prototype is numerically equal but **41.11% slower overall** than retained
C01 on the large frozen save. It failed the registered first-pair screen.
No extended timings, retention regression campaign or deployment followed.
The prototype has been removed; exact tested source/executable are archived.

| Metric | C01 control | C06 candidate | Change |
|---|---:|---:|---:|
| Complete fixed-work run | 66.467s | 93.789s | 41.11% slower |
| Warm learning iteration | 3.400s | 5.520s | 62.36% slower |
| Warm accuracy check | 6.794s | 9.065s | 33.43% slower |
| Constructor | 1.252s | 1.556s | +0.304s |

The work-sharing premise is real (D05 measured47.35% fewer average-check CDF
rows), but the implementation loses more elsewhere. Learning arithmetic and
dispatch were unchanged, yet learning slowed too. Memory pressure, cache/TLB
effects or residency are plausible causes; these timings do not isolate the
cause. Do not label this a demonstrated paging problem or a speedup.

The actual device buffers totaled22,655,334,172bytes, matching D05 exactly.
Adding256MiB reserve gives22,923,769,628bytes. Constructor planning avoided old/
new CDF coexistence. Existing HU cache and batch32 were preserved. The large
CDF grew8.445GB to15.714GB, with three complete extra value buffers. Fitting
the registered allocation budget alone was insufficient for fast execution.

## Numerical evidence

Three final tests passed: planner mapping/budget/overflow; complete strategy
arenas and check roots through repeated eager/captured operations, frozen
seats, point locks, stop/sync and batches5/32; all terminal bits through zero
own/live/folded opponent reach and recovery, all2-8-opponent templates, and
final-batch CDF prefix bits against the original writer. Table sizes3,4,5,6,8,9
were exercised. Seven-player and additional error-path coverage would still
be needed for retention, but the performance rejection makes further C06
qualification unnecessary. The first six large checkpoint gaps/EVs and final
complete arena fingerprint match the paired control exactly.

Small/large saved-game construction independently confirmed all46 plain device
buffers plus cohort scratch match the planned budget/group selection. The
benchmark build reran the final three numerical tests. Initial expanded-test
compile errors were fixed before those runs; their logs remain in the record.

Artifacts: `artifacts/c06-rejected`, `artifacts/c06-source-map.json`,
`raw/c06-*-bench.json`, guarded exit metadata/logs, and `raw/c06-verified.json`.
Frozen local executable: `target/c06-benchmark-frozen.exe`.
`check_c06.py` audits tested source/input hashes, numerical comparisons,
allocation accounting and rejection ratios. The allocation test executable
preceded the benchmark-only wiring change; all constructor/kernel/planner
sources are identical. No speed or broader convergence claim. Port56708
remains unchanged.

Next: test a distinctly smaller working set under a new protocol, rather than
repeating the failed four-player/23GB configuration. D05 already identifies
three-player partitions with roughly31% work reduction near20.5GB. Retain the
same particles, batch, precision, caches and numerical gates.
