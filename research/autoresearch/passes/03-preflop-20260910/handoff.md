# Current state

Ten-hour run ACTIVE: deadline 2026-09-10 21:34:18 UTC (Sep11 07:04:18 Adelaide).
Never reset the clock or mark complete before required research/final gates.
User server56708 preserved; both sessions backed up as
Before preflop autoresearch 20260910 2104. Preflop checkpoint74 is frozen.
Only run isolated hardware jobs while live API is idle; measure.py and
run_guarded.py poll every3sec and kill only their own process if userwork starts.

Worktree: T:/Dev/GTOpen/target/autoresearch/preflop-20260910.
Branch codex/preflop-autoresearch-20260910. Main master, setup pushed49e69b5.
Implementation baseline1b8fc3f, frozen GPU harnessc4501e3. Inputs/hash in run.json.
No production implementation or server restart yet. Check active.json before GPU.

## Candidates so far

- 192-thread coupled terminal9ea4164 vs original64 on largegrids:
  eight baseline9.788/9.762s ->7.852/7.829s; check11.700/11.688 ->8.935/8.910.
  Exact fingerprints/gaps/EVs on3/6/7/8controls. 128thread4b872ce rejected (8.438s).
  Baseline controls483c63a finished;6bc56e3 restores192.
- Active-slot gating+prepared probability f7b2072: eight7.083/7.098s;
  sevenfresh1.653s vsbaseline2.821. All1024samples/f32 arithmetic retained.
  Exact fingerprints. Check regression addressed by3295571 learning-only gating:
  eight7.084s/check8.907s, seven1.656s/check4.565s. Tests atf7: internal6/6,
  preflop GPU13/13. Combined fullCPU/final tests stillrequired.
- Normalized reach8ac30e8: identical f32 division once per slot before particle scans.
  Eight6.303s/check8.373s, seven1.513s/check4.326s. Exactbaseline fingerprints/gaps/EVs.
  Eight32batch,21408MB estimated, +~514MB. 497c549 adds non-unit/stale/poison/gate0
  tests, compilation session80524. Agent preflop_kernel_review preparing optional
  normalization memory-fit fallback proposal; preserve old minimum oneparticle fit.

## Commands

Main cwd: python research/autoresearch/passes/03-preflop-20260910/measure.py ID ABS_INPUT N
UniqueIDs; uses alreadybuilt worktree target/release/examples/preflop_research_bench.exe.
Rebuild after sourcecommit so commit/executable evidence agrees.
Eight input T:/Dev/GTOpen/saves/preflop/Before preflop autoresearch 20260910 2104.gtop,6iters.
Seven fixtures/seven.json,4; six fixtures/six.json,6; three fixtures/three.json,30.
Use absolute fixture paths under this passdir. Optional --legacy supported.
Build in worktree: cargo build --release -p solver --features gpu --example preflop_research_bench
Tests: cargo test --release -p solver --features gpu --lib --test preflop_gpu --no-run
Run built testexe via run_guarded.py ID ABS_EXE [filter] --nocapture --test-threads=1.
Internalfilter preflop::gpu::tests::. Testexe filenames in buildoutput.
render.py derives results.json/progress.png from append-only events.jsonl.
Rawlogs immutable. Archive candidate git-show patches. Push periodic evidence.

## Next rotation

Finish normalization tests/fallback, repeat8 and smallcontrols. CPU quadrature proposal
ready in proposals/cpu-quadrature (UNTESTED): minimum exactGauss points by opponents,
retainsf64/1024samples, reference tests. Needs before/after CPUterminal benchmark
and solver time-to-same-gap because rounding differs. Other GPU hypotheses:
compactCDF slots per traverser, lowerbatchmemory, checkpointreuse, phaseprofiling.
No reducedprecision/samples/betmenus. Neverreuse across alternating learning without
correctinvalidation. Atdeadline finishaccepted combined CPU/GPU/save/profile/legacy
validation, integrateverified changes, pushGitHub, final measured report, pause
heartbeat preflop-autoresearch-10-hours, thenmark goalcomplete.

## Update 12:33 UTC

