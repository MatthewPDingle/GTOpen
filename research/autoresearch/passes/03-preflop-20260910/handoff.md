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
