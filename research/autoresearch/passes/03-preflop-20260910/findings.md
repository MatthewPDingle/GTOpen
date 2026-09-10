# Preflop performance research — interim

The ten-hour run remains active until **21:34:18 UTC, 10 September 2026**
(07:04:18 Adelaide on 11 September). These are isolated research results;
the live application on port 56708 has not been replaced or restarted.

## Best measured GPU candidate so far

| Fixed control | Original iteration | Candidate iteration | Reduction |
|---|---:|---:|---:|
| Eight-seat saved game, checkpoint 74 | 9.788 s | 5.462 s | 44.2% |
| Seven-seat fresh game | 2.821 s | 1.368 s | 51.5% |
| Six-seat fresh control | 99.535 ms | 49.225 ms | 50.5% |
| Three-seat small control | 2.481 ms | 1.314 ms | 47.0% |

Iteration figures are medians after the first iteration, with identical input
and iteration counts for each comparison. Early fresh-game iterations change
workload as strategies develop; compare only the matched controls, not rows
against each other. Small controls remain sensitive to timing noise. The eight-seat repeat was 5.469 seconds.

All four controls have **identical complete regret/strategy fingerprints,
gaps and EVs**. The eight-seat accuracy check fell from 11.700 to 7.036 seconds (repeat 7.030).
Its estimated solver VRAM fell from about 20.9 GB initially to 13.1 GB;
the intermediate normalization candidate used 21.4 GB. These are constructor
allocation estimates, not whole-device memory measurements.

Changes retained in the research branch use a 192-thread terminal launch,
prepare counterfactual probabilities once, skip unused learning CDF slots,
normalize reach once before particle scans, and allocate CDF scratch for the
largest individual traverser span instead of the union across all seats.
They also precompute opponent CDF addresses and specialize exact terminal
calculations by opponent count without changing arithmetic order.
Low-memory fallbacks preserve direct normalization and union storage where needed.
All 1,024 particles, precision, bet menus, policies and model semantics remain.

The compact candidate passed 11 internal GPU tests, exact union/compact graph
comparisons, and a real direct/cached one-particle memory-boundary test. Earlier
normalization also passed the 13-test preflop GPU suite. Final combined CPU/GPU,
legacy and save/profile checks remain required before integration.

## CPU work

Minimum exact quadrature reduces redundant tie-share products for fewer than
eight opponents. Recorded three/four-seat solves reached the same target at
the same iterations with identical gaps, EVs and root strategies. A six-seat
20-iteration control also matched those outputs and completed sooner.

An all-eight-opponent terminal microbenchmark regressed approximately 5%.
Several source-shape experiments did not fix it and are not being retained.
A whole nine-seat limp-only control reached the same target in 20 iterations,
about 15% sooner in the first trial and 13% sooner with the clean candidate.
The full default CPU suite passed 174 tests (four ignored) across 36 executables.
Two initial fixture lookup failures were runner working-directory errors;
the identical executable passed all 56 preflop tests from the Cargo package folder. Do not describe the CPU change as universally
faster or bitwise identical at the f64 equity level: reference differences are
around machine precision, though the measured solve outputs matched.

## Remaining work

The eager CUDA phase diagnostic attributes nearly all time to CDF generation
and coupled terminal evaluation. It preserves the expected final fingerprint,
but event timings are diagnostic and are not production graph benchmarks.
Those experiments are complete: address hoisting and opponent specialization
were retained; live-terminal worklists and wider CDF blocks did not clear the
whole-solve retention threshold. Current work covers modeled/frozen tables,
forced-policy VRAM budgeting, and CPU checkpoint traversal.

Raw evidence is append-only in `raw/` and `events.jsonl`; `results.json`,
`cpu-comparisons.json` and `progress.png` are derived views. Failed/rejected
trials remain visible. No final speed claim or completion is implied here.

## Further trials, 13:32 UTC

The static live-terminal worklist passed all correctness gates but was rejected:
its repeatable roughly 1.5% gain missed the fixed 2% retention threshold and
required extra indices. Its source and evidence remain archived.

Precomputed 64-bit CDF base addresses (dea49d1) are promising: the eight-seat
median is 6.018 seconds and its check 7.867 seconds, with exact original outputs.
This is still under repeat/control testing. CDF block geometry trials run
sequentially at 8/16/4 independent warps; all use identical scan arithmetic.

## Checkpoint and modeled-workload gates, 14:03 UTC

