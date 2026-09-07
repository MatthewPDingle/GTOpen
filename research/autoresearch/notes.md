# Research notes

Initial run: 2026-09-07 00:38:27-03:38:27 UTC. The append-only ledger and
raw logs are the measurement record. Updated during the second rotation.

## Retained paths

- Preflop CUDA: E001 captured per-seat sweeps; heads-up iteration 0.220 to
  0.094-0.100 ms. E007 compact shared reach: six-seat iteration 33.508 to
  23.784-24.037 ms; eight-seat 152.884 to 106.379-106.602 ms. All 2/6/8-seat
  arena/gap/EV fingerprints remain bit-identical. Next: cache each shared
  reach block's mass with the same 256-thread reduction order.
- CPU solving: E008 batches exact equity dot products across hero hands.
  Six-seat iteration 204.808 to 77.834-84.698 ms; check 1439.994 to
  325.655-338.982 ms. Full arena/gap/EV fingerprints unchanged; 124 CPU
  tests passed. E002 scratch pooling rejected (near-tie, slower checks).
- Memory and transfers: E003 reusable transactional pinned snapshots:
  six-seat sync 59.988 to 26.615-30.926 ms; eight-seat 150.459 to 67.568 ms.
  Tradeoff: pinned host RAM retained while engine lives equals arena bytes
  (224.55 MB for six seats, 587.24 MB for eight). Allocation failure retains
  the ordinary-memory fallback. E007 actual preflop VRAM: six-seat 1140.85
  to 603.98 MB; eight-seat 3590.32 to 1543.50 MB. No game simplification.
- Reports and profiles: E005 per-report lazy board classifications reduce
  report time 212.40 to 67.70-68.43 ms, with identical complete JSON hash.
  Next: profile raking, especially repeated allocations/divisions.
- Build/save/load: E006 direct f32 arena loading. Isolated paired warm-load
  control 54.134 ms / 198.885 MB peak working set; candidate 39.876 ms /
  172.012 MB. Identical bytes and loaded exploitability; eight save/lock/
  compatibility tests pass. Durability and format unchanged. Broad lifecycle
  timings are noisier than this dedicated 20-sample harness.

## Current postflop experiment

E009 compacts the already shared logical reach owners into dense physical
slots. Rainbow VRAM 7683.96 to 6274.68 MB; two-tone 7683.96 to 5637.14 MB.
First fixed-iteration timing is slower; time to the same 0.3 percent target
is unchanged (rainbow 12.244 vs 12.267 s; two-tone 7.346 vs 7.325 s, 200
iterations each). All GPU/private equivalence tests passed. B008 reruns the
original allocation to separate drift from cost. Retained and promoted after B008/E009R2 paired repeat: 58.918 vs 59.090 ms rainbow; 34.811 vs 34.924 ms two-tone.
E004 block sizes 256 and 64 were rejected; original 128 is restored.

Further candidates: compact active CFV slots; replace fold atomics with
preindexed card sums; specialize profile raking while preserving scalar
operation order; remove redundant preflop upload copies. Each requires its
own measured trial, correctness gates, and keep/discard decision.

## Harness notes

Global sequence includes baselines and repeats. Gray points are baselines
or metrics outside a trial's target; blue retained points need not be new
records; green is the running minimum of eligible measurements. The ledger
shows runs with no metric (e.g. E006W fixture path failure). Dedicated load
harness path was corrected before its first successful measurement, with
old/new hashes recorded. Benchmark definitions remain frozen thereafter.

## Third rotation, 02:14 UTC

- E010 retained/promoted: shared preflop reach masses computed once per down
  sweep, keeping the original 256-thread reduction order. Six-seat iteration
  19.145/19.257 ms, eight-seat 78.157/78.010 ms; exact arena/gap/EV fingerprints
  unchanged. 28 unit + 5 preflop GPU tests passed. Extra device memory is one
  f32 per shared reach block (less than 2 MB for eight seats).
