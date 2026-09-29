# Active handoff: longer matched river continuation

Verified 28 September 2026, approximately 23:13 Adelaide.
The broad preflop-quality goal remains active and incomplete.

## Completed work

The two-update matched pilot and its independent readback finished successfully.
See RIVER-MATCHED-PILOT-FINDINGS.md. All eight registered comparisons are
inconclusive; no playing-strength or preflop-accuracy improvement is established.

The complete four/eight-worker control also finished successfully, exec 23567
exit 0. Do not restart that job. All checkpoints and ordered artifacts were
identical to the original update. Its paired wall times were:

- Baseline: 56.297 seconds with four workers, 55.312 with eight.
- River candidate: 247.750 seconds with four, 169.765 with eight.

The candidate used 31.5% less time (1.459x throughput) in one paired replay.
This is descriptive evidence, not a universal or statistically precise speedup.
Result: eight-worker-full-update-control-v1-result.json. Stored allocation
885,984,954 bytes, logical 2,063,708,180. No fresh test deals were used.

Commit 63fbd9cc records this result, the continuation runner/reviewer/plan and
a pure synthetic analysis control. All five committed raw files matched disk.
The synthetic control covered zero variance, a rare tail, eight contrasts,
independent scalar readback, corrupt-output rejection and wrong-count rejection.
No production code, deployment, additional GitHub push or historical deletion.

## Current live process — do not duplicate

- Exec session: **82879**.
- Python PID: **53388**; creation Unix **1790602757.6862433**.
- Command: `river_matched_continuation_v1.py --run --wait` using
  `C:/Program Files/Python312/python.exe -B`.
- Exact command, creation identity and live handle were independently verified.
- Current status: A-baseline training update 81; saved boundary 80.
- Store: `S:/GTOpen-research/weighted-complete-river-continuation-v1`.
- Status: `river-matched-continuation-v1-status.json` in this directory.
- Registration SHA256:
  `6b4b4dec4d0580d3aed5b3c2a38361eb91a58ab5dee778d929b919408ebbf14a`.
- Fresh global allocation scan passed: 721,534,139,377 bytes already allocated,
  plus 64,000,000,000 reserved, below the 800,000,000,000 global cap.

Readiness verified all frozen source dependencies, parent states and qualified
shared-query evidence. The runner and reviewer are now frozen by registration.
Do not edit them while this run is active or rewrite registered evidence.

The fixed plan continues all four parent arms 80 to 110, using eight physical
workers/four board workers. That is 120 new learning updates total. Fixed order:
A-baseline, A-river, B-river, B-baseline. The final evaluation uses 16,384 fresh
common deals, seed 9294101, full played models 0..109; model 110 is excluded.
Training and evaluation may take several hours. An invocation stops at eight
hours and preserves published boundaries; that is not a completion-time promise.
Light desktop GPU sharing, production priority and storage/memory guards remain.

The primary conservative intervals remain unchanged. A separately registered
normal approximation and tail diagnostics are exploratory only, conditional on
frozen banks; they are not finite-sample guarantees or training-seed uncertainty.
Do not select a favorable seed/seat, change the test budget from outcomes, or
promote on these results alone. See RIVER-MATCHED-CONTINUATION-PLAN.md.

## Next actions

1. Poll the existing exec handle and compact status. Verify exact process identity
   before restarting or treating missing output as failure.
2. Resume with `--run --resume --wait` only after authoritative terminal evidence.
   Preserve partial attempts; only published verified boundaries are reused.
3. After result completion and process exit, run
   `river_matched_continuation_review_v1.py --run` as a separate CPU process.
   It verifies the complete archived evaluation, checkpoints, parent continuity,
   scalar statistics, propagation snapshots and secondary tail diagnostics.
4. Report every seed/seat, uncertainty and cost. Decide whether further work on
   this river treatment is justified. Equal-time and broader stack/rake/sizing/
   multiway validation remain necessary. No broad accuracy claim is earned yet.

Original pilot handles 22398 and 13146 and worker-control handle 23567 have
all completed with exit 0. The older RIVER-MATCHED-PILOT-RUNNING.md ends with
the now-finished worker control; this document supersedes that live-job pointer.

## Follow-up preparation while the continuation trains

The same live session 82879 / PID 53388 progressed through at least 94 updates
(14 new A-baseline rounds); later progress is in the atomic status/checkpoints.
No active-study implementation, settings or analysis changed.

Commit 6ebbc93b adds river_matched_continuation_report_v1.py. After the final
independent review passes, run it with --write to produce
RIVER-MATCHED-CONTINUATION-FINDINGS.md. It authenticates the result/readback
chain and presents all eight primary and exploratory comparisons, learning cost,
preflop propagation and tail diagnostics. It refuses partial-outcome reporting.

Commit 56452604 records an isolated CPU optimization and complete evidence:
VISIBLE-FEATURE-VECTOR-FINDINGS.md and visible-features-vector-control-v1-*.json.
The CPU control handle 31141 exited 0. All 1,558,846 rows across eight immutable
parent reservoirs matched the original 302 float32 features byte for byte;
full feature preparation was 2.32-4.26x faster in one paired observation per
fixture. Synthetic card-category/invariance/invalid-input controls also passed.
The source objective/fitter copies are prepared but NOT GPU-qualified or used
in the active continuation. See that findings document for the exact next
fit-parity and complete-update checks. Do not start competing GPU work or
retrofit this runtime into the registered experiment. This is an execution
optimization, not evidence of improved poker play. No push or deployment.

## First baseline complete; candidate continuation started

Exec 82879 / PID 53388 remains live. A-baseline reached boundary 110, saving all
30 new rounds. Recorded update time totals 1,801.845 seconds; recorded competing
GPU wait totals 1.967 seconds. Checkpoint verification and orchestration add wall
time beyond the per-update metric. This is a cost observation, not an accuracy
result. The current stage is A-river update 81 (status Unix 1790605233.38394).
B-river, B-baseline, the frozen fresh evaluation and independent review remain.
The bounded monitoring exec cell 2008 completed after seeing A-baseline 110;
it was only a watcher, not a separate research process. Continue polling 82879.

Commit 68d2ad04 adds visible_features_vector_gpu_control_v1.py and
VISIBLE-FEATURE-VECTOR-GPU-PLAN.md. Read-only preflight passed all eight saved
reservoir fixtures and correctly reported the occupied research lock; no GPU
fits were started. After the active study releases GPU resources, --run will
require both original and vector fits to exactly reproduce the saved model-80
networks, scales and non-timing fit metrics, using the original seeds/settings.
A passing fit control still needs complete-update/checkpoint parity before
future adoption. Keep the currently registered experiment unchanged.

## First seed finished; second seed running

Both A-baseline and A-river reached verified checkpoint 110 (30 new rounds each).
Recorded update time totals are 1,801.845 and 5,544.326 seconds. B-river has
started; read the atomic status and progress files for its current boundary.
Main exec 82879 / PID 53388 is still the live study. Monitoring cell 2043 ended
its bounded watch; that was not the study ending. Do not wait on it again.

A small CPU-only reuse diagnostic is recorded in RIVER-QUERY-REUSE-AUDIT.md.
All 38 native exports of a fixed historical batch matched their archived bytes;
9.82% of 916,635 query rows repeated canonical visible inputs. This is not
caching performance or evidence of better poker play. The earlier four-export
audit is preserved. The full diagnostic's exec 24464 exited 0. It took 47.656
seconds on one CPU worker and overlapped live training; the result timestamps
record that overlap. No scientific sources, settings, training or evaluation
changed, and no GPU fit controls have been started. Whole-policy-query caching
is not currently a strong large-speedup lead from this one batch.

Continue the registered B-river and B-baseline arms, fresh evaluation, independent
readback and report. GPU vector-fit qualification remains queued until the main
study releases its GPU resources. No new push or deployment.

## Isolated CPU preparation candidate qualified on one archived batch

Main exec 82879 / PID 53388 remains the live continuation. Latest checked
boundary: A-baseline 110, A-river 110, B-river 87; status shows B-river update
88 in progress. B-baseline and the final evaluation/review remain outstanding.

See RIVER-QUERY-PREPARATION-FINDINGS.md. A four-export CPU profile (exec 83243,
exit 0) identified repeated validation/table scans. The new isolated
river_query_preflop_subset_v1.py applies the same tables only to preflop rows
after unchanged array/history validation and a full key/phase check.

The full fixed archived-batch control (exec 84986, exit 0) passed 38 exports,
916,635 query rows, exact prepared arrays and archived policy bytes, and twelve
invalid-input rejections. Preparation sums were 39.865 versus 21.130 seconds
(1.887x observed ratio), under concurrent study load and only one paired timing
per export. This is not full-update performance or poker-accuracy evidence.
Both helpers are finished; no new GPU task was started. Their overlap timestamps
are in their results. The current scientific sources/settings remain unchanged.

Before future adoption, qualify broader models and complete target-generation /
update equality. The separate GPU vector-fit control is still queued for after
the main study releases its GPU resources. Continue polling the same main
session; do not duplicate it. No new push or deployment.

## Downstream subset-preparation replay passed

The isolated CPU target-calculation control completed (exec 17104, exit 0).
It replayed A-river update 79 batch 00 and B-river update 80 batch 00, using
models 78 and 79. All 1,529 river target rows and all 249 output-file bytes
matched their original archives. A separate file-list/hash readback passed.
Evidence and limitations are appended to RIVER-QUERY-PREPARATION-FINDINGS.md;
control registration SHA256 is
fe5acec47b556e2c1e0962273802551a9d30cddd2c992cf98a95d1ca3352cbe9.
The candidate-only replay retained 16.12 MB and did not use GPU or new deals.

Main study session 82879 / PID 53388 is still live. Latest confirmed completed
B-river update is 91; atomic status shows update 92 running. A-baseline/A-river
remain complete at 110, and B-baseline has not started. Re-poll the same live
session for newer boundaries. No monitoring timeout is a terminal study state.