Paired CPU checkpoints reuse terminal values between best-response and average
outputs. Four fixed controls preserved every checkpoint gap, EV, iteration and
root strategy. Total time fell 22.7%, 8.5%, 16.0% and 6.9% for the three-, four-,
six- and nine-seat controls versus the preceding CPU candidate; the six-seat
control is fixed 20 iterations, not converged. Checkpoint time roughly halved.
Observed peak RSS was 54.6 MB versus 54.7 MB on six seats and 15.95 MB versus
15.48 MB on nine seats. Wider-frontier and parallel cancellation gates remain.

Forced-policy GPU storage was omitted from the previous memory planner. The
common accounting fix now passes host routing/budget, internal GPU, real
minimum-fit and all 13 preflop GPU tests. It will be applied to both original
and optimized modeled-workload controls. A new native fixture helper caught a
post-save preservation mismatch and refused its output; that fixture is not
yet an accepted benchmark input. Original user saves remain untouched.

## Modeled tables and memory sensitivity, 14:40 UTC

Native measured-policy fixtures now pass strict typed and raw metadata checks.
Legacy and frozen-legacy comparisons match exact arenas/gaps/EVs and show no
material timing change. Coupled modeled trees use 15.36GB optimized versus
22.89GB original allocations at the same23GB budget, with batch32 versus30.
The first iteration medians were3.52s versus28.09s, but original at21GB falls
to6.60s and a23GB repeat is much slower. This demonstrates memory sensitivity;
do not report a stable eightfold kernel speedup or claim measured paging.

The full comparator checked861384actionnodes. Aggregate EV/gap differences
are below3e-8bb, but individual conditional policies differ by up to28.2
percentage points on tiny-reaching branches. This is real distribution change,
not the native uniform fallback. The weighted mean does not establish local
correctness. A matched-batch control and an original-grouping compatibility
planner are being assessed before accepting modeled-table behavior.

### 14:51 UTC: matched grouping restores exact modeled strategies

The optimized layout with explicit batch 30 matches original batch 30 in all 623,785,422 regret/strategy-sum values, all 311,892,711 effective policy entries, every gap and EV, and the native header. Median iteration is 3,624.8 ms and check 4,525.6 ms. Production candidate b7e8583 preserves the original corrected-budget batch and HU cache selection while using compact physical storage. Budget controls and minimum-fit fallback checks remain pending. The earlier default batch-32 local policy divergence is not accepted.

### 15:10 UTC: deployed versus corrected reference scope

The modeled exact-parity controls above include the forced-policy accounting correction in both baseline and candidate. The deployed pre-pass code omitted that allocation, so its batch/cache selection can differ. We are separately reviewing preservation of the deployed grouping when the accurately accounted compact allocation fits. This does not change the frozen convergence protocol or establish deployed-model parity yet.

### Modeled six-seat convergence, corrected-accounting reference

The predeclared 19 GB pair reached the unchanged 0.004 bb learning-gap target at iteration 80 in both versions. Original trajectory 526.5105347 seconds; compatible candidate 289.5910553 seconds (44.998% less). All eight checkpoint gaps, EVs, learning-seat masks and final arena fingerprint d2df70bd6515aabf match exactly; both native save/reload checks passed. This comparison uses the explicitly frozen original kernel with the common forced-policy accounting correction, B23/HU cache enabled. Literal deployed grouping differs for this modeled fixture and remains a separate pending gate; do not relabel this result as that comparison.

### Eight-seat fixed continuation trajectory

Both versions completed native iterations74→174 and missed the predeclared0.005bb target, finishing at0.13924453875862922bb. All ten checkpoint gaps, EVs, learning masks and the final arena fingerprint34d3d0185ea97ce4 match exactly; native round trips passed. Original trajectory1064.6219903seconds; compatible602.4928996seconds (43.408% less). This is fixed-work speed, not time to convergence. Full elementwise native comparisons are running separately.

### Literal deployed compatibility and minimum-memory gates

Candidate5f4f42c preserves literal pre-pass B/cache targets where accurately budgeted physical storage fits. The modeled19GB(B24/HUoff) and21GB(B27/HUon) controls match all623,785,422native arena values and311,892,711effective policy entries bit-for-bit after six iterations. A realistic coupled native80 fixture with five non-BTN seats frozen also matches all entries after six additional iterations. Their iteration medians are6529.2136→3575.0275ms,6592.1862→3624.9175ms and1078.3546→606.991ms respectively. Source profiles, headers and model metadata match; full-native assertions passed.