- E011/E011B/E011C discarded: indexed f64 fold sums are too slow on this GPU,
  even after shared staging and a parallel total reduction (rainbow 114,114,
  69.6 ms vs about 59 ms). E011D retained/promoted: indexed fixed-order sums
  at the existing f32 precision. Warm repeat 56.643/33.599 ms rainbow/two-tone,
  check 35.059/28.463 ms. Time to identical 0.3-percent target 11.882/7.149 s,
  both 200 iterations. 28 unit + 6 GPU tests passed. Independent learning
  and shared/independent evaluations now compare bit-for-bit in the private
  GPU test. Original atomics caused run-to-run rounding noise; operation
  order changes, precision and accuracy targets do not.
- E012 retained/promoted: specialize profile raking at 2/3/4 actions. Full
  profiles 592.620/579.795 ms vs previous 648-681 ms. Frozen 512-case standalone
  raking control 5.683 to 4.629 ms, exact output hash aac3ae3fc5347b11.
  Profile/report/save fingerprints unchanged; unit and report tests passed.
- Current: baseline B010R for complete postflop save/EV fingerprints across
  12 board/isomorphism/rake cases and both unlocked/locked states. B010 failed
  to compile because the new harness used PathBuf with save(&str); fixed
  before any measurement and audited old/new hashes. Next E013 targets dense
  CFV slots only for visited GPU nodes. Main has no unvalidated candidate.

- E013 candidate: dense visited-node CFV slots. Complete saved bytes and
  exploitability bits match B010R on all 24 unlocked/locked states. Two-tone
  actual VRAM 5637.14 to 4932.50 MB (original B006 7683.96 MB); rainbow only
  saves about 34 MB because it has little suit sharing. First iteration
  57.56/34.06 ms vs retained fold baseline 56.64/33.60 ms; repeat and unit/GPU
  suites running. Do not claim speed improvement; this is a capacity trial.

## Fourth rotation, 02:39 UTC

- E013 retained/promoted: two-tone actual VRAM 4932.50 MB, repeat matches.
  All 24 complete saved states/EV bits match B010R; 28 unit + 6 GPU tests pass.
  Small measured iteration cost of 1-2 percent vs best pre-compaction repeat
  is recorded explicitly. This is a memory/capacity gain.
- E014 retained/promoted: remove temporary preflop upload copies. Warm init
  129-135 ms six-seat / 211-214 ms eight-seat vs B011 167/282 ms. All original
  2/6/8 fingerprints and 5 GPU tests pass. No new retained-memory cost.
- E015 retained/promoted: exact equity-vector cache by shared opponent reach,
  per-traverser work lists for learning and a union list for shared evaluation.
  Repeat six-seat iteration 19.29 ms (neutral), check 13.49 ms vs 24.45;
  eight-seat iteration 67.28 ms vs 78.01, check 41.82 ms vs 93.79.
  Actual VRAM 671.09/1711.28 MB (extra 67/168 MB), preferred estimate
  706.78/1750.51 MB; tight budgets omit cache and use direct calculation.
  Existing 700 MB six-seat test passes. All original fingerprints identical.
  Added cached-vs-direct checks in both graph learning and shared evaluation;
  three private GPU tests pass (E015-direct-equivalence.log). Warm init after
  new CUDA JIT is 136/230 ms. Small HU repeat normal, no heuristic needed.
- E016 integration in lab only: new GpuSolver::new_with_budget builds its
  actual plan once and checks compact staging plus full arenas and 512 MiB
  slack before device allocation. Interactive server uses it, enabling trees
  that the old conservative Spot estimate refused. E016 test failed because
  its new assertion assumed any suit symmetry saved memory (false on river);
  corrected assertion requires omitted nodes. E016R GPU/unit validation is
  running. Server GPU tests still needed before promote. Constructor new()
  retains unlimited-budget wrapper for reports/other existing callers.