Next: finish the registered study and independent evaluation review. The
preparation candidate still needs complete-update/checkpoint equality before
adoption; the feature-vector GPU fit control also remains queued. Do not change
the running study or start competing GPU controls. No push or deployment.

## Complete-update qualification prepared, not run

Prepared training_preparation_full_update_control_v1.py and
TRAINING-PREPARATION-FULL-UPDATE-PLAN.md. Source-only preflight completed
(exec 80489, exit 0), reported the occupied research lock, and correctly listed
continuation, continuation review and GPU fit control as pending. No GPU work,
new registration, new storage directory or training replay was started.

After the matched study and independent review finish, run the existing
visible_features_vector_gpu_control_v1.py --run first. Only after all eight
saved-network/fit-metric checks pass, run
training_preparation_full_update_control_v1.py --run. It compares four complete
A-seed update-79 replays (baseline reference/candidate, river candidate/reference)
with their original saved oracle, using eight physical/four board workers.
It requires full checkpoint/restored-state/artifact and numeric-fit equality.

The candidate pipeline copies differ only in the fit-preparation import, plus
the river subset pool import. The new pool retains the original initialization
and binds subset preparation to the worker's engine instance. Original live
pipeline/worker/fitter files remain unchanged. The plan has production/GPU
priority and 12 GB plus 2 GB reserve within the global 800 GB allocated cap.
Preserve failed attempts; the queued control does not automatically retry.

Main exec 82879 / PID 53388 is still running. Latest confirmed B-river boundary
is 97 (77/120 new study updates overall); re-read actual status for current
progress. Do not start queued GPU controls while this session remains live.
No push or deployment.

## Findings timing labels clarified before final evaluation

The report generator now labels metrics.seconds sums as training-pipeline time,
not total elapsed training/research time. Source inspection showed the runner's
checkpoint restore/compare_states, progress publication and cleanup happen after
the pipeline timer. Parent copying, admission, evaluation and independent review
are also outside those sums. The separately recorded GPU wait counter is not
subtracted to invent pure compute time. Numerical evidence and the registered
study, pipelines and reviewer are unchanged; the report generator is not a
registered study input. This wording correction does not establish a new speedup.

## Checkpoint readback candidate: historical CPU parity passed

A separate CPU profile (exec 50466, exit 0) located row-by-row reservoir validation
as a substantial checkpoint-readback cost. The isolated bulk-validation loader and
complete restore wrapper then passed exec 92362 (exit 0): eight reservoirs with
1,657,939 rows, four complete parent-80 checkpoint states, three valid synthetic
archives and 36 invalid-archive rejections. Full checkpoint timing pairs totaled
49.063 seconds original versus 21.795 candidate under concurrent load. This is
component evidence, not full-training performance or poker-accuracy evidence.

See CHECKPOINT-RESTORE-VECTOR-FINDINGS.md. Registration SHA256:
23f066326dfdf8ab69a8ad8a8886ce877529be5d3caf7ccd9c169942800454b3.
The candidate preserves the original reservoir type and all original full
checkpoint checks; an AST check limits the wrapper change to the loader call.
It has not been substituted into the registered scientific run or queued GPU
controls. Future runner integration still needs qualification. Both CPU helpers
are finished; overlap timestamps are in the evidence. No new large artifacts.

Main session 82879 remains live, now in B-baseline (latest observed completion
97; re-poll for the current boundary). Current watcher is functions cell 2135.
Finish the existing study and independent review, then the prepared GPU feature
fit/full-update controls. Do not restart because a monitor yields or times out.
No new push or deployment.

## Training and evaluation finished; independent review running

Main session 82879 exited 0 after all four arms completed boundary 110 and all
16,384 fresh evaluation deals finished. Do not restart that completed run.
river-matched-continuation-v1-result.json reports passed/complete, with
accuracy_qualified=false and independent analysis still required. Its SHA256 is
e0a81a258b3189047c3cfee9581a0ef6496eacdddc686b2c4f15c32dea1eaf95.
Recorded invocation time is 21,405.969 seconds; this is broader than the pipeline
timing sums, and does not include the subsequent independent review.

The registered reviewer is now running as unified exec session 46414, PID 89012,
process creation time 1790624365.0911193. Its read-only preflight passed; no earlier
review registration/result existed. The current review watcher is functions cell
2171. Poll the same reviewer session and require an authoritative terminal result
before proceeding. A monitor yield or timeout does not imply reviewer termination.

After review passes, run river_matched_continuation_report_v1.py --write and assess
all seeds/seats, uncertainty, tails and learning cost. Then run the prepared GPU
feature-fit and complete-update controls. The separate bulk checkpoint loader is
also tested on historical states but has not replaced any live study source.
The broad preflop modeling goal remains incomplete. No new push or deployment.

## Independent review and decision complete; GPU fit control running

This section supersedes the earlier running-review handoff. Session 46414 exited
0. Independent review passed all 512 batches / 16,384 deals / 7,443,270
observations. Review SHA256:
8676d3ae76e0c3d026fecc468b3052278dd8ff06a6816463a16049bc3bede5fb.
The generated findings and separate decision are now recorded in
RIVER-MATCHED-CONTINUATION-FINDINGS.md and
RIVER-MATCHED-CONTINUATION-DECISION.md.

All eight point estimates favor the candidate, but all eight primary intervals
include zero. Only the two correlated B-seed BTN exploratory normal intervals
exclude zero. Training pipeline cost is approximately 2.8-3.1 times baseline.
Do not promote this as proven range improvement or deploy it. Preserve the study
and finish the prepared runtime controls before planning an equal-cost comparison
and better evaluation precision. The broad goal remains active.

visible_features_vector_gpu_control_v1.py --run is running in unified exec
session 31237 after a successful read-only preflight. It permits light desktop
use and yields to production/heavy work. Await its authoritative exit; do not
restart on a monitor timeout. If all eight saved-network and numerical-fit
comparisons pass, run training_preparation_full_update_control_v1.py preflight
and then its --run mode. No simultaneous GPU controls, push or deployment.

## GPU fit control complete; complete-update control running

Session 31237 exited 0. All eight reference/vector fits exactly reproduced the
saved model-80 networks and non-timing numerical metrics. Result SHA256:
1996352403a5586faffbebb10266f4ee8fe24f4879efb4dc7a852c50ff3420f4.
See VISIBLE-FEATURE-VECTOR-GPU-FINDINGS.md: aggregate measured fit time fell from
93.514 to 64.111 seconds, but this is not a full-training speed claim.

training_preparation_full_update_control_v1.py passed its source/prerequisite
preflight (no pending gates, research locks clear). Its --run invocation is now
unified exec session 79637. Await that same process and preserve all attempt
records. Initial global storage inventory can take several minutes before the
first case starts. Do not mistake quiet output for a stopped process.

Require an authoritative terminal exit and all four archived-update matches
before adoption in a future versioned study. No current scientific inputs,
production sessions, push or deployment have changed. The checkpoint bulk loader
remains separately qualified only against historical states, not integrated here.

## Complete-update qualification finished; next experiment is not started

Session 79637 exited 0; PID 74416 is gone. All four reference/candidate update-79
replays passed exact oracle/checkpoint/state/artifact/numerical-fit comparisons.
Result SHA256:
5d8c3f22a6270ee95111e3e8c32a50828cfdac4bcf2e253fd5b295661ab282ef.
Registration SHA256:
0f8ce077c79297513231a2edb8eceb2e3335f8db72865632c24eb17230f6e249.
A separate readback checked registration binding, four metric/checkpoint digests,
completion markers, all physical subbatch artifacts and timing arithmetic.

See TRAINING-PREPARATION-FULL-UPDATE-FINDINGS.md. Pipeline times were baseline
59.500 -> 49.625 seconds (16.60% less) and river 181.312 -> 171.250 seconds
(5.55% less). Total control invocation: 928.437 seconds. Retained evidence:
2.064 GB logical / 0.886 GB allocated. Do not equate pipeline time with whole
research elapsed time or infer poker accuracy from parity.

No study or control is currently running. All prior sessions/watchers are
terminal, including functions cell 2212. Do not restart completed controls.
The qualified preparation pipelines are eligible for a future versioned study;
the bulk checkpoint loader and JSON snapshot candidates remain separate.

Next: implement and freeze the bounded serial-versus-concurrent two-arm control
specified in TWO-ARM-TRAINING-THROUGHPUT-DESIGN.md. No runner for it exists yet.
It must preserve exact original updates, own its children, respect production and
combined GPU/storage budgets, and measure comparable timed regions. The point is
research throughput while keeping learning unchanged, not utilization for its
own sake. If the effect is weak, retain serial execution rather than repeat
standalone controls indefinitely.

The scientific decision remains RIVER-MATCHED-CONTINUATION-DECISION.md: all eight
quality point estimates positive but all primary intervals inconclusive; no
accuracy promotion. Improve evaluation precision and compare similar compute
budgets before another expensive quality study; broader stack/context modeling
remains required. Goal active. No new push, deployment or production changes.

## 2026-09-29: two-arm throughput and first precision controls finished

Session 63870 exited 0. Parent PID 95484 and all four child coordinators exited;
the final owned job reports zero active processes. No benchmark is running.
Do not restart this or any earlier completed control.

TWO-ARM-TRAINING-THROUGHPUT-FINDINGS.md records exact original-update parity for
all four cases and an independent 2,128-artifact readback. Serial update calls
summed to 241.030 seconds; concurrent makespan was 205.912 seconds: 14.57% less
elapsed time (1.171x pair throughput). Individual concurrent updates were slower;
this is a single-pair research-throughput result, not production-solve latency.
Whole invocation took 1,213.297 seconds, including two global storage inventories,
setup and verification. Final global allocated research storage: 740.141 GB.