The literal23GB(B31/HUoff) attempt hit its declared300second cap before one iteration completed. CandidateB31 completed one iteration in3704.7765ms, but no completed literal whole-game parity or speedup ratio is established for this case. Retain the timeout and this limitation.

All28internal GPU/planner tests and13preflop GPU integration tests pass. Both separately invoked low-memory tests pass: a real134MB union/minimal boundary retains originalB1/HUoff and exact outputs; direct/normalized134/135MB paths match. The optimized layout therefore passes tested physical minimum-memory and graph/zero-reach recovery gates.

Full native continuation comparisons also independently passed for modeled80 and eight174:623,785,422 and529,900,514raw arena entries respectively, all bit-identical, plus every effective policy.

### Original allocation diagnostics

Literal source allocates19,098,906,628payload bytes at19GB while its plan omits414,292,684forced-policy bytes. After correcting for that known omission/headroom, an additional~1.138GB driver delta remains. Each-allocation tracing first exposes most of it at d_reach allocation/initialization (1.127GB beyond that payload). Both diagnostic modes return exactly to the starting device-memory baseline after drop. This localizes an interval, not a paging, allocator, memset or leak diagnosis. No additional allocator change is retained.

### 16:22 UTC: launch geometry sweep and specialized register probe

The fixed 192/128/160/256/192 sweep retains 192 threads. Six-iteration eight-seat medians were 5456.37, 6320.53, 5901.48, 5724.69 and 5441.61 ms respectively. Every arena fingerprint, gap and EV matched the original; the repeated 192 control confirms that the alternate widths regress this fixture. These results do not establish optimal widths for untested GPUs.

An isolated compile/load probe reports 64 registers for the generic prepared kernel, 40 for O2/O3 and 48 for O4, all with zero local-memory bytes. The bounded grouped-dispatch candidate is being tested at unchanged 192-thread geometry; reduced resources alone are not acceptance evidence.

### 16:35 UTC: further rejected GPU trials and tree-build screening

The grouped opponent-entry candidate reduced registers but regressed the eight-seat median from5456.37 to5825.03ms and check7022.56 to7747.13ms. Its graph/partial-batch tests and original whole-arena fingerprint/gaps/EVs passed. It was rejected on performance. Shared normalized CDF staging also preserved outputs but regressed median to5629.33ms/check7296.71ms; it was reverted. No grouped dispatch or shared staging remains in the retained implementation.

Action ownership transfer screens at628.386→607.9415ms for a fresh eight-seat tree with identical topology, zero arenas, metadata and native roundtrip. Retained String capacity increases621170bytes (under0.1% of the full game). This single3.25% result is not acceptance; repeated pairs and RSS review are pending. The runner stopped on Windows extended-path spelling despite identical file identity; the comparator now uses OS samefile for existing input/output files, with dedicated tests. Existing timing outputs remain unchanged.

### 16:47 UTC: implementation frozen for final gates

Retain action ownership transfer4878044. Five fresh eight-seat pairs show median paired reduction4.2428% (range2.4899–6.7244%); baseline/candidate timing medians620.4585/595.0525ms. Five load pairs show no material regression (medians1296.8208/1293.5347ms; paired median improvement1.2208%, range-0.6642–4.3630%). All typed metadata, full native arena fingerprints, topology and action-label gates passed.

The initial small-tree one-pair2.38% regression did not reproduce: five new alternating pairs give13.0015/12.8364ms medians and1.2699% median paired improvement, with noisy-6.95% to+6.51% individual reductions. No small-tree speedup claim is made. Large-tree retained action strings cost621170extra bytes; observed whole-process peak RSS medians differ by only12–25KB against~2.745GB. Small-process50ms RSS sampling is insufficient for a reliable memory comparison.

The full default CPU suite on4878044 passed181tests,0failures,5ignored, across36executables plus doc tests. Final GPU tests and final frozen-source throughput checks remain in progress; no runtime deployment has occurred. CPU quadrature retains its stated numerical tolerance rather than claiming original CPU bitwise identity.

### 16:56 UTC: final controls complete; extended protocol frozen

Accepted source4878044 passed181default CPU tests and105GPU-feature/library/integration/boundary test invocations. The final3/6/7/8fixtures match all original fingerprints, gaps and EVs;68GPU runs in this pass now pass the frozen comparison. Final8median5456.6196ms/check7033.9039ms,7median1369.1646/check3586.2247,6median48.8118/check80.7558,3median1.3070/check2.4563. Timings are fixture-specific medians after the first iteration, not universal throughput.