Remaining run ends 03:38:27 UTC (about one hour left at this note). Next small
CPU trial: showdown_cfv can store its intermediate weaker-opponent mass in
its caller-provided output buffer, then overwrite each unique hand in the
reverse final pass; remove per-terminal Buf allocation/TLS access. Exact
operation order should remain unchanged. Compare frozen lifecycle fingerprints
and run full CPU suite if retained. A separate later idea is precomputed CPU
showdown group boundaries, but measure setup/load overhead too.

GPU regret/strategy arena compaction was inspected, not implemented: keeping
complete sync/save semantics would require preserving initial inactive arena
values when CPU queries materialize suit siblings mid-solve. Blind partial
scatter changes saved inactive bytes. Avoid that shortcut; a full solution
needs explicit host snapshot/memory tradeoff and broader resume tests.

Reserve final time for combined main CPU/GPU/server suites, aggregate accuracy
and time-to-target validation, documentation, chart render/visual review and
final source audit. All retained sources so far are in main except E016.

## Final comparison phase

E016R/E016S retained and promoted after 28 unit + 6 GPU + 1 server test pass.
E017 retained and promoted: CPU showdown output reuse, 25.11/25.49 ms vs fresh
26.05 ms control, exact lifecycle fingerprints and full 124 CPU tests pass.
E018 rejected after 25.22/25.58 ms near-tie; game.rs and GPU plan restored.

Final retained lab snapshot: f28e16f45f570cfd86f201b698dd1a1eb2816c86 (also in
run.json final_kept_commit). Main source hashes were checked against the lab.
Temporarily restore lab crates/solver/src and crates/server/src/main.rs from
bc192bf for fresh original-code controls B013 onward; keep all frozen harness
files. RESTORE THOSE SOURCE PATHS FROM final_kept_commit AFTER CONTROLS before
any promotion or final validation. Main stays on retained code throughout.
Baseline controls planned: preflop fixed target 0.03 total gap; CPU/lifecycle;
postflop 0.3-percent target; report adaptation; isolated warm load if useful.
Then restore retained source and repeat corresponding workloads + combined
main suites. Deadline remains 03:38:27 UTC. Do not finish prematurely.

Final source restored in lab at cd84600; it matches retained snapshot f28e16f. B013/F001 complete accuracy checks match exactly: six-seat 5.3922 to 3.2170 s (175 iterations), eight-seat 17.6992 to 7.9861 s (125 iterations), total gap target 0.03. Fresh original CPU/lifecycle B014, postflop target B015, report adaptation B016, isolated loader B017 retained in ledger.

03:19 UTC: main CPU 124/0, CUDA 40/0 (includes large 6/8-seat tight-budget exact equivalence), server 1/0 passed. Final review found a new E019 profile allocation reuse trial: 512-case hash remains exact; profile 551.84 -> 435.54/445.79 ms (19-21 percent less time). Main still prior kept snapshot until E019 correctness gates pass. Consider one bounded CPU AVX2 dispatch trial using portable fallback and unchanged multiply/add order; reserve time for affected full regression reruns and final documentation.

## Completed research run

All 20 numbered hypotheses have decisions; 17 retained implementation families, 87 recorded runs, 64 metric graphs. Final source snapshot a557aede88743db8efd29f99ef50833847918862 is in the isolated research branch and matches every promoted main source file. No temporary original-code control remains active. E019 profile aggregate reuse and E020 runtime vector dispatch were retained after repeats and exact equivalence checks. Final main suites with both included pass: CPU 124/0 (4 manual benchmarks ignored), CUDA-enabled 40/0 including large-budget fallback equivalence, server 1/0 (1 manual benchmark ignored). Final verification script passes 76 source, harness, numerical and suite checks. F008 resolves river checkpoint outlier at 0.555 ms; F009 repeats original exact preflop target states at 3.200/7.931 seconds. Full results in report.md, dashboard index.html, validation.json; incremental production patch in patches/final-retained.patch. Source changes remain uncommitted in main, user overnight scripts preserved, live desktop server was not restarted. Completion: 2026-09-07T03:37:15+00:00.

## GPU research pass 2 active

