# E023 independent terminal review

Confirmed **rejected** on both registered performance gates. All three fixed pairs remain included; no timing exclusions, extensions or native reruns occurred.

The sum of fixture medians was **9784.7065 -> 9667.4698 ms**, a **1.1981626633%** reduction, below 2%. River median time increased **4.8054091077%**; paired changes were -0.7807%, +4.4151% and +7.3083%, so two of three exceeded the 3% regression threshold.

| Fixture | E020 median ms | E023 median ms | Change |
|---|---:|---:|---:|
| Rainbow | 5768.0171 | 5725.7849 | 0.7322% faster |
| Two-tone | 3915.3640 | 3835.4904 | 2.0400% faster |
| River | 101.3254 | 106.1945 | 4.8054% slower |

All **18 complete non-timing result objects and 138 convergence checks** matched, including full stage trajectories, state fingerprints, exploitability bits and 200/200/60 stops. V023-unit passed **86 tests with 4 ignored**. Its 90 test headers equal E020's original 88 plus the two named plan tests; the separate feature-enabled capacity test was not run.

The audit verified the exact fixed order V023-unit,B074,E023R1,E023R2,B075,B076,E023R3, raw logs, binary/build/authorization links and the physical E023R1 patch alias. All 162 source entries match the executed candidate; precisely five differ from accepted E020. Both newly compiled executables contain the complete candidate CUDA, its unique opponent entry and the intentional exact E020 prefix. Fresh-target Cargo artifacts, compiler environment, terminal build and review/activation precedence passed. Current source custody was recorded before root restoration.

Descriptive candidate-minus-reference component median changes, in milliseconds:

| Fixture | CPU build | GPU init | Solve/checks | Readback | Complete cycle |
|---|---:|---:|---:|---:|---:|
| Rainbow | -3.8139 | -29.1490 | -26.1186 | +12.5151 | -42.2322 |
| Two-tone | -72.4808 | +6.4325 | -24.9836 | +11.8768 | -79.8736 |
| River | +0.0201 | +3.0590 | +1.7120 | -0.0046 | +4.8691 |

The paired total gains were 1.0328%, 1.1505% and 1.1913%. Paired solve/check sums decreased 32.3414, 51.0900 and 64.5593 ms. CPU-build changes and readback offsets also contribute; these spans do not isolate a cause or convert D043's compiler resources into a measured occupancy benefit. Per-component medians need not sum to the complete-cycle median difference. Whole-test/process elapsed values are retained as descriptive evidence and include work excluded from the registered score.

The first reviewer audit stopped because its name parser required each test's result on the same line as its header. Diagnostic output and a caught expected overflow panic split some lines. The failed script/logs remain; an additive r2 parses all headers while preserving the strict 86/0/4/0/0 native summary and exact inventory check. The r2 file-only audit passed 952 assertions. No native workload was repeated.

No broader F32/state/menu/resume/GPU/continuation, capacity test, wide holdout or fresh-original cumulative qualification was executed after this failed screen. The compressed primary and unit raw-state oracle cover the executed cases, not all possible F32 states or workloads. E020 remains the retained implementation; E023 is not accepted or deployed. No checkout, dashboard, build or GPU changes were made by this audit.
