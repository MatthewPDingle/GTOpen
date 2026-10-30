# E015 independent qualification review

Status: **qualifying, not accepted**. Independently recomputed primary score: **11262.8874 → 10814.3093 ms**, **3.9827984% improvement** (448.5781 ms). All three repetitions remain included. All fixture medians improved and no repeated material fixture regression guard triggered. Broader controls have now passed independent review; fresh original-baseline cumulative evidence remains pending outside this review.

All **18 complete non-timing fixture records** match exactly across six runs, including full arena/root fingerprints, exploitability bits, iterations200/200/60, configurations and targets. Raw stdout result payloads match each report. Both benchmark binaries/build manifests, all six primary stdout/report pairs, frozen-input identity, candidate archived mod.rs, build log/patch, unit evidence and broader-control artifacts were independently hashed; 62 input artifacts remained unchanged during review. Kernel source is byte-identical to E004: `8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0`. Frozen evaluator/configuration and mathematical source inputs are unchanged.

The 84-pass/4-ignored unit log includes both new raw-device reach-reuse tests passing. This covers their bounded in-memory lifecycle and standalone-refresh controls. Additional independently verified evidence now includes 160 ordered exact state/menu/resume snapshots (24/24/112), all non-timing fields for three F32 fixtures, and six GPU tests passing. All corresponding raw logs, reports, preserved binaries and build manifests were hash-checked. These checks qualify the next gate; they do not establish cumulative performance against the original baseline.

## Components

Fixture medians, baseline → candidate (ms):

| Fixture | Full cycle | Solve plus checks | Init |
|---|---:|---:|---:|
| rainbow | 6658.4234 → 6361.7028 | 5520.9071 → 5182.1471 | 682.4113 → 668.3981 |
| two-tone | 4486.3512 → 4344.8963 | 3406.9777 → 3162.6601 | 477.6018 → 456.6619 |
| river | 118.1128 → 107.7102 | 19.8735 → 16.9723 | 95.2379 → 89.5884 |

Solve spans improved in **all nine paired fixture comparisons**. Summed per-fixture solve medians save **585.9788 ms**, versus **448.5781 ms** primary full-cycle saving. Component medians are not additive to the primary statistic, so these figures are not an accounting decomposition.

Paired suite savings below use baseline minus candidate; positive means faster. They are descriptive, separate from the primary sum-of-fixture-medians score.

| Pair | Full-cycle gain | Build saved | Init saved | Solve saved | Readback saved | Full-cycle saved |
|---|---:|---:|---:|---:|---:|---:|
| B035/E015 | 4.9740% | +45.9495 | +37.8539 | +440.9375 | +39.8582 | +564.6043 |
| B036/E015R2 | 5.4665% | -15.3467 | -0.1326 | +665.0202 | -30.3633 | +619.1816 |
| B037/E015R3 | 4.1260% | -54.7805 | -26.4341 | +515.4788 | +30.9786 | +465.2644 |

The mean paired suite saves **549.6834 ms**, with **540.4788 ms** in solve spans. The other measured components add a net 9.1943 ms of saving (mean build -8.0592, init +3.7624, readback +13.4912 ms). This arithmetic supports locating the observed improvement primarily in the measured solve phase. It does not establish the specific kernel cause or explain initialization variation. Solve includes accuracy checks; no statistical-significance claim is made.

All six runtime provenance snapshots contain the same status-runner hash despite the old baseline build manifest recording an earlier Python runner version. Original full reports and stdout payloads remain intact. No production edits, build, test or GPU launch were performed by this review.