User authorized another approximately three hours focused on preflop CUDA, postflop CUDA and GPU memory. Start 03:57:10 UTC, deadline 06:57:10 UTC. Continue through this window across compactions; no agents or live-server restart. Baseline a557aede88743db8efd29f99ef50833847918862, first pass archived under passes/01-first-pass. Continue IDs B022/E021 onward and existing graphs. First trial: remove preflop full sigma cache, recompute sigma at own action nodes before their updates; expected 112/294 MB VRAM savings and less traffic. Next postflop ideas: specialize action arithmetic to avoid local-array spills; compact GPU action arenas with explicit preservation of inactive initial bits during readback, including compressed storage and CPU queries while the GPU engine lives. Frozen harnesses and main-source guards still apply.

04:19 UTC pass 2: E021 and E022 kept/promoted. E023 down-specialization candidate in LAB; E023R running. B025 fresh original-postflop kernel control complete; source restored to E023 at 9f... (query git). Do not promote original control. New frozen cuda_resources, postflop_resume_state (E022R reference), postflop_action_menus (B025 reference) in main+lab and run hashes. Prepared exact compact action-arena module in research/autoresearch/proposals/arena.rs; still not production. Implement after E023 decision. Deadline06:57:10Z.

04:29 UTC: E023 kept/promoted, final_kept_commit1d86527. E024A all 112 resume snapshots, queries and EV bits exact; saves1107.296 MB two-tone VRAM, step timings unchanged but init slower. E024B applies >=5% action-storage savings threshold, preserving direct upload on rainbow/noiso. Also all exact. B026 running original full-action host memory/lifecycle controls (new frozen postflop_memory_perf.rs), LAB mod.rs/plan.rs TEMPORARILY RESTORED FROM1d86527 at1e6124f; next restore mod.rs+plan.rs FROM e274391f6fe54ba1a0fcfcf28349c8d7f89a9219 BEFORE continuing candidate. New arena.rs still in lab, unreferenced by baseline. Main has no arena.rs yet; null source guard added, promote now checks explicit registered absence. After controls test OR-fold zero detection in snapshots (vectorizable) to reduce cold init. More preflop ideas: templated np2/6/8 terminal mass arrays; templated action counts; split non-reduction launch blocks from fixed256 reach mass. Deadline06:57:10Z.

04:33 UTC: E024C lifecycle exact vs B026 and resume controls, but F32 regresses
(host-live cold4463 vs3924MB, warm5729 vs3936; init1249/1614 vs653/652ms;
sync432/490 vs332/309ms). Compressed improves host5320 to2755/4155MB and init
1544/1586 to903/1337ms. DO NOT KEEP E024C as final. E024D (360ce0d) running:
reuse pinned buffer for packed uploads, merge consecutive F32 copies, snapshot
F32 directly without scratch copy, shrink snapshot vectors. No main promotion
yet for E024. B026 source restoration was undone; LAB mod/plan active candidate.

PROMISING NEW PATH after preflop: postflop CFV liveness reuse. Existing
postflop up sweep already processes fold/show/chance/action by descending
level. Keep terminal CFV slots unique and persistent (checks reuse them), but
reuse action/chance CFV scratch across same-parity levels. Allocate max action
+ chance width for even and odd depths, then unique terminal slots. Root must
remain slot0 for eval download. A parent only reads depth+1 children;
nonterminal depth+2 storage is dead. No new kernels, precision or sum-order
changes. Both iteration and eval code must be inspected to confirm scheduling.
Current plan unit asserting all visited slots distinct must instead validate
live-level uniqueness and terminal/scratch separation; frozen resume/state
harnesses use only sentinel checks and need no changes. plan.staging_bytes and
budget auto-adjust via cfv_blocks. Potential hundreds of MB beyond dense CFV.
Preflop analogous action-value liveness would need new val_slot indirection
(kernel overhead), so prioritize postflop first. Preflop speed next: template
pf_terminal on common np2/6/8 to remove local mass[10] array; then specialize
pf_down/up action counts and try per-kernel blocks while fixing reach-mass256.