Result SHA256: e6b0b0e6cc835c1aace7737e627a6396fe932170326f1c020c2dd879ae74f782.
Registration SHA256: e164546be2e6f0c06e66eb86b6a487103167f85a83d0647555e487f19a0872e1.
Readback: two-arm-training-throughput-control-v1-readback-v1.json.
The two initial direct invocations declined resource admission before creating
registration/work. The bounded admission wrapper then passed unchanged checks.
Light desktop GPU sharing is enabled; active production/heavy work retains priority.

Next priority is REACH-WEIGHTED-EVALUATION-DESIGN.md. Existing evaluation already
integrates preflop all-in runouts; improve private-pair/postflop sampling rather
than repeat that integration. The complete 110-model bank has shared mass 632/1221,
so the earlier one-update 9.89bb mixture bound does not apply: its conservative
metadata bound is now approximately 193.20bb. Old intervals remain unchanged.

The exact-rational proposal prototype passed 512 expectation equalities and
7,248 pointwise bounds in 0.17 seconds, with no poker data or GPU. It is not yet
a qualified floating-point sampler or native poker estimator.

The next prerequisite also passed: complete_preflop_query_catalog_v1.py builds
699 supported queries across all five preflop decisions from the retained native
6,630-row physical catalog. Control v3 checked 488 native observations and 220
own-history links on 128 retained training deals, plus six negative cases.
See COMPLETE-PREFLOP-QUERY-CATALOG-FINDINGS.md. V1 and V2 failed only because the
control first used queries without histories, then a labelled format-3 input for
a format-2 exporter. Preserve both earlier versions/registrations/artifacts.

Next concrete work: extract all four frozen 110-model complete-bank preflop
policies using the checked query catalog, original root-catalog metadata and
unchanged own-history-weighted inference. Verify CPU/CUDA agreement and native
reach/terminal decomposition before forming the deterministic proposal envelope.
Reuse board_root_components_v1.py and the class-pair/all-in matrix where their
checked scope applies; do not assume a new class reduction without validation.
The existing 60-input public-economics descriptor and seven native stack-geometry
fixtures are already available. Cross-context learned ranges remain outstanding.

Scientific quality remains promising but inconclusive. Goal active. No production
model/session change, deployment or new GitHub push. New research changes are
committed locally on codex/continuation-symmetry-research.

## 2026-09-29: complete banks exported; simple reach-envelope path stopped

Session 42080 exited 0. Complete preflop exports passed for A-baseline, A-river,
B-baseline and B-river, 110 played models / 699 supported queries each. No study
or control remains running. Registration SHA256:
7e693318b0a18fa664d423f7f7d23f73550211a1323c4fc4ea07c9313d38daeb.
Maximum CPU/CUDA policy difference 3.47e-18, own reach identical. Output:
S:/GTOpen-research/complete-preflop-bank-export-control-v1 (0.26 MB allocated).
Do not restart completed controls or restore reservoirs just to inspect policies.

preflop_proposal_envelope_screen_v1.py passed its native decomposition check on
all eight frozen profiles / 24 forced postflop leaf profiles, using one retained
training deal. Its registration SHA256:
01420ce70189e73cfdbadad1126f25488503623f54944adfa67c1008cd0478a5.
The deterministic planning result is disappointing: Z=249.59970460035993 bb,
versus the existing mixture planning bound 193.19778869778872. At n=16384 its
additive Bernstein term alone would be 0.4593974989 bb per entry. Do not launch a
fresh expensive evaluation using this simple reach-only proposal. It is neither
a qualified sampler nor a rigorous floating-point bound. Preserve old intervals.

Independent preflop_export_envelope_readback_v1.py checked 600 files, including
440 played-model references, and recomputed C/Z via closed-form CPU arithmetic;
maximum error 2.85e-14. See COMPLETE-PREFLOP-EXPORT-AND-ENVELOPE-FINDINGS.md.
Executed sources and evidence are immutable. Both export and screen passed first
run, with no fresh poker deals, training changes or production changes.

Next concrete work: resume STACK-CONTEXT-PLAN.md. Read existing
sampled_public_economics_features_v1.py (60 public inputs),
sampled_visible_features_bulk_v1.py (302 existing inputs),
hu_stack_geometry_control_20260923.py and its seven verified native contexts.
The geometry fixtures have uniform incoming policies, not learned ranges, and
their query files contain public actor/phase/hi/n only, not private-card features.
Do not feed those directly into the existing visible-feature encoder.

Build a versioned cross-context observation/table/checkpoint contract that keeps
each context hash in cache/table/history identity while supplying actual public
stack/price/action inputs to the shared network. Preserve context-mismatch and
hidden-information checks. Then establish small fixed-context reference runs and
a bounded shared-model pilot; hold out 60 and 150 bb from fitting/tuning. Broad
strategic accuracy and full-tree preflop ranges remain unproven. Do not confuse
the earlier negative 12-input fixed-depth test with a multi-depth experiment.

Light desktop/video GPU sharing remains enabled. Active solves/heavy work take
priority, 4GB combined research CUDA budget / 2GB external headroom, 800GB global
allocated-storage cap, hidden helpers. Latest admission allocation 740.159GB.
Goal remains active. No new GitHub push, deployment or app-session changes.


## 2026-09-29: shared stack input/model interface passed; exact reference next

Session 28703 exited 0. PID 99576's completed stack-context control is terminal;
do not restart it. The independent stack_context_model_readback_v1.py also
exited 0. No experiment is currently running.

STACK-CONTEXT-MODEL-FINDINGS.md records seven depths (20/40/60/100/150/200/400),
5,028 observations, 2,514 public states and 17,724 own-history links from TWO
retained physical deals. All context-qualified keys were distinct despite 3,996
collisions without context. Maximum CPU/CUDA error 4.44e-16. Independent readback
verified 156 files, exact public scalar features and synthetic root inference.
Control registration SHA256:
c6f728a810612b77df1569c2afbc65eff92031cf92aabc81617da394df6f94bd.
Registry SHA256:
463a5e81abe01279b6fa3be79d37e5edb25041c086a39bb9789559a1ec7f6943.
Evidence occupies 1.36 MB allocated. No training or fresh evaluation deals.

New immutable interfaces: stack_context_inputs_v1.py (302+60 inputs, explicit
context routing) and stack_context_policy_v1.py (shared networks, context-local
preflop tables, own-reach model averaging, hashed model objects). These are NOT
resumable training checkpoints. Holdout roles for 60/150 bb are enforced. The
synthetic test policies say nothing about poker accuracy or depth generalization.
Existing grouped reservoirs lack own histories required by Registry.prepare;
introduce an explicit versioned training adapter rather than fake inference
histories when fitting is implemented.

Next concrete work: STACK-PRICE-REFERENCE-DESIGN.md. This reconciles the last
handoff's stack-interface work with the earlier quality gate: do NOT launch a
large seven-depth self-play run yet. First qualify a restricted real-Hold'em
river call/fold reference with enumerated uniform-opponent values, native legal
states and independently checked cash flows. Verify price coverage before
choosing the fixed dataset. Plan is design only, not registered/executed. Then
freeze a bounded learning comparison and test held-out depths. Passing it will
not certify full preflop or multiway strategies.

Light desktop/video GPU sharing is verified enabled in the research admission
code (<65% external utilization after yielding, 4GB research CUDA/2GB headroom).
Production solves/heavy work retain priority. Preserve all historical files,
executed sources, 800GB global storage cap and hidden helpers. Goal remains
active. No deployment, app-session change or new GitHub push.

## 2026-09-29: exact river reference qualified; supervised comparison next

Session 44026 exited 0; coordinator PID 100172 and all owned descendants are
terminal. Independent readback exited 0. No experiment currently runs. Do not
restart completed controls. Latest local prior commit is bdb1b33c; the current
reference milestone is being committed separately.

STACK-PRICE-REFERENCE-FINDINGS.md records first-run agreement across 476 native
terminal fold/call states at fitting depths 20/40/100/200/400, twelve probe boards,
12,972 hero holdings and 12,842,280 legal directed private-hand pairings. The
independent evaluator maximizes every five-card subset. All 6,174,672 call values
matched the separate equity formula (1.14e-13 bb maximum). Exact-rational readback
checked 22,848 selected values / 204 files (3.56e-15 bb maximum discrepancy).
Registration SHA256:
aad577169e3c0cc688cd0ef988bc4db64c070515d2227ae3b1605804cca5801e.

Probe-only canonical board groups live in the registration and reference files;
exclude them from subsequent fitting, validation and final test. 60/150 bb labels
remain untouched. Uniform opponent holdings are a diagnostic assumption, not
the range induced by actual betting. Native river states can face non-all-in
bets too; do not call all of them jams. No model fitting has happened yet.

New immutable modules: stack_price_reference_v1.py (independent five-card rank,
legal-pair enumeration, exact-price call advantage/regret),
stack_price_reference_control_v1.py (eight hidden workers / native qualification),
stack_price_reference_readback_v1.py (artifact/rational readback).
Probe evidence occupies 0.337 MB allocated. Global allocation at admission:
740.163 GB. Entire invocation 188.797 s, mostly global storage inventory; each
board worker completed in 0.297-0.406 s. No GPU needed for this qualification.

NEXT: implement and execute STACK-PRICE-LEARNING-PLAN.md. Use the existing exact
reference rather than repeat its controls. Build a feature-only adapter matching
native canonical observations (do not fake own histories), then register the
four fixed-budget GPU fits comparing 302 vs 362 inputs with two seeds. Keep
card/count and public-state caches separate; assemble batches on the GPU to avoid
writing huge duplicate feature matrices. One bounded invocation should include
adapter qualification, preparation, fitting and final scoring after one storage
admission. Preserve all old sources/results and held-out depth/test-board roles.

Plan is prospective, not executed or fully registered: exact initialization,
optimizer learning rate, seeds, thresholds and data layout still need freezing.
This is a learning diagnostic; success will not finish the broad goal or justify
production promotion. Research GPU sharing with light desktop use remains
approved, with production/heavy work first. No new push or deployment.

