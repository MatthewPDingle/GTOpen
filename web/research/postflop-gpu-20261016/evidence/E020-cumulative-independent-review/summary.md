# E020 cumulative independent review

PASS. Recommend accepting E020 for the registered postflop GPU corpus, carrying the separately sealed primary, broader correctness and wide-turn holdout reviews. This is a qualification recommendation; root controls integration and deployment.

The six prescribed runs completed in order with no exclusions or extension. All 18 complete non-timing results and all 138 convergence records match the preserved primary anchor, including whole-arena fingerprints, root vectors, exploitability bits, settings and stopping iterations. All 222 raw stage objects also match after removing only timing fields. Binary/build-manifest/source identities, raw-log hashes, runtime settings, assessment invocation and qualification readiness before the first native launch were verified.

The unchanged sum-of-fixture-medians score is **10,952.0754 to 9,815.2669 ms: 10.379845% lower** than the fresh original baseline. Pair totals improved 10.1928%, 10.3649% and 10.3491%; these are descriptive, not a replacement score.

| Fixture | Original median ms | Candidate median ms | Change | Paired slowdowns above 3% |
|---|---:|---:|---:|---:|
| rainbow | 6484.6166 | 5786.6521 | 10.7634% faster | 0/3 |
| two-tone | 4362.5817 | 3922.9901 | 10.0764% faster | 0/3 |
| river | 104.8771 | 105.6247 | 0.7128% slower | 1/3 |

River paired slowdowns were -9.7130%, +5.5324% and +0.9283%. Its 0.7128% median slowdown and only one pair above 3% pass the unchanged repeated-regression guard. No favorable observation was substituted.

Descriptive component deltas (candidate median minus original median, milliseconds):

| Fixture | Build | Init | Solve/checks | Readback |
|---|---:|---:|---:|---:|
| rainbow | -1.9603 | -317.9174 | -383.0554 | +5.1996 |
| two-tone | +8.7499 | -234.6826 | -216.8829 | +1.1804 |
| river | -0.0481 | +0.9365 | -0.3196 | -0.0080 |

Both flop solve/check spans were lower in every pair. Initialization and solve improvements describe the combined accepted changes versus the original; this cohort does not isolate E020 or establish the cause of individual component variation. Component medians do not necessarily sum to the full-cycle median. The isolated E020 screen versus retained E015 was separately measured at 2.2141%; percentages from separate cohorts must not be added.

Scope: three pairs on one RTX 5090 and the fixed compressed fixtures, plus the independently audited wide-turn holdout and correctness controls. No statistical significance, universal configuration/device, cold-start, F32 speed, API, disk-saving or SSD-spill claim follows. Runtime NVRTC/JIT remains inside initialization; Cargo, fingerprinting and final destruction are outside the registered score.

The comparison helper leaves generic broader/F32 correctness fields marked pending/not run; those placeholders are superseded by the separate pinned qualification reports and readiness, not silently rewritten here. Likewise, missing original-manifest source entries mean unknown coverage, not source changes. The previously sealed primary audit supplies the accepted-E015 two-file source proof. The wrong-arm R1 holdout build remains preserved and unused.

audit.py is a standalone CPU-only verifier. Its sole invocation succeeded; raw stdout/stderr and exit record are preserved. No builds, native tests, GPU jobs, production edits or dashboard changes were performed by this audit.