04:43 UTC: E024F (28d36988) KEPT/PROMOTED all3 GPU sourcefiles, new arena.rs hashguardset. E024A/B/C/D/E rejected as superseded; E024 original build failure remainscrash. Finalpolicy defaultcompressedcompact, F32fullwhenfitsbudget(compactunderpressure). Exact112resume snapshots+queries/EV andB026 lifecyclechecks;29unit6GPU tests pass. E024F also establishes frozen preflop_variants baseline16casesx3phases (2..9seats,narrow/wide,plain/frozen/hero+locked). B027 running preflop perf+resourcescontrol session41748. Next apply research/autoresearch/proposals/preflop_terminal_np.cu toLABpreflop/kernels.cu asE025 afterB027. Postflop liveness proposal file prepared and includesupdatedunitliveness assertions; basedcurrentE024Fplan. Needapplyafterprefloptrial. Main stayskeptsource, liveuserdesktopuntouched. Deadline06:57:10Z. Labdecisionrender now~12sec aftermoregraphs; set yield_time_ms30000 andawaitsessionifrunningbefore anothermeasurement.

04:51 UTC: E025 main-dispatch terminal specialization and E025R gave3-6%
largepreflop iteration improvements, allfull/48variantstatesexact and5GPU+
budgettests pass. E025B refines to separate kernelentrypoints selectedonhost:
pf_terminalgenericresources46regs/40local unchanged; np2 47regs/0local,np6
64regs/0local,np8 56regs/0local. Fullfingerprints and48variantstatesexact,
6iteration17.535ms,8 59.263ms vsB02718.213/63.517. E025BR sessioncurrent
(runlistquery) repeatsfinalentrypoints+prefGPU/budget and collects postflop
perf/capacitycontrol before CFVreuse. LABHEAD8f2a92c; MAINstillE024F
28d36988. Nextapplyprepared postflop_cfv_liveness.rs to gpu/plan.rs asE026;
proposal includesfull-action policyhelper fromE024F andlive-levelunitassertions.

More bounded paths afterCFVreuse: (1) preflop terminal block-shared uniform
mass/probability to lowerregisters; (2) preflop2/3/4actionspecialization; (3)
GPU evaluation graphs. Both engines already have separate down/up routines.
Capture entire check with device-to-device root copies into small output
buffer, then single hostdownload; samekernelorder/f64hostdot order, invalidate
postflopgraphs onlockupdate. Preflop checkdown once, then eachseat terminals,
upBR/copy,upAVG/copy. Postflop downonce,BR/copy perplayer,AVG/copy ifrake.
Keepterminalcached betweenBR/AVG. Use eager first check to warmJIT before
capture, preserveunshared/eager unitcontrols. (4) For full/unpacked COMPRESSED
postflop arenas (rainbow/noiso), upload currentlystillallocateswholef32temp
andreadbackwrite_arena seriallyencodes. Reusealreadyallocatedpinnedbuffer to
decode directly andparallelizeper-node write_arena. Should extendmajorE024
host/transfergains to allboards. Existing16resume controls exercisefulliso-off
compressed. Measure freshserverreport_adaptation benchmark onrainbow before
that trial, existingfrozenserverharness. Deadline06:57:10Z; reserve~30minfinal.