## 2026-09-29: first learning comparison failed; broader-board comparison running

Sessions 7536 (learning v2), 23276 (independent CPU readback), and 52671
(train/validation-only diagnosis) all exited 0 and are terminal. V1 session58988
failed before fitting on the NumPy integer-max property call; preserve its
sources/registration/interruption. V2 corrected that property access in a new
module with unchanged scientific choices. Do not rerun those completed studies.

STACK-PRICE-LEARNING-FINDINGS.md records actual four-fit learning evidence.
Giving the network 60 public economics inputs helps fit the training boards,
but both seeds fail the final accuracy gate. On excluded 60/150 depths, mean
normalized regret changes from3.5416% to3.3562% of stack for seed9296401, and
3.6139% to2.4134% for9296402. Target was<=0.1% at each depth and>=20% improvement
in both seeds. Seed1 worsens at150bb. No model promotion or full-game accuracy.

V2 registration SHA256:
f4b0f0a3a6f6b530a43eb5ee4aa812776698e9caa6d5c0c96fa7f33a0e61acd9.
CPU readback checked270 files and23,245,824 final rows; maximum context-mean
CUDA discrepancy4.94e-7bb. Completed run490.547s, four fits roughly64-68s each,
peak CUDA175.26MB,3.99MB allocated new study evidence.

The separate exploratory diagnosis used ONLY fitting/validation boards and
fitting depths, without new training. Richer models' training regrets are
0.01232% and0.03653% of stack, versus2.26062% and2.12507% on validation boards.
Changing score-to-action conversion barely changes validation error. The main
immediate limitation is new-board generalization, not policy conversion.
Diagnosis216.859s; original validation means replayed to1.68e-8bb. Its source
and evidence are immutable. The original negative final test remains negative.

LIVE: stack_board_coverage_run_v1.py --run owns unified exec session78297,
PID90252, process_created1790634895.4364045. Last observed phase was storage
admission. Poll the original session; a status timeout is NOT a process failure.
Do not restart or run a concurrent study. The new plan is
STACK-BOARD-COVERAGE-PLAN.md, preflight passed before execution.

It compares nested24 vs512 fitting boards, fixed362-input64/64 networks,
8192updates each, two seeds9296601/9296602, 16new validation and16new test boards.
All544 groups exclude the prior52 probe/learning groups. Fit depths unchanged;
60/150 excluded from fitting/selection but are not globally unseen geometries.
Four checkpoints per fit, selection frozen before preparing final-test labels.
One-hour cap;256MB new evidence+128MB reserve. Eight hidden CPU workers now
process batches of boards to avoid imports per board. No new model architecture.

NEXT: monitor78297 to a definitive exit. If successful, copy/run the prepared
C:/Users/there/Documents/New project/.work/board-recovery/stack_board_coverage_readback_v1.py
to the research tools directory (refuse overwrite), only after the live job has
released the research lock. It independently replays final decisions on CPU,
checks board separation/paired initial weights/selection/artifact hashes, and
recomputes gates. Then analyze results and preserve them regardless of outcome.
Do not change executed sources, increase the run budget, or use final-test
results to select a replacement. No broad preflop accuracy is established.

Goal remains active. Light desktop GPU sharing approved, heavy/production work
first;4GB combined research CUDA/2GB external headroom, RAM28GB admission/24GB
during, Sfree40GB, global allocated cap800GB. Latest completed learning admission
was740.163GB allocated, Sfree roughly290GB. No deployment, app-session changes,
new GitHub push or historical evidence deletion.

## 2026-09-29: broader board coverage gave a large verified gain; still no promotion

Session78297 / PID90252 completed successfully and is terminal. Independent CPU
readback session21529 also exited0. All owned preparation descendants exited.
No newly launched research experiment currently runs. Do not restart these jobs.

STACK-BOARD-COVERAGE-FINDINGS.md records the fixed24-vs512-board comparison.
Both arms use the same362-input network and8192-update budget. On fresh test
boards at60/150bb excluded from training, cost of mistakes falls92.55% and91.88%
in the two seeds. Mean normalized losses are0.001325 and0.001768, versus
0.017784 and0.021783 for24 boards. All fitting-depth final slices improve too.
However the absolute<=0.001-per-depth gate still FAILS. At150bb,99th-percentile
loss remains6.91/8.73bb and worst loss about33bb. This is a uniform-opponent,
terminal-river diagnostic, NOT a preflop-quality or full-game-gap certificate.

Independent CPU replay:46,491,648 rows,734 files verified; paired initial weights,
board separation, selection and gates checked. Maximum context-mean CUDA error
6.48e-7bb. Main invocation520.078s;528-board preparation16.828s with eight batched
CPU workers; four fits64.5-73.4s each. Peak CUDA995.92MB. New evidence16.64MB
allocated. Inventory cost188.14s; neither accuracy nor timing is a production
solver measurement. Readback source was corrected for544 distinct boards before
its first execution; executed sources/results now immutable.

NEXT SCIENTIFIC STEP: implement/register STACK-BOARD-TRAINING-BUDGET-PLAN.md.
The broad models' validation curves kept improving through8192 updates; compare
short8192 versus long32768 budgets on the same512 fitting boards, paired within
each of two NEW seeded training chains, with32 NEW validation and64 NEW test
board groups excluding all earlier groups. Keep representation/optimizer fixed.
Freeze seeds/checkpoint-selection rules and budget before fitting. Completed
study is not extended; old final boards must not become validation/fitting.
If the accuracy gate passes, move to a multi-decision reference with independent
best responses. A narrow reference pass never completes the broad preflop goal.

Optional throughput work: staging contains unexecuted
C:/Users/there/Documents/New project/.work/board-recovery/global_research_inventory_v3.py.
It binds the NTFS allocation API once, reuses directory-entry stats and resolves
roots once, preserving reparse/activity checks. Old global inventory spends
roughly3min scanning467k files per run. This is ONLY an untested candidate:
review and compare counts/logical/allocated bytes with immutable v2 on quiescent
roots, including failure cases, before using it. It is not copied to T: or used
by any experiment. Do not change the executed v2 implementation in place.

Research goal remains active. Production56708 untouched, no deployment, no new
GitHub push. Light desktop GPU sharing approved; production/heavy work first.
Preserve the research resource caps and all historical evidence.

## 2026-09-29: training-budget comparison running; faster inventory qualified

Previous completed coverage results remain unchanged. The new paired comparison
is live under unified exec session69509, PID96052, created1790636198.6820257.
Its first 32768-update chain completed; the second is fitting. Poll the same
session until a definitive exit; do not restart after an observation timeout.
It owns the normal research lock. Sources executed by this run are immutable.

The new sources are stack_price_learning_long_fit_v1.py,
stack_board_batches_v1.py and stack_board_training_budget_run_v1.py. Registration
is stack-board-training-budget-v1-registration.json. It freezes seeds9296701/2,
512 reused fitting boards,32 fresh validation and64 fresh test groups, paired
8192/32768 update budgets and the unchanged network/loss/selection/gate.
All 96 new groups exclude the prior596 groups. Final-test labels are prepared
only after all four model identities are frozen. Resource and production-priority
limits remain as in the preceding handoff.

Independent CPU readback is prepared as stack_board_training_budget_readback_v1.py.
Run it only after the main job exits successfully and releases its lock. It checks
artifact hashes, board separation, shared-prefix selection and independent dense
inference, then recomputes gates. Do not relax the numerical tolerance or gate
in response to the final result. Analysis and next-study choice follow readback.

The qualified global_research_inventory_v3.py matched original v2 accounting for
all468268 files in34.829/35.453 seconds, versus189.797 seconds. Five negative
controls passed. See GLOBAL-RESEARCH-INVENTORY-V3-FINDINGS.md and control-v2.json.
The first wrapper control_v3 had a syntax error before executing; retained.
Separate control_v4 completed successfully. No old source/evidence was edited.

No promotion to production, deployment or new push. Broad preflop accuracy is
still unproven; goal remains active.

## 2026-09-29: longer training failed; CPU diagnosis now running

The training-budget job session69509 / PID96052 exited0 and is terminal.
Its independent CPU readback session19004 / PID32048 also exited0. The readback
verified796 files,185966592 final decision rows and both failed gates; maximum
context-mean CPU/CUDA difference7.9651e-6bb (tolerance1e-4 unchanged).

Long versus short training reduced normalized primary mean regret26.34% in
seed9296702 and worsened1.10% in seed9296701. Both absolute gates fail. Selected
long steps16384/32768; short8192 in both. Main694.531s; peakCUDA982.56MB;
4.78MB new allocated evidence. Full findings now in
STACK-BOARD-TRAINING-BUDGET-FINDINGS.md. Commitde13304f preserved sources/results
before readback. No production model promotion is warranted.

GPU analysis v1 NEVER STARTED. Direct admissions failed twice; waiting helper
session28722/PID95360 was deliberately stopped while external GPU utilization
stayed94-100%. It exited1, with no study registration/store/result. A temporary
exclusive admission lock prevented a start during the verified helper-only stop.
Sources retained unchanged. This is not a failed scientific model evaluation.

LIVE: CPU-only stack_board_error_diagnosis_v2.py --run, unified exec session30060,
PID81188, started2026-09-29T08:49:54 local. It owns the research lock. Poll this
same handle to completion; observation timeout is not failure. Registration,
status and result use stack-board-error-diagnosis-v2 prefixes. Sources immutable
after execution. See STACK-BOARD-ERROR-DIAGNOSIS-CPU-AMENDMENT.md.

It uses the same two selected models,32 existing validation boards,32 randomly
selected fitting boards (seed9296800), fitting depths only and the unchanged
decomposition. Dense NumPy float32 CPU inference,4 BLAS threads; no CUDA. The
original validation means must replay within1e-4bb before interpretation. CPU
admission<50%, during<75%; production/heavy work priority, RAM28/24GB, Sfree40GB,
global800GB,1800sec and32MB+32MB reserve. No final-test labels, new training,
new boards, model selection or excluded depths are used.

