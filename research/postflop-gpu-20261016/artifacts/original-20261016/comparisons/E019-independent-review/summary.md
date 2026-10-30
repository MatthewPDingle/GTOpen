# E019 independent terminal review

Confirmed rejected. The registered sum of three fixture medians is 9,981.6832 ms for accepted E015 and 9,910.0980 ms for E019: a 0.7171656% improvement, below the fixed 2% gate. No fixture regression guard fails. All six planned timings remain included; no extension or exclusion was used.

All 18 complete result objects match after excluding only the six timing fields. This includes the whole arena/scale fingerprint objects, root strategy bits, configuration, stopping iterations and exploitability values. All 138 convergence-check records match, and the entire non-timing stage sequence is identical. The unit screen ran the same 88-test inventory as E015: 84 passed, four ignored, none failed or filtered.

The verified 162-entry build-source maps differ only at kernels.cu, using the exact independently tested D036 candidate bytes. Evaluator and workload hashes match the original frozen manifest. The candidate/reference binaries, manifests, build logs, raw outputs and declared order were checked. Cargo completed before the unit screen; the unit screen completed before all six serial primary runs. The explicit logical E019 to physical E019R1 adapter and byte-identical build-patch alias are preserved; no synthetic E019 measurement exists.

| Fixture | Baseline median ms | Candidate median ms | Complete-cycle gain | Solve median change ms |
|---|---:|---:|---:|---:|
| Rainbow | 5,885.5626 | 5,853.2969 | 0.5482% | -3.1851 |
| Two-tone | 3,982.1984 | 3,952.8444 | 0.7371% | -7.2745 |
| River | 113.9222 | 103.9567 | 8.7476% | -2.1668 |

Negative component changes mean shorter candidate times. The flop solve medians fell only 0.0665% and 0.2480%; rainbow paired solve differences were +1.6405, -13.4470 and +1.0326 ms. Across all fixtures, paired solve sums changed +3.3527, -26.7604 and -7.3559 ms. Paired total-cycle gains were 0.1201%, 0.4081% and 0.4279%, each below 2%.

Initialization median changes were -9.5812, -35.3449 and -7.3333 ms for rainbow, two-tone and river. Construction and readback also varied. These are descriptive observations, not evidence of what caused the timing differences. Per-component medians and paired medians use different order statistics and need not add to the primary score difference. Whole-test and process times were slightly shorter in each pair, but include excluded work and do not replace the registered score or prove statistical significance.

Broader original-baseline F32, saved-state/menu/lock/resume, continuation and cumulative checks were not run after the failed screen. Compressed final-state equality, D036's constructed cases and shared-candidate unit references do not establish universal raw-state equivalence or solver acceptance. No gain is accepted or deployed; E015 remains the retained baseline.

Audit actions were evidence reads and CPU-only analysis. The first audit script stopped on uppercase-versus-lowercase hexadecimal digest formatting in the original manifest; the initial script/failure record is preserved, and the corrected case-normalized check passed. No experiment was rerun or altered. validation.json records 754 assertions and 96 hashed input artifacts.