05:00 UTC: E025B/E025BR kept+promoted preflopgpu.rs/kernels.cu; E025/E025R
supersededdiscard. final_kept_commit8f2a92c. E026 initialrunINVALIDATED:
Copy-Itempreservedproposalmtime4:42olderthancompiledrlib4:49, sointegration
benchmarksstaleevenwhileunittestbinaryrebuilt. NoE026sourcepromoted. lab.py
now refresh_build_inputs beforeeverycargo run: hash.rs/.cu/tests/examples,
Cargo files/benchspot; touchchangedcontents regardlessoriginalmtime using
LABtarget/autoresearch-input-hashes.json receipt. Firstuseforce-refreshedall
inputs. E026runstatusinconclusive; invalidate_measurements eventpreserves
originalnumbersinraw+event but removesfromgraphs. E026Aactualrebuiltcode
shows335.54MBrainbowVRAMsaving(6241->5905),201.33MBtwo-toneF32saving
(4932->4731),335.54MBnoiso(6275->5939). Step/check unchanged/slightlybetter.
All112resume snapshots+queries/EV and24originalstatechecks exact,29unitpass.
E026R currentrepeatdefaultcompressedmemorylifecycle+GPU6+postflopfixed
0.3%-pot target; contextdeadline06:57:10UTC. LABHEADbc699c7, MAIN8f2a92c.
NextafterE026decision: E027 optimizeFULL compressedpostflopupload/download
usingalreadyallocatedpinnedbuffer andparallelwrite_arena; firstB028server
report_adaptation_benchmark controlrainbowdefaultcompressed. Then preflop
commonaction specializations/block-sharedterminal uniforms and/orGPUevalgraphs.
Reserve~30minforfreshoriginal-vs-final targets,mainCPU/GPU/serverfullsuites,
newpassverification/report andgraphs. Don'tfinishbeforeapprox06:57.

05:35 UTC checkpoint: E027 full compressed transfer optimization retained/promoted (09ad3d1), E028 action specialization retained (a6a2e0a), E029 preflop eval graphs retained (1167a2f). Main matches all retained; run.json final_kept_commit1167a2f. E030 postflop eval graphs exact112resume/24state/24menu/target, river steady0.31ms vs0.58-0.82; first-call regression led E030A (e20667e) eager first check, steady0.31ms, first0.88ms. Large timings drift8%, so LAB temporarily restored gpu/mod.rs from1167a2f for B032 fresh postflop-check control + preflop perf/capacity. Restore E030A after control and repeat before decision. New gpu_check_perf frozen with first/second/steady bits. New validate_main_gpu_pass.py and verify_gpu_pass.py prepared; not run yet. The latter requires run.json pass_final_runs covering all state families and gpu-main-manifest source-attested final suites.
Prepared next proposals in research/autoresearch/: preflop-terminal-shared-proposal.cu (based E028 kernels); preflop-values-proposal.rs (based retainedE029 gpu.rs) and .cu (basedE028). Shared terminal proposal must be tried/decided BEFORE value addressing; if shared kept, regenerate value .cu transforms from current kernels, avoiding overwrite. ValuePlan merges linear level construction with alternate action scratch, terminal CFVs persist, root0; updates minimum estimate + slot table and adds liveness assertions in existing GPU test. None installed yet. E031 next hypothesis, E030AR next repeat, B033 next control. Deadline06:57:10Z; reserve final20-25min. No agents. Main user scripts and live server remain untouched.

06:06 UTC: main retained source through E035 (db5b25e): adds exact128-thread reach total mapping, unit30now (finalGPUminimum42). E033generic shared retained cf62471 with large9-seat251.8/252.7 vs290.7ms, allseatstaticE033Bdiscard. E034postcardrun rejected andpostCUDArestored. E035repeats6iter15.1ms,8iter52.9-53.5ms,9iter227.1ms, targets2.697/6.787s with original175/125iterations and states. Focused reduction tests include allpositivezero/allnegativezero/subnormal and mixed values vsoriginal256-lane f32 tree.
LAB currentE036 (8db273b) unroll4 pf_equities only; running session82811. Next E037 compare non-reduction global BLOCK192 vs128; prepared preflop-block192-proposal.rs/128.rs based currentE035; masskernel remainsexplicit128 so no summation change. Equityunroll8 proposal also exists, only try if useful. WARNING older preflop-equities-unroll-proposal.cu withoutfactor is based discarded allseatstaticcode; DO NOT apply it. Correct current unroll4/8 files created06:04 includeE033shared+E035mass.
Frozen generic preflop_perf3/5/7/9 baselineB033 now recorded; verifier preflopreferenceunionB022+B033. Optionalcuda_resources diagnosticextended for3/4/5/7/9, hashregistered. All GPUmemory/math refs asprevious. Deadline06:57:10Z, begin final checks by06:30 latest. Need final freshpass-starta557 vsretained target comparisons, allstatefamiliesG001/G002/G003, main full CPU/GPU/server via validate_main_gpu_pass.py, pass_final_runs config, verify_gpu_pass.py, finalreport/graphs visualreview andpatch. Main sourceguardstilltrue, live serveruntouched, overnight scriptsuntouched.