A read-only metadata check found training board categories247 high-card,
215 pair,32 two-pair,14 trips,1 straight,2 full-house,1 quads; no board-only
flush/straight-flush among512. The32 validation boards comprise22 high-card,
8 pair,1 trips,1 two-pair. This describes coverage only, not causes of errors.
Do not use old final-test boards to choose the next feature or training change.

NEXT: finish30060 and check original validation replay and error decomposition;
then choose/register the next controlled representation/reference experiment.
Preserve adverse results. Full preflop accuracy remains unproven, goal active.
Production56708 untouched; no deployment/new push/evidence deletion.

## 2026-09-29: error diagnosis and relative-feature mathematics completed

CPU diagnosis session30060 / PID81188 exited0 and is terminal. It reproduced
the selected GPU validation means within3.9683e-7bb. Runtime344.969s, no CUDA,
0.32MB allocated evidence. Completed result and reproducible aggregation:
stack-board-error-diagnosis-v2-result.json and
stack-board-error-diagnosis-v2-analysis.json. See the corresponding findings.

Both models generalize poorly: validation/fitting-subset loss ratios6.48/17.43.
Changing action conversion improves validation by less0.3%. Same-category
better-kicker rows are37.06% of data but63.03/53.78% of losses; high-card/pair
full hands contribute81.27/85.30% of losses. These exploratory findings use
existing fit/validation data only, not final-test labels. Do not treat their
selected-model validation performance as a fresh independent accuracy claim.

Next plan is STACK-BOARD-RELATIVE-FEATURES-PLAN.md. It appends25 visible facts
to362 original inputs: board-only category/tiebreaks, relationship to board,
same-category kicker differences and minimum private cards needed. No opponent
equity/labels/future cards in inputs. Same512 fitting boards,8192 updates,64/64
networks; fresh seeds9296901/2 and fresh board seed9296900. New32val/64test groups
exclude692 earlier groups. The two-player candidate adds3200 first-layer weights
(1600 each). Preserve paired initial outputs and draws. Gates unchanged.

Feature source stack_board_relative_features_v1.py is implemented and qualified.
CPU control session66932 exited0 and is terminal. Result:
stack-board-relative-feature-control-v1-result.json;12972 holdings,285384 exact
five-card evaluations,27648 invariance variants,8 invalid cases, zero feature
error. Four owned workers finished with no active descendants.41.578s including
inventory;16980 bytes retained. Source/control/plan hashes are now immutable.
See STACK-BOARD-RELATIVE-FEATURE-CONTROL-FINDINGS.md.

NO research process launched in this turn remains running. The old admission
helper28722 is terminal; do not restart it. The GPU was busy with foreground
applications; no research competed with it. Resource limits remain unchanged.

NEXT IMPLEMENTATION: create separate paired362/387-input factory/fitter/runner
and CPU qualification for matching initial outputs, added-feature gradients,
checkpoint save/load and batch pairing. Original executed fit modules cannot
be edited. If ordinary widened GEMM changes rounding, use an explicit original
362-column branch plus a25-column extension initialized to zero to preserve
the exact baseline initial computation; document implementation before training.
Reuse qualified scores/evaluation as appropriate; Dataset public vectors need
25 zero columns to match extended card factors. Keep original512 features/counts
immutable and store only extra arrays. Qualify assembly/actor/context boundaries.

Only then register/run the new learning trial with fresh held-out boards as
planned. CPU preparation can proceed while GPU is busy. GPU fitting must pass
normal admission, with production/heavy work first. Independent readback and
tails/slices remain necessary. No model has been promoted; full preflop accuracy
is unproven. Goal active; no deployment, new push or historical deletion.

## 2026-09-29: relative models qualified; preparation complete; admission live

This supersedes the previous NEXT IMPLEMENTATION section. The paired model,
CPU qualification, data assembly and runner are implemented and have executed;
do not edit their sources or registrations. CPU model-control session42555
exited0. Preparation session50612 / PID104140 exited0 (polled authoritatively).
No preparation descendants remain. Preparation took56.047s including41.593s
inventory and10.562s eight-worker work;1,677,796 allocated bytes,544 boards.
Final-test labels and GPU training were not started during preparation.

Model control:960 probe rows per seed, exact initial scores/base parameters,
nonzero extension gradients, checkpoint round trips and hash/width rejection.
REG SHA885a743e9283e0a54efbfdf70c57172b4ba0810686b3359944ed42eba162b886.
Independent readback control completed on CPU:5760 rows, maximum score
difference3.7252903e-8,6 action-conversion edge cases,2 nonfinite rejections.
REG SHAad484cac762c15667cb4e7badac99b1bd0a81c57e7ebed1f22c009cfdd2a6733.
It uses retained probes and synthetic extension weights; no policy training.
See STACK-BOARD-RELATIVE-PREPARATION-FINDINGS.md.

LIVE at this checkpoint: unified exec session25386, admission helper PID98580,
process creation1790640118.058712. It was confirmed live waiting on external
GPU utilization99-100%; ~14GB free VRAM does not imply spare compute. Poll the
same handle; do not start a competing invocation. It waits up to14400s before
admission, probing every30s, then starts one hidden owned runner child. Status:
stack-board-relative-admission-v1-status.json; immutable manifest:
stack-board-relative-admission-v1.json. Per-launch output is retained in
stack-board-relative-admission-v1-launch-N.log. A pre-start admission race may
defer; once gpu-attempt.json exists, failure MUST NOT be silently retried.
No other helper from prior turns should be restarted.

The authorized comparison is stack_board_relative_run_v1.py --run. Its
registration and complete preparation already exist. Never rerun --prepare.
Source/store names use stack-board-relative-learning-v1. Inputs:362 vs387,
same512 fitting boards, fresh32val/64test excluding692 previous groups,
seeds9296901/2,8192 updates each. Four identities freeze before test labels.
Paired CUDA initial scores/common batches must match exactly. A passing mean
gate is not full preflop qualification; preserve tails and adverse outcomes.

NEXT after main result and authoritative terminal state: run the already
qualified stack_board_relative_readback_v1.py once, with normal CPU admission
and the research lock released. It independently reconstructs NumPy scores,
cash losses and both gates, checks board separation and all hashes. It checks
the recorded CUDA parity proof and the selected checkpoints. Target destination
stack-board-relative-learning-v1-readback-v1.json; no overwrites. This result
does not exist yet at the preparation checkpoint. Analyze only after replay;
do not relax gates/tolerances or choose another model from final-test results.

Resource limits and scientific scope unchanged. Production56708 untouched;
no deployment, new push or historical deletion. Full accurate preflop ranges
remain unproven, so the goal stays active.

## 2026-09-29: weighted-range reference qualified while GPU admission waits

Previous goal turn was a verified wait on live session25386. This turn made
independent CPU progress toward moving beyond uniform-opponent diagnostics.
Admission helper25386 / PID98580 remains live; the latest authoritative poll
still reported external GPU utilization100%, no comparison started. Do not
duplicate or restart it. Its four-hour admission deadline is unchanged.

New sources river_range_reference_v1.py and river_range_reference_control_v1.py
have executed and are immutable. The CPU control session69027 / PID105312
exited0 authoritatively. Result river-range-reference-control-v1-result.json
passed, REG SHAa4ee23c95b26162cd9336e713c6589297a45a63116ff7115a44cbe439d48d9d8.
It verified77832 outcome-mass rows and778320 cashflow rows on12 old probe boards
with6 fixed synthetic weight cases. Max equity error7.77156e-16, max payoff
error6.25278e-13bb. Twelve invalid cases rejected, uniform integer counts exact,
scale/suit/ordering invariance checked, zero support explicit. Runtime53.703s
including inventory;9484 bytes allocated, no GPU or policy training. Separate
readback rehashed55 files and reconstructed result maxima. See
RIVER-RANGE-REFERENCE-PLAN.md and RIVER-RANGE-REFERENCE-FINDINGS.md.

The reference computes all hero holdings against a fixed pre-card-removal
opponent reach vector. It uses nonnegative summation rather than subtracting
nearly equal masses, preserving tiny surviving ranges. Synthetic arithmetic
qualification does NOT establish real-policy reach factorization/binding.
No new final-test labels from the pending learning trial were accessed.

Useful independent CPU next step IF GPU still busy: qualify this reference
against real native history queries from retained TRAIN cases and frozen played
policies (see RIVER-POSTERIOR64-FINDINGS.md and river_posterior64_native_control_v1.py).
The current river_training_overlay_targets_stream_v1.py already constructs exact
posterior mass as entry times actual opponent-history likelihood over990
compatible holdings. It then samples64 future trees. Do not replace that
qualified pathway or silently substitute uniform ranges.

Potential bridge control: at one fixed board/public history, use at least three
disjoint hero holdings to cover every one of1081 opponent holdings in a union
of legal990-hand exports. Check overlapping pre-normalization weights are the
same with canonical suit mappings restored. This must be proven, not assumed.
Then compare each hero's conditional equity/payoff against existing exact
per-hero native outcomes. Use the same frozen policy, original entry weights,
all actual prior actions, and explicit zero support. Retain CPU bounds and
acquire the research lock so the admission helper cannot start concurrently.
First inspect existing retained artifacts/source contracts; no duplication of
old target-learning or expensive full-policy evaluations is needed.

Primary queued trial and its readback instructions above remain the next
scientific learning comparison. Full preflop accuracy is still unproven.
Production56708 unchanged, no deployment or new push; goal remains active.

### Follow-up numerical correction: v2 supersedes v1 payoff calculation