GPU preferred normalization repeated6.299s/check8.374s exact. Fallback8 fixture6.317s
exact too. f2f217c fallback pureplanner+internal9 pass. Current083d478 includes
CPUquadrature423f58a (UNTESTED) andactualignoredGPUboundarytest e828f53 (nested
modulepathfixed083). Buildsession59551 compilingtestexes thenbothbenchharnesses.
Next run internalpreflopGPU including explicit ignored
coupled_minimum_budget_direct_and_normalized_paths_match, CPUmultiwayreference,
and CPUbenchterminal/three/four/six vsbaseline logs. CPUharnessfrozenddcebc2 after
rawfixturefitguardfix; initialcpu-three-baseline-a failedharnessassertbeforemeasurement.
CPUbaseline3 reachedgap0.004 at30,4 at40; six20fixediterations33sec (notyetconverged).
Agentpreflop_kernel_review preparingcompactimplementation/testproposal, noGPUjobs.
Instrumentation9880326 shows8union760578,maxseat388082=51%,potential8.333GBnet
normalized32cache saving. OptinPREFLOP_MW_SLOT_STATS=1 usedinrawfallback-eight log.
Nevercompactassume beforeactualparity/timing. Instrumentationnotproductionrequired.

## Update 13:11 UTC

Current research HEAD3732885 applies static live-terminal worklists (new experiment).
Build session38054 compiles internal/preflopGPU tests and both frozen examples.
Run guarded internal GPU tests, ignored minimum-budget boundary, preflopGPU13,
then frozen8/7/6/3 measurements only if gates pass. Proposal terminal-cdf-base
is ready but separate; apply only after measuring worklist. Agent idle.

Retained GPU compact15ac951:8 median6238.7536ms,check8261.2487, estimated13075MB,
exact baselinearena/gaps/EV. 7=1507.6361ms,6=55.6132ms,3=2.3794ms. Repeat8needed.
Phase profiler5550a0b proved exactfingerprints: learningCDF2.54sec,terminal3.56sec;
checkCDF3.11sec,terminal5.09sec. Diagnostic only; not leaderboard productiontimings.

CPU clean423f58a restored byb4acd79. All36default testexecutables checked:
174passed,0failed,4ignored. Two fixture failures from wrongcwd resolved by running
identical preflop exe in crates/solver; run_guarded now accepts PREFLOP_TEST_CWD
and records cwd. Source5f55793 adds GPU-feature gate to frozenCUDAexample so
cargo test default builds. CPU reference2e-12passes. 3/4/6whole controls improve
22/32/26percent with exact root/gap/EV. Eight-opponent terminalmicro~5percent slower;
source-shape trials rejected.9limp-only baseline4105ms vsaf349candidate3506ms at
same20iters/0.004target; repeat with clean423source stillrequired.

Mainfindings.md and run.json updated; handoffolder sections are historical.
Mainlastpushed08662f6, researchlastpushedc235e2c; periodicpushdue.
Live56708 PID99216unchanged; guardsevery3sec. Deadline21:34:18UTC; do notendearly.

## Update 13:32 UTC

FullCPU174passed/4ignored. Main731f4e8 pushed, research3732885 pushed.
Worklist373 rejected ~1.5percent, restored1b52be6. CDFbasehoistdea49d1 candidate
8=6018.392ms/check7867.041, exactall4controls; largerrepeatstillneeded.
Active exec63797 runs sweep_cdf.py dea49d1:8warps215e8fe completedallgates/4controls,
16warpsc0cae8d currenttestscomplete/benchrunning; willthenrestore4warpsandrepeat.
Do noteditresearchsource until sweepfinishes. Scriptguardsjobs/deadline, records
commits/buildlogs/rawruns, verifiesexactoutputandrenders. Initialcontrollerassert
expected2hostcallsbutonecommonlaunch; fixedbeforeanysourceedit/benchmark.
New verify_gpu.py checksallcontrol arena/iteration/gaps/EV;40runs match sofar.
CPU9clean3559.392msvs4105.448base, exactgapsEV/root. compareCPUincludes9now.
Agents:preflop_kernel_review prepares pairedCPUcheckpoint proposalonly;
CPUallocation/reusemasses patchesready. multiway_validation prepares optional
hostkeycountsandopponent-count specialization; noagenthardwarejobs.
Remaining~8hours todeadline21:34:18UTC. App56708unchanged.

## Update 13:50 UTC

