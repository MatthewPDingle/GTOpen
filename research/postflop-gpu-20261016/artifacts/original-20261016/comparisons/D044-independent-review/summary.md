# D044 independent terminal review

**PASS for this scoped diagnostic. No optimization is accepted.** All six fixed ordinary/instrumented processes completed in the declared D044B1,P1,P2,B2,B3,P3 order. All 18 complete non-timing results, 138 convergence checks and normalized stage trajectories are exact. All nine constructor records passed: exactly three per instrumented run, none in controls, correct fixture/start/build placement, exact board/hand/node identities, finite nonnegative nested envelopes and unchanged suit-permutation counts.

Ordinary sum of fixture medians was **9823.5624 ms**, instrumented **9766.7499 ms**, an outer change of **-0.5783288962%**. This passes the prespecified absolute 10% usefulness guard. It is not a performance improvement result and does not bound individual component bias. Every pair remains included; the river paired changes (-9.7687%, -4.3248%, +1.8034%) are retained.

| Instrumented median, ms | Rainbow | Two-tone | River | Sum of fixture medians |
|---|---:|---:|---:|---:|
| Tree build | 76.6030 | 174.9296 | 0.0074 | 251.5400 |
| River-table build | 3.3669 | 3.5668 | 0.0257 | 6.9594 |
| Suit symmetry | 0.0376 | 0.0454 | 0.0222 | 0.1052 |
| Constructor before logging | 80.2578 | 178.7047 | 0.1909 | — |
| Outer build minus constructor | 2.8758 | 189.2427 | 0.0783 | — |

Tree, river-table and symmetry sums represent 2.5606%, 0.07084% and 0.001071% of the ordinary complete-cycle score respectively. The river-table span contains its entire builder, including ranking, sorting, allocation, scheduling and cleanup. Its small measured direct cost alone does not justify a ranking-deduplication candidate; no removable fraction or global cache-effect bound is established. Tree time and especially the two-tone outer residual are larger observations, but they do not identify an optimization or establish a possible 2% saving.

The outer residual includes CPU storage/setup, final constructor return and temporary destruction, logging/timer and evaluator overhead. It must not be labeled allocation time or attributed to a particular cause. Nested envelopes/residuals overlap; sums of component medians need not equal medians of enclosing spans. All raw component values and ranges are retained in validation.json.

Fresh-target Cargo solver/test artifacts, correct source paths, compiler environment, accepted embedded CUDA plus the diagnostic marker, immutable binary/source/authorization pins and source custody passed. Exactly game.rs differs from the accepted 162-entry E020 source map; all 162 current entries matched the executed diagnostic when audited. Root may restore that exact owned file after the custody check. No source, dashboard, build or GPU action was performed by this reviewer.

The first file-only audit stopped because an inherited strict chronology check rejected equal one-second timestamps: D044B3 finished and D044P3 began at 13:25:12Z. The frozen runner waits for each child, and wrapper exit/invocation records are nondecreasing. The original reviewer failure is preserved; additive r2 changes only this comparison to <=. No native rerun, measurement replacement, exclusion or policy change occurred.