An extra subnormal-weight probe found a real v1 corner-case failure after its
registered6-case control passed: with one opponent holding at float64's smallest
positive weight on the old royal-flush board,990 supported hero holdings had
equity0 instead of0.5. Halving tie mass before normalization underflowed.
Preserve v1, its original result and the recorded failure. Do not use v1 values
as the final qualified reference. No learning trial was changed.

New river_range_reference_v2.py inherits the nonnegative mass calculation and
normalizes outcome masses before taking the half-tie share. Expanded control
river_range_reference_control_v2.py session68320 exited0 authoritatively.
REG SHA2b21da81719612fae1c065d1c5d197f2169ea606b993382bb05b81447543083d.
All12 boards and8weightcases passed:103776 mass rows,1037760 cashflow rows,
max equity error7.77156e-16, max payoff error6.25278e-13bb,12invalid rejections.
The old failure was reproduced and both smallest-positive-weight cases checked
against discrete outcomes/original integer counts. No tolerance was relaxed.
Runtime60.313s including inventory;11494 bytes allocated, noGPU/training.
Separate readback rehashed58files and reproduced maxima. Read the numerical
amendment and updated RIVER-RANGE-REFERENCE-FINDINGS.md before any integration.

The latest live poll of25386 still had helperPID98580 waiting, elapsed1489.6s,
externalGPU100%. Main relative-feature GPU training has not started. Follow
the same handle and frozen-study instructions. Real-policy reach-vector binding
is still an independent CPU next step; use v2 arithmetic. Production untouched,
no deployment/new push and broad preflop goal remains active.

## 2026-09-29: actual-history weighted-range binding passed

Previous goal turn was a verified wait on admission helper session25386,
PID98580, plus read-only inspection. This turn completed the independent CPU
binding check described above. Main session47548 exited0; independent readback
also exited0. Use RIVER-RANGE-POLICY-BINDING-FINDINGS.md for scope and evidence.

New executed immutable sources:
- tools/research/river_range_policy_binding_v1.py
- tools/research/river_range_policy_binding_readback_v1.py
Registered plan: RIVER-RANGE-POLICY-BINDING-PLAN.md.
Result prefix: river-range-policy-binding-v1, registration/result/readback-v1.
Store: S:/GTOpen-research/river-range-policy-binding-v1.
REG SHA11c2e778b60a25d95a462f8efa960df14ea87058f82b706cbb645e22a2306642.

Sixteen fixed public situations, both actors/two generation77 policies/four old
TRAIN boards. Three disjoint hero holdings reconstruct all1081 opponent weights;
fourth disjoint holding verifies them. Restore canonical suit permutations.
30224 overlaps matched actual opponent histories and raw mass. All63360 native
pair outcomes matched. 52/64 hero rows supported,12 explicitly unsupported;
separately52 had zero own-history reach. This is not a strategic quality sample.
Max errors mass8.53e-14,posterior5.56e-17,equity1.12e-16,payoff7.11e-15bb.
Negative coverage/mass/history cases rejected. 50.234s including inventory;
13.39MB allocated/52.93MB logical/114compressed files. No active owned children.
Readback rehashed193files and reconstructed native histories/terminal payoffs;
maxcash5.56e-17bb,2.797s. NoGPU,training,or new learning holdout labels.

Do not repeat these now-qualified arithmetic/binding controls. The primary
scientific next step remains the queued relative-input learning comparison,
then its registered independent CPU readback. It has not started as of the
latest live25386 poll (elapsed2575.9s, externalGPU100%). Helper98580 was verified
live again. Keep following the same handle; do not duplicate or restart it.
The CPU control released LOCK normally. Four-hour helper deadline unchanged.

If relative inputs improve heldout predictions, integrate through a new version
of the actual full-training encoder/checkpoint path before a matched research
continuation with history-conditioned opponents. Existing302-input full models
cannot silently consume387-input weights. This binding only applies to one
current policy; historical average banks retain their reach-weighted mixture
logic. No full-action evaluator replacement or training speed claim yet.
Production56708 unchanged; no deployment/new push. Broad goal remains active.

## 2026-09-29: relative-input native context adapter passed CPU checks

Previous goal turn made concrete progress in commit167c1d6a (weighted-range
history binding). This turn added the versioned387-input context registry and
model-object inference path, reusing the existing qualified362-input registry.
Do not rerun the now-complete CPU adapter control. Main session31363 exited0.
No GPU training or scientific holdout labels were accessed.

New executed immutable sources:
- tools/research/stack_context_relative_inputs_v1.py
- tools/research/stack_context_relative_policy_v1.py
- tools/research/stack_context_relative_control_v1.py
Read STACK-CONTEXT-RELATIVE-CONTRACT.md and STACK-CONTEXT-RELATIVE-FINDINGS.md.
Result prefix stack-context-relative-control-v1; same-named S: study store.
REG SHA6e623a0aa0dee9e9af7513f648a27645632667697f78b042b95f206c08876d16.

5028 retained native observations, all7depths/bothactors/all4streets. Exact
362-column prefix, zero-extension policies, own-history reach and average-bank
policies; synthetic nonzero extension affects3696riverrows only, leaving1332
preflop/flop/turn rows unchanged.14native rows match diagnostic assemblerexact.
3model object roundtrips and9negative controls passed.59.859s inclinventory;
2.21MBallocated/3.25MBlogical/11compressed files. Post-completion inline readback
checked84hashes and saved comparison arrays; it was not independent inference.

This is a research inference/model-object contract, not a full resumable training
checkpoint. CUDA parity for this new context-policy path remains unqualified.
The neutral lift accepts explicit362-input context models; it does not convert
old302-input generation77 policies. Diagnostic Fold/Call weights must not be
installed as an unrestricted all-street/all-action policy.

PRIMARY NEXT remains live helper session25386 / PID98580, verified live this
turn. Latest read state elapsed3233.61s externalGPU100%, training_started=false.
Its four-hour wait deadline remains unchanged. The adapter control released
LOCK. Poll the same25386 handle; do not restart or duplicate it. If the learning
comparison succeeds, run its existing stack_board_relative_readback_v1.py once
as described above. Analyze its fresh-test gates only after that readback.
No additional scientific experiment has been selected or registered here.
If still waiting, verify the live wait rather than repeating completed controls
or starting a competing GPU job. Keep all sources/frozen inputs immutable.
Production56708 unchanged; no deployment/new push; broad goal remains active.

## 2026-09-29 10:35: GPU wait and quiet scheduled follow-up

After the adapter commitd9a7124a, three consecutive goal turns verified the
same live admission helper25386 / PID98580 and sustained externalGPU89-100%.
No scientific GPU attempt has begun: gpu-attempt.json and the main result are
absent. One child launch62848 exited normally before admission; its log reports
prepared_waiting_for_gpu at100% utilization. This is not a failed scientific
attempt and must not trigger duplicate work. The helper remains live.

The remaining primary work depends on GPU capacity. The independent CPU range
binding and context adapter checks are complete; do not repeat them to fill a
wait. The agent goal is being marked resource-blocked after the repeated wait,
without stopping the automatic launcher. Its deadline remains13:31:58 Adelaide
on29September2026. A trial admitted before that deadline may run beyond it.

Existing Codex heartbeat gtopen-research-updates was updated through the app to
ACTIVE at its existing15-minute cadence, replacing its completed older study
prompt. It now watches this specific helper/trial, stays quiet on unchanged
state, and on definitive main completion runs the existing registered CPU
readback once and reports the reviewed analysis. It pauses itself after that
completion notification, a terminal failure, or admission expiration before
training. It must not launch a fresh scientific experiment, push or deploy.
This keeps the follow-up automatic without rapid unchanged goal updates.
Production56708 remains untouched. No new scientific findings in these waits.

## 2026-09-29: Relative-input comparison and independent analysis complete

Admission helper25386/PID98580 launched child33044 at11:13:39 Adelaide after
GPU resources became available. The main comparison completed at11:21:02;
the helper exited0 with zero active descendants. This was the sole started
scientific attempt; earlier pre-admission deferrals were not retried fits.
The main result SHA256 is
4bcd1948186032f550c0001ba534e6941c35888577b5abfe54e876e47978810f.

The registered readback ran exactly once in session5971/PID92100, exited0,
and released LOCK. It verified1419 file identities and independently replayed
185966592 decision rows. Maximum CPU/CUDA context-mean difference was
1.1939673952854335e-6bb, below the unchanged1e-4bb tolerance. Both model selection
and held-out comparisons passed their integrity checks. No process remains
from this helper, main comparison or readback. Do not restart these completed jobs.

Scientific outcome: relative features reduce the fresh held-out-depth normalized
mean loss by46.1071%/23.8730%, satisfying the relative20% requirement in both
seeds. Both still fail the absolute0.001-of-stack target, so the combined gate
fails. Candidate60/150bb mean losses are0.09453/0.22549bb and0.11629/0.29050bb;
required maxima are0.06/0.15bb. Tail mistakes and adverse slices remain recorded.
Validation means favor the baseline in both seeds, even though these final boards
favor the candidate; retain this evidence of limited generalization certainty.

See STACK-BOARD-RELATIVE-LEARNING-FINDINGS.md and
stack-board-relative-learning-v1-analysis-v1.json for the completed analysis.
Its reporting-only producer is tools/research/stack_board_relative_analysis_v1.py.
This is terminal river Fold/Call against a uniform legal opponent distribution,
not full preflop accuracy and not an all-street strategy checkpoint. No promotion,
new scientific experiment, push, deployment or production56708 modification.

The next proposed research direction is better balanced fitting and validation
coverage of hand-versus-board relationships, followed only after sufficient
accuracy by a separately registered multi-decision, action-conditioned range
comparison. This is a proposal, not a running or registered follow-up. Do not
use this final test for tuning or silently extend/retry the completed comparison.
The gtopen-research-updates heartbeat is to be paused with the terminal analysis
notification. The broad accurate-preflop goal remains unachieved.


# Balanced board coverage comparison running — 29 September 2026