CDFsweepfinished;4warpsretained(21c1a6c),8/16marginal<2percentnotretained.
Newd3fd6cf addsallO21-caseGPUtests + opt-inhostkeycounts. Countzero withinpduplicates,
10.317percentcross-seatonly; no cacheimplementationplanned(3.43GBforatmostcheckgain).
Current2f415e4 specializesGPUqloopO2..8. Exact21,294f32directpayoffs vsdynamiccontrol,
internalgatespassand8/7/6/3arenas/gaps/EVmatch. Eight5461.9563ms/check7036.3546;
seven1368.4051/check3583.4519;six49.225/check81.0359;three1.314ms. Repeat8pending.
52cumulativeGPUrunsverifyexact. GPUcodegoodcandidatebutnotfinalintegrated.
CPU unchangedclean423. BaselineCPU3/4/6/9rerun cpu-paired-baseline-*.
CPU6/9memorybaselinecomplete(peakRSS54.7MB/15.5MB). Currentf88ac43 appliespaired
CPUcheckpointproposal; activeexec43991 compilesGPU-featurelib/prefloptestsand
bothfrozenbenchharnesses. Next run5pairedtests+fullpreflop56,then3/4/6/9CPU
pairedbenchwithRSS andcompareto cpu-paired-baseline-* / cpu-memory-baseline-*.
Pairedproposalreviewed:independentBR/avgneeds,exactf32gap,privatecancelOption;
noAPIorserverchange. Five focusedtests plusfullsuite/solve/RSSrequired.
NarrowCPUallocationandmasses patchesreadybutseparateexperimentslater.
Allagentscurrentlydone:modeled-fixturehelperready; forced-policy-budgetfixproposal
ready(andnecessarybefore modeledGPU:actualforcedVecbyteswereunbudgeted).
Inspectpatches/applyaccountingcommonfix toold/newkernelcontrolsformodelledperfs.
Researchsource2f415e4;mainlastpushed731f4e8,branchlastpushed3732885. Pushdue.
Liveapp56708notchanged;deadline21:34:18UTCstill~7h40remaining.

### 14:08 UTC continuation
Research HEAD739c68d compiling via exec88681. CPU paired f88ac43 passed7focused+56preflop tests, 4bench exact; reductions7-23%, checkpoint~half. 127630nodes4thread synthetic memory233.996MB→234.381MB exact. Forcedbudget8e7e4b0 passedhost/internal/boundary/GPU13. Fixture helper failed post-save due f32 JSON Value promotion; exact rawheaderpreserved; strictfix739c68d. Next run actualCUDAforcedbudget, generatefreshcoupled/freshlegacy/frozen modeled fixtures underlabtargetfixtures using newcoupledfilename, compare optimizedvsoriginalGPU+samebudgetfix fromproposals/original-modeled-budget-baseline. CurrentGPUoptionalPREFLOP_GPU_LAYOUT_STATS logsactualplannedstorage. Alluserworkuntouched. Deadline21:34:18UTC.

### 14:40 UTC
Research HEAD5cc6b3f is TEMPORARY ORIGINAL GPU control (bd03660wrapper+originalkernels+budgetfix), notretainedoptimized. RestoreGPUfilesfrom739c68d foroptimized. Newfrozencomparator8305245,budgetharnessd0a3466/5ccmanifestfix,buildharness5cc. Activeexec52860 originalbudget23GB6iter repeat, muchslower86-96seciter, mayhit600secguard; earlier19GB6iter passed6.58s,21GB6.60s. Original23first28s vsopt3.52 was memory-sensitive; doNOTclaimstable8x. Rawfullcomparator saved-comparator-modeled-a: maxpolicy0.282 at~1e-12reach, allfinite, gapsEV3e-8; selftestallbitsexact. Agentpreflop_kernel_review preparingcompatibilitybatchplan preservingoldB+cache atsamecorrectedbudget; multiway_validation diagnosticcap30readyagainst739c68d, plus frozenconvergenceharnessproposal. Nextafteractivequeue applycap30optimized, build, comparemodeled6fromfreshandfullarenas original30; longconvergencegates. Alsobuildownershipcandidateproposal andfrozenharnessready; baselineexe archivedtarget/research-binaries/build-control-5cc6b3f.exe manifestmainbuild-binaries.json, plan5pairedCPUfresh/loadtimingcontrols. Mainlatestcbc63fe pushed; research739c68d pushed, newercontrol/harnesscommitsnotyet. Userlive56708untouched. Deadline21:34:18UTC, ~6h54remain.