The final modeled19GB,21GB and frozen-coupled native fixtures independently pass full comparisons:623785422raw arena values and311892711effective policy entries each, all finite and bit-identical with literal pre-pass controls, plus headers/profiles. Native iterations6/6/86 respectively.

A separate extended protocol was frozen before launch at16:55:54UTC (SHA256aac9b54c22361acdbfb3951a845bfa5d6e3c81bf54e6006de37b569ce436f7f8). It compares literal deployed15723d2GPU control with final4878044. Modeled19GB starts fresh, target0.004bb,limit100,checks10;8seat starts from the identical original native174, target0.005bb,limit900additional,checks50. Explicit finite timeouts and the original21:34:18UTCdeadline apply. This new comparison does not erase or relabel the prior100-iteration8seat target miss. No implementation change or live deployment is planned during these trajectories.

## Final literal modeled convergence gate — 17:13 UTC

Frozen accepted4878044 versus literal GPU15723d2, 19GB/B24/HU-off, fresh0→80: both reach the predeclared0.004bb target with final learning gap0.003812060588789537. All8 checkpoint sequences and final EV/gap/arena values match. Trajectory522.1386656→282.9241671seconds (45.8% less); total guarded process548.266→306.031seconds. Independent extended-native-modeled-a comparison and strict assertion pass all623,785,422 stored floats and311,892,711 effective policy entries, finite and exact, with matching native metadata. Extended eight-seat original then candidate queue has started; its target remains0.005bb,900 additional iterations maximum from the same native174 save. Initial100iteration target miss remains separate evidence.


## Final eight-seat convergence, integration and deployment — 20:20 UTC

Both frozen extended eight-seat runs reach0.005bb at native1024 (850 additional from174), gap0.004783754646191074. All17 checkpoints and complete native data match. Trajectory6813.4893943→3531.2897268seconds (48.2% less); guarded total6833.860→3550.469seconds. Native assertion verifies529900514 raw values and264950257 effective policies exactly. Initial74→174 target miss remains recorded independently.

Main184f17a integrates only the5 accepted preflop files plus README link; byte-normalized hashes and git blobs match4878044. Server8passed/0failed/1ignored, productionreleasebuildpassed. RuntimeSHA7e96cde87bb87ee6dbdd693e010275851eb4d1cc6b4d2bcb550c4ef89173bb6d. Isolated smoke and live cutover verified complete native header/arena state. Port56708 nowPID108484, target/desktop-runtime/release/gto-server.exe; oldPID99216 ended only after latest native recheck. Preflopnative74 andpostflop210/Kd6s5c preserved; no live solve started. Details deployment-evidence.json. Old executable/backups preserved.

A final fresh-state qualification is frozen/pushed947447d before launch: three alternating original/accepted pairs,8seats1.57Mnodes native0→20,23GB,target0.005,checks10, complete native comparisons. It covers first-checkpoint latency for a newly built game, whereas long eight-seat tests resumed native174. No new source changes. Fixed-work results will not be described as fresh-game convergence; guards stop on user activity and reserve the original deadline.


## 20:38 UTC: fresh-eight startup complete; real API qualification started

All three alternating originalGPU15723d2/final4878044 pairs from native0 to20 (check10,target.005,23GB,16threads,1024samples) match every checkpoint and every raw/effective native entry. Strict native assertions fresh-eight-native-{1,2,3}-a each passed529900514raw/264950257effective values. Median paired fixed-work reduction42.4453579361%; medianoriginal192465.6162ms versuscompatible110694.6566ms. First checkpoint including load/init medians92497.7012→53474.855ms. Both miss target at20 in every pair; no fresh-game convergence claim.

API firststrategy qualification api-first-strategy-eight-a launched20:37UTC after freshqueuecompleted. Actual original archived9c095b6e... and deployed7e96cde8... runtimes; independent hidden servers in privatecwd, defaultcheck50 omitted from POST, native0→50,target.005,23GB,16threads,1024samples. Protocol frozenbeforelaunch and copied into mainpass/api-first-strategy-eight-a-protocol.json. Controllerexec84577; originalchild82768/privateport62703. Real56708 onlyGET guard, no live mutations.600secondscase,21:29:18stop-before; failurepreserved. Fullnative/rootsemanticidentity gates required. e89e8f4 helper source pushedbeforelaunch. No more implementation changes.