The latest human instruction, “Proceed with the study - I'll check in later!”,
approved STACK-BOARD-BALANCED-COVERAGE-PROPOSAL.md and lifted the earlier
monitor-only restriction. The completed relative-input study is not restarted.

Three newly registered controls passed: exact deterministic board selection and
independent13-cell census, scalar-oracle/tail metric checks, and parallel data
preparation exactly matching retained qualified arrays. They used no scientific
training. Eight CPU workers then prepared1,152 new fit/validation boards in a
98.219-second invocation, alongside512 readonly original fitting boards.
Current new-store allocation is29.87MB; logical evidence35.29MB. There was no
GPU use or final/stress-test label generation during this preparation.

The exclusion union has867 distinct groups:788 historical plus80 fixture groups,
with one overlap. All1,344 new groups and exact five-card lists are registered.
The sampler qualification manifest and registration replay match exactly.

Frozen registration SHA256:
1e4e2a8a615e1ad5a38cf89c77cd785740273ed7479db472cd13b309f30990e4
Frozen preparation SHA256:
3042384e6230cf9665aa6cd3efbc91021fa60a9cc76fa38eb84042ff293b7c80

Live admission helper: session93077, PID79944, creation1790653143.1142557.
Owned research child: PID28312, creation1790653144.6399736.
Both actual command lines and creation times were verified. The helper began
at13:09:03 Adelaide and admitted its sole child immediately with9% GPU use and
21.71GB free VRAM. Main output reached `starting_fit`, seed9297101, random362.
Do not trust these PIDs without verifying creation/command and fresh outputs.

Files:
- `stack-board-balanced-admission-v1-status.json` and `...-launch-1.log` here.
- `stack-board-balanced-learning-v1-{registration,prepared,status,result}.json`.
- Store `S:\GTOpen-research\stack-board-balanced-learning-v1`.
- Sole-attempt marker in that store: `gpu-attempt.json`.
- Scientific runner `tools/research/stack_board_balanced_run_v1.py`.

The original four-hour admission window ends about17:09:04 Adelaide today; an
already admitted trial may run beyond an admission deadline. Here training was
already admitted. The scientific3,600-second cumulative work cap and fixed
8,192 updates still apply. Never restart a scientific attempt or change inputs,
gates, tolerances, seeds or budgets because of an observation timeout.

Once the main comparison definitively finishes successfully and releases LOCK,
run `C:\Program Files\Python312\python.exe -B` with
`T:\Dev\GTOpen\tools\research\stack_board_balanced_readback_v1.py` once, only
if its result/attempt marker are absent and no readback is running. It has four
CPU workers,1,800 seconds, its own exclusive attempt marker, and no new training.
Wait for adequate CPU/RAM and idle production before starting; do not infer an
attempt from a stale status file. Verify its terminal exit and retained evidence.
Readback names begin `stack-board-balanced-learning-v1-readback-`.

Then analyze BOTH fresh seeds and all predeclared comparisons: primary is
structured versus random at387 inputs on random test boards. Keep the362-input
diagnostic and structured stress test separate. Include absolute target failures,
tails, subgroup regressions and validation/test disagreement. Preserve failed
evidence and report numerical readback failures rather than relaxing tolerances.
No subsequent scientific experiment, GitHub push or deployment is part of this
monitoring follow-up. Diagnostic river Fold/Call weights remain restricted and
are not a complete preflop/all-street policy. The broader goal remains unachieved.

Research shares the GPU with light desktop use and yields to production or heavy
work. Production56708 is untouched. Quiet15-minute monitoring should notify only
on finished independent analysis, terminal failure, or admission expiry before
training; then pause the heartbeat. No routine unchanged status updates.

## Terminal handoff — 29 September 2026

The balanced-board comparison has finished. The admission helper and scientific
runner exited successfully (exit 0); all eight fixed fits completed. The main
result SHA256 is
0dab880a026c91fc29edcc60c7df81a1cf97fb9bd492c3c192e23d1d827cfc43.
The one-time independent CPU readback exited 1 and remains FAILED. Its preserved
failure file is stack-board-balanced-learning-v1-readback-interruption-4d42f10f.json,
SHA256 7968a6e3c560f94fbb2bf6094b6a15ffb805565f98abc0d530f96b2c7dad808b.
The successful readback result does not exist. Do not retry this attempt, relax
its tolerances, or run the success-only analysis producer.

The first preserved failing context differs by one classified decision on each
of two boards; all its other recorded metrics stay inside their fixed limits.
The affected raw probabilities and holdings were not retained, so a numerical
boundary explanation remains unproven. Full independent qualification did not
finish. Retained GPU measurements show primary error worsening by 0.51% and
38.99% across the two seeds. The separate rare-board stress gains do not rescue
the failed primary comparison. These remain restricted terminal river Fold/Call
results against a uniform legal opponent, not established preflop accuracy.

The reporting-only terminal producer checked file identities, selection metadata
and stored gate arithmetic without further inference or training. Evidence and
analysis are saved in:
- stack-board-balanced-learning-v1-terminal-analysis-v1.json
- STACK-BOARD-BALANCED-TERMINAL-FINDINGS.md
- STACK-BOARD-BALANCED-INTERPRETATION.md
- tools/research/stack_board_balanced_terminal_analysis_v1.py (repository root)

PIDs 79944, 28312 and 78800 were verified absent and the study lock was released.
The gtopen-research-updates heartbeat is PAUSED following terminal notification.
No scientific process is left running for this comparison. No new experiment,
GitHub push or deployment was performed; production on 56708 is unchanged.
Keep ordinary random sampling and relative-hand inputs as the research baseline.
A small separately registered numerical diagnostic is proposed in the
interpretation document but has NOT been launched. The broad goal of robust,
accurate preflop ranges remains incomplete.

## Follow-up prepared — numerical diagnostic, not started

The separate stack-board-boundary-diagnostic-v1 is prepared. Six synthetic
controls passed, and preparation verified 404 input identities. It targets the
preserved seed 9297101/random/362-input/40bb failure on boards 51 and 101, keeps
original CPU/GPU matrix shapes, and saves raw scores and exact decision identities.
The registration fixes a 600-second invocation cap, 4 GB CUDA cap, 2 GB external
headroom, and 32 MB evidence limit. It has no training or new test labels.

See STACK-BOARD-BOUNDARY-DIAGNOSTIC-PLAN.md and the corresponding registration.
The run stage has NOT been invoked; no attempt marker or diagnostic store exists.
Original failed evidence and thresholds are unchanged. The success-only old
readback must stay absent. The monitoring instruction prohibited launching a
subsequent experiment; request approval for this distinct explanatory diagnostic
before run. The heartbeat remains paused and production 56708 is untouched.

Preparation validation caught a JSON tuple/list equality mismatch before any
scientific invocation. The rejected registration and both preparation sources
are preserved under stack-board-boundary-diagnostic-v1-preparation-*. The
manifest was corrected to use JSON-native lists, with batch intervals unchanged.
All seven preparation controls now pass, including an exact disk round trip.
The current registration matches all 404 recorded identities. Approval for the
separate run is pending; the attempt/result/store remain absent.

## Numerical diagnostic completed — approval interpretation corrected

The earlier approval block overextended the monitoring restriction on new
learning experiments. The resumed goal's bounded diagnostic was limited to
explaining the already authorized study's failed verification. The original
failed readback was not retried or replaced, and no new training was launched.

stack-board-boundary-diagnostic-v1 ran once, session 48035, PID 90452, creation
1790687521.3759525. Its terminal exit was 0 after 25 seconds, and the process and
research lock were verified gone. Peak reserved CUDA memory was 304,087,040
bytes; retained raw evidence totals 4,063,643 bytes. Production was untouched.

Both historical count differences and both original GPU board-average losses
reproduced exactly. Independent saved-array arithmetic checked 151,340 rows.
Both disagreements arise when nearly equal negative fold/call scores reverse
ordering between CPU and CUDA, causing the nonpositive-score fallback to flip
between 0% and 100% calling. The reference call advantages are +1.181313bb and
+1.996212bb, while the predicted call values are slightly negative. Consequently,
this is not solely a harmless rounding difference or a fix to the verifier.

See STACK-BOARD-BOUNDARY-FINDINGS.md, the diagnostic result, and its independent
-readout.json. The latter pins all inputs and independently reconstructs public
prices, call probabilities, losses, exact error counts and the two raw cases.
Original raw historical predictions were absent, so exact historical bitwise
identity is not claimed. The original full readback remains failed and absent.

Next design work should address the learned call-value errors and the action
conversion together. Anchoring known fold value at zero alone would still fold
both of these profitable calls. Use separate controls and fresh evaluation for
any new method; do not tune on these failing cases. No new training comparison,
GitHub push, deployment or broad-goal completion has occurred. The old heartbeat
remains paused; the diagnostic is terminal and must not be invoked again.

## Equity-pricing candidate implemented; no scientific fit yet

The research-only stack_equity_priced_model_v1.py learns card equity with a
191/64/64/1 shared sigmoid network and computes terminal call value from the
known price. Fold value is exactly zero. Its 191 columns contain only the
existing card/hand/relative-board inputs, excluding public context. This is
restricted to the uniform-legal-opponent river reference and refuses a different
opponent scope; it is not a range-conditioned or production preflop model.

Eight CPU implementation tests and 12 separately recorded synthetic CPU/CUDA
cases passed. The latter checked two seeds and three batch sizes at float32 and
float64, forward values, independent NumPy inference, losses and gradients.
Control compute took 0.813 seconds (about five seconds including startup), with
155,189,248 bytes peak reserved CUDA. No poker dataset was fitted. No numerical
threshold from an earlier study changed. The control process exited 0 and the
research lock is absent.