06:22 UTC: E036unroll4 discarded (4-5% slower, all exact). E037192/B128/C64 all exact; adaptiveE037D uses256threads for fewerthan256blocks and64otherwise, with massalwaysfixed128. D isbest:6iter12.734,8iter41.536,9iter184.509ms;2seat0.081ms. CurrentLAB76ca9e7, repeatE037DR session81388 includesallfullperf+targets+GPU/budget and freshpostcompressedmemory/fullmemory controls (untargeted gray). Afterrepeat decideD/DRkeep, E037/B/Cdiscardassuperseded andpromote preflopgpu.rs+kernels.cu. MainstillE035db5b25e.
Last planned hypothesisE038: postflop-parallel-upload-proposal.rs isforgpu/arena.rs, paralleldecode disjoint65536-float pinnedchunks withnode-scale boundarylookup; smallbuffers retainserialpath. IncludesnewCPUunit crossingnode boundaries/hostgaps atdifferentI16/U16scales. CompareE038 againstmemorymetricsfromE037DR, then repeat+serverbenchmark ifgood. Final sourcefreeze by06:30latest. README/docs nowlinkpass2; liveappGET06:20 stillpostidle0/prestopped750, untouched.

06:36 UTC checkpoint: E037D/DR retained and promoted. E038 parallel upload rejected (all compressed initialization cases 2-11% slower, exact112resume and large EV); its actual compiled source523c8d4 is corrected by append-only source_attribution event (proposal was committed during compilation, no bytes changed). Final main source e6a4ada (E037D plus comment/indent cleanup), main guards updated. Actual main CPU124/GPU42/server1 suites ALL PASSED, source-attested gpu-main-manifest.json complete. Final research pipeline final_gpu_research.py running session52456: B034 restores pass-starta557 CUDA5files, benchmarks preflop full/generic/targets/capacity and postflop convergence; then restores e6a4ada, runs G001 preflop states/targets, G002 post states/resume/menus/convergence, G003 capacity/memory/checks, G004 server. Configpass_final_runs set afterpipeline. All hardware serial. Important: postflop_perf convergence mode omits fixed65iteration metrics/checks; need additional fresh baseline B035 and final G005 normal postflop_perf to cover required postflop fingerprint and compare fixed-step performance. About20min remain before06:57:10. Decide finalG runs only afterexact comparisons; verify_gpu_pass.py requiresallfamilies/manifest/decisions, then writesgpu-validation.json. Current mainunchanged, LABtemporarilyB034 source. Need finalreport rewrite gpu-pass.md (preservechronology separately), finalpatch/graphs/visualcheck. Graphpasslegend added, tracker status nowconfig-driven. No new implementation ideas; spendremainingtime repeatcomparison/report.

06:54 UTC: all implementation and validation work complete. Final retained tree d3ff6d6; actual main CPU124/GPU42/server1 passed, G001-G005 all retained after exact comparisons. B034/B035 fresh pass-start controls attest original source. gpu-validation.json now696 source/numerical checks and130metricgraphs. Finalreport gpu-pass.md generated fromrecords, patch77696bytesattested. Graphlegendspacing visuallyfixed andall353tracker/55reportlinksverified. FinalGPUprofile remainingpostshow/upactiondominant documented in gpu-pass-handoff.md. Beforefinal: setrunstatuscomplete, addpasscompletionevent, finalrender, archivepass2snapshot; liveappstillidle0/prestopped750, untouched. Deadline06:57:10. No pendingexperiments/processes.