STACK-EQUITY-PRICED-CANDIDATE.md describes the architecture, exact correspondence
to the existing normalized value-MSE objective, limitations, and requirements
for a prospective matched learning comparison. Its fresh seeds and board plan
are proposed only: no scientific runner/registration/data preparation or fitting
has occurred for that comparison. Next implement and qualify integration with
the current baseline, common batches, selection, fresh board separation and
independent evaluation before any scientific fit. Avoid repeating the already
qualified original cash-flow/reference calculations as substitute progress.

Earlier evidence matters: alternative action conversion alone barely helped
prior validation, and substituting uniform equity for actual betting-conditioned
ranges was rejected. A candidate pass would still require range-conditioned,
multi-decision qualification before contributing practical preflop ranges.

The earlier pending Run diagnostic question referred only to the now-completed
boundary diagnostic. If its answer arrives later, do not duplicate that run or
mistake it for approval of another experiment. The earlier blanket approval
block was corrected as documented above. All evidence is local; no push or
production changes. The old heartbeat remains paused.

## Matched equity-pricing study registered and running

The earlier candidate proposal is now implemented. Seven CPU integration tests,
six protocol tests, and a recorded GPU integration control passed. The GPU
control checked eight raw comparisons, four complete metric readbacks and exact
agreement with the legacy CUDA sampler. It used only synthetic fixtures.

stack-equity-priced-learning-v1 reuses 1,024 fitting boards and prepared 128 fresh
validation boards in 46.297 seconds. Seeds 9297601/9297602 fit both approaches
with one shared batch per update. Both use float32 training and widened-float64
validation/final inference. All four selections must be frozen before preparing
128 fresh random test and 64 separate stress boards. The original primary gates,
readback tolerances and failed historical evidence remain unchanged.

Main GPU session 5880, PID 28172, process creation 1790690089.1683035 was confirmed
live and reported starting_paired_fit for seed 9297601. Its gpu-attempt.json
exists. Verify current process identity and outputs; never retry this attempt.
Registration SHA256 41b5b799b7fb6cae773bf3358313959a691bef1c2c46af0ad701c5b8d89d66c8.
Preparation SHA256 e29378e93c26647d13e68e7f9058802195568bf875fe7af4a818039014ed2610.
Store S:\GTOpen-research\stack-equity-priced-learning-v1. See
STACK-EQUITY-PRICED-COMPARISON.md for precise scope, budgets and execution rules.

After successful main completion and lock release, run the registered
stack_equity_priced_readback_v1.py once if no readback attempt/result exists.
It collects all numeric discrepancies and writes complete=true, passed=false
for a completed but unsuccessful verification. That is a terminal failure,
not authorization to retry. Then analyze both seeds and the fresh-test gates.
No result, practical preflop accuracy, push or deployment is claimed yet.
The old heartbeat remains paused; the active goal is carrying this study.

## Matched equity-pricing main complete; independent readback live

Main session 5880 exited 0 after 1,008.0 total work seconds and released its
research lock. The registered primary GPU gate failed in seed 9297601 (3.54%
relative reduction) and passed in seed 9297602 (41.89%). Both candidate seeds
met the per-depth absolute mean-loss limit. These are provisional GPU outcomes.
The first candidate seed has worse p99 and maximum errors despite its small
aggregate improvement; retain those adverse tails in the final interpretation.

Independent readback was started once after verifying no prior readback attempt,
result or live process. Current session 85622, PID 9504, process creation time
1790691089.3120685. It is live and has read back 20bb contexts for all four models.
Do not invoke readback again. Verify this handle/process rather than stale status.

The reporting-only stack_equity_priced_analysis_v1.py is committed as 9bdc7d13.
After readback reaches a terminal result and releases the lock, it verifies
recorded identities, reconstructs gates and writes complete per-seed findings.
It performs no new inference or training and handles completed numerical failure
without promoting unverified results. If readback terminates before a result,
preserve the failure and use a separately scoped reporting-only analysis.
Current files retain prefix stack-equity-priced-learning-v1. No production change.

## 2026-09-30: equity-pricing analysis complete; full-context integration started

Previous goal turn was a verified wait on live readback85622/PID9504. This turn
completed that wait: it exited0 after1587.969s, checked2900 identities and replayed
557899776 correlated decision rows. All fixed numeric checks and rebuilt gates
agreed. PID9504 is gone and LOCK released. Do not run main or readback again.

The reporting-only analysis ran once and exited0. See STACK-EQUITY-PRICED-FINDINGS.md,
STACK-EQUITY-PRICED-INTERPRETATION.md and stack-equity-priced-learning-v1-analysis-v1.json.
Scientific combined gate fails:3.54%/41.89% ordinary reductions,20%required in BOTH.
Both absolute limits pass, but seed1 has worse150bb mean and worse tails at both
depths. Separate rare stress-board loss worsens in BOTH seeds. No adoption.
All selected models, retained main result and independent readback remain intact.

Correction to the earlier inferred next step: actual-history weighted-range
binding was ALREADY completed this morning (river-range-policy-binding-v1).
Do not repeat it. Read its FINDINGS. The real gap is complete training integration.

STACK-CONTEXT-TRAINING-INTEGRATION-PLAN.md maps concrete missing pieces. New
stack_context_full_policy_v1.py preserves both existing root/exact corrections
in the362/387shared inference path. Four CPU retained-policy tests passed7.642s,
recorded in stack-context-full-policy-v1-cpu-tests.json and its FINDINGS. This is
one-context implementation evidence, not CUDA/multi-context/training qualification.
No new scientific experiment is registered or running; no research processes
remain from the completed equity-pricing comparison. The old heartbeat is paused.

Next implement/qualify context-local isolation, full-model CUDA inference,
stack-normalized weighted fitting and complete joint-cycle checkpoint semantics
as listed in the integration plan. Keep all executed scientific inputs immutable.
Do not replace this with another terminal uniform-equity fit, drop exact/root
overrides, migrate old checkpoints implicitly, or claim full-preflop accuracy.
Production56708 unchanged. No push/deployment. Broad goal remains active.

## 2026-09-30: full-context CPU/CUDA control and fit-row bridge complete

The one-time stack-context-full-control-v1 finished successfully: session78435,
PID84444/creation1790693343.055133, exit0,58.297s. Process is gone; LOCK and OTHER
are absent. It checked16 retained-policy comparisons and14 synthetic multi-context
CPU/CUDA cases. Registration SHA256:
9b44e853347acb6d3dfb10d8e86f7ce149f33248350a819653401116fec1a04f.
Do not rerun this control. Its new saved-array/hash readback also exited0 and
passed; limitations are in STACK-CONTEXT-FULL-CONTROL-FINDINGS.md. It uses no
new inference or training and does not qualify a trained policy/checkpoint.

stack_context_fit_rows_v1.py is now in tools/research, with five CPU tests
passed2.912s. It reconstructs native context inputs without fabricated own
histories, preserves weighted visit-reservoir semantics, separates identical
numeric keys across games, and normalizes targets by starting stack and each
context's weighted legal-action count before an explicit context mixture.
See STACK-CONTEXT-FIT-ROWS-FINDINGS.md and its recorded test evidence.
Targets were synthetic; no new scientific comparison has started.

Next: add the CUDA fitting adapter using this exact objective and both input
representations; then complete atomic joint-cycle state/checkpoint semantics
and native worker integration. Qualify one real complete cycle, including
restart equivalence and upstream preflop propagation, before registering the
matched full-policy learning comparison. Do not repeat completed diagnostics
or confuse terminal river gains with full preflop accuracy.

The user received a current plain-English status: latest equity-pricing
candidate rejected as inconsistent, fuller training integration progressing,
no long training currently active. Production56708 remains unchanged; no push
or deployment. The old heartbeat remains paused and the broad goal active.

## 2026-09-30: GPU fitter and joint-cycle checkpoint implementation qualified

Previous goal turn was concrete progress (000e6f71: full-context inference and
weighted fit-row bridge). This turn added stack_context_training_fit_v1.py.
Four CPU loss/gradient/initialization/export tests passed1.787s. The new bounded
stack-context-fitter-control-v1 ran ONCE: session61846/PID88024, creation
1790694459.5942416, terminal exit0 in71.141s. Registration SHA256:
190461478ae4d75306bafefa407090e4521f91d945da9b95e39706dc7ed58615.
Do not rerun. All four direct/captured256-step fits gave identical networks;
CPU/CUDA raw-score/gradient checks passed. Saved-array/hash readback also passed.
Store S:\GTOpen-research\stack-context-fitter-control-v1 is5.8MB logical.
Peak CUDA163.6MB. Process gone and both research locks absent.

stack_context_training_checkpoint_v1.py now binds all fit contexts, objective
and source identities, samplers/RNGs/reservoirs/local accumulators and complete
played-model bank. Four CPU tests passed10.034s, including exact continuation
of RNG streams and interrupted-publication replay. Tests use synthetic updates,
NOT an actual complete native training cycle. Prior state is unchanged on an
interrupted publication; no partial context set or unplayed final model may
enter a saved bank. Fitter uses fresh Adam per fit, so no optimizer carries over.

Read STACK-CONTEXT-FITTER-FINDINGS.md and STACK-CONTEXT-CHECKPOINT-FINDINGS.md.
Next required work is step4 of STACK-CONTEXT-TRAINING-INTEGRATION-PLAN.md:
connect native query, board-target, posterior64 and evaluation paths to this
full context model. Existing board_training_targets_v1.policy_rows and
river_policy_batch_v1.CPUCurrentPolicy are hardcoded302-input paths and must
not be reused unchanged. Preserve full action menus, actual history-conditioned
opponent targets, exact/root overrides and own-history reach; do not fabricate
own-history links for fixed-board rows that do not retain them.

Then qualify a real complete cycle including restart and upstream preflop
influence before registering the matched learning comparison. Native worker
provenance and whole-run progress-marker selection are still outstanding;
checkpoint identity fields alone do not prove native target derivation.
No scientific training is currently active. No production56708 change,
push or deployment. Old heartbeat paused; broad goal remains active.
