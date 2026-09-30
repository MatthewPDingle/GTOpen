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

## 2026-09-30: current-policy and board-target adapters passed bounded CPU checks

The user requested a status update. Live process inspection found no GTOpen
research Python/native job; GPU snapshot was0% and both research locks absent.
Latest scientific equity-pricing comparison remains terminal and rejected.
No new scientific training, production change or GitHub push occurred.

Finished the three previously staged modules and copied them to tools/research:
stack_context_current_policy_v1.py, stack_context_board_components_v1.py,
stack_context_board_targets_v1.py. Added test_stack_context_native_adapters_v1.py
and stack_context_native_adapter_check_v1.py. The recorded implementation suite
exited0: session71222, seven tests10.889s, recording10.906s. Four bounded native
invocations (two full physical catalogs, two tiny fixed boards); no GPU fitting.
Evidence: stack-context-native-adapters-v1-cpu-{attempt,tests}.json. Do not overwrite.
Read STACK-CONTEXT-NATIVE-ADAPTER-FINDINGS.md for exact scope and limitations.

Key implementation correction: old board_root_components_v1 assumes200bb node
indices.20bb has12nodes and only postflop branches2/5; its re-raise is an all-in.
The new decomposition follows actual topology and requires common terminal
showdown economics before using one exact matrix. Seven-depth synthetic pairwise
recursion and old200bb closed-form parity pass. Native tiny boards pass20/200bb.

Cached CPU policy parity passes both representations, seven contexts, allstreets,
and retained generation77 models. Fixed-board score-only rows MUST be postflop
and omit own_history entirely; native/preflop batches must retain genuine links.
Complete physical preflop catalogs require1326holdings at every decision node.
The engine rejects keys/context/menu mismatches and foreign prepared batches.

Still outstanding: cached CUDA engine parity, versioned board/posterior64 worker
integration, context-specific all-in matrices/full physical catalogs with actual
provenance, complete prepare/draw-record/generation-evidence qualification, whole
joint native training cycle and interruption/restart/upstream-preflop checks.
The saved fixture matrices for seven contexts are synthetic routing sentinels:
never use them as scientific poker targets. Do not relabel the original200bb
matrix to the different geometry200bb context. Native output hashes from this
implementation check are recorded, but outputs were not retained for readback.

Continue step4 of STACK-CONTEXT-TRAINING-INTEGRATION-PLAN.md, then step5, before
a matched full-policy learning comparison. No terminal uniform-opponent rerun,
no promotion of diagnostic weights. Old heartbeat paused; broad goal remains active.


## 2026-09-30: complete all-in coverage and real stack-local resources passed

The user requested another status update; no live research job was present at
the initial check, and the latest scientific learning candidate remains rejected.
The active goal continued with concrete resource integration work.

stack-context-complete-allin-cache-v1 main session91955 and readback29115 are
terminal exit0. Main121.594s, readback16.203s; 93769 canonical keys covering all
1624350 compatible ordered physical pairs. Reused47478 original keys, expanded
to71200 by explicit win/loss role reversal; newly enumerated11346 representatives
for22569 missing keys, up to12 native CPU workers. Readbackpassed includes22692
sample-board checks and full retained artifact/count reconstruction. Do NOT rerun.
Registration242663d663a66a530827efdf3e94fa1720228f6fbb05816d36023dce4658512b.
Cache32c9225b3e500f72e5f670c8fd99a90eeeca104fb9178847c47d989e58553f87.
Read STACK-CONTEXT-COMPLETE-ALLIN-CACHE-FINDINGS.md. Store8.33MB allocated.

stack_context_resources_v1.py and its plan were completed and copied from staging.
Three narrower-context/negative tests passed6.122s, with immutable test evidence.
Preparation session64533/PID93520 (creation1790697774.207835) exited0 in31.187s
after admission. Seven contexts20/40/60/100/150/200/400bb now have real population,
matrix, full physical catalog and initial class catalog. Maximum separate matrix
arithmetic discrepancy8.674e-18. 29files82.8MB logical/22.44MB allocated. Saved-file
readback passed7contexts/87identities in1.016s. Do NOT rerun completed attempts.
Read STACK-CONTEXT-RESOURCE-FINDINGS.md; files use stack-context-resources-v1.

These geometry fixtures have broad UNSOLVED 169/169 incoming class support. They
are implementation-control inputs, NOT learned opening ranges or chosen scientific
training population. Do not silently use or relabel original200bb matrices, nor
continue using synthetic routing sentinels as real poker targets. Use the new
context-bound result paths/hashes and verified cache explicitly.

Two worker adapters remain ONLY STAGED in
C:\Users\there\Documents\New project\.work\board-recovery:
stack_context_board_workers_v1.py and stack_context_river_workers_v1.py.
They were syntax-checked, not copied/qualified. No complete joint native training
cycle, cached CUDA engine, restart replay or upstream influence check is passed
yet. Continue steps4/5 of STACK-CONTEXT-TRAINING-INTEGRATION-PLAN.md using the new
real resources. No scientific comparison is registered/running; diagnostic
weights are not a complete preflop model. No production56708 change or push.
The old heartbeat remains paused and the broad goal remains active.


## 2026-09-30: native pipeline controls and history bridge qualification

Latest user asked for status. Live process inspection confirmed no active
GTOpen research process; GPU snapshot0%, research locks absent. Reported plainly
that infrastructure is progressing but no validated better preflop ranges yet.

Workers/pipeline are now copied into tools/research and their three bounded
publication/identity/future tests passed0.024s. Cached CPU/CUDA/reference parity
passed all14cases; the separate saved-array/hash readback passed with maximum
error2.220446049250313e-16. V1 native cycle stopped on status FileExistsError
before collection; V2 stopped on missing native own_history before fitting.
Both failure sources/evidence preserved, processes terminal and locks released.
V2 retained one complete200bb fixed-board native tree/request/result.

New hu_sampled_allin_history_bridge_v1.rs/exe compiled offline. It adds actual
native own-history export without changing the old bridge or value traversal.
stack-context-history-bridge-check-v2 passed once, exit0: 20/200bb,13 physical
deals each,1920/5911 observations and5499/21762 genuine ancestor edges, allstreets.
Strict complete-model scoring succeeds. Stripped query export equals old;
history export equals established bank helper; old/new nonuniform-policy
traversals exactly equal,52 cashflow traversals,zero error. CheckV1's JSON-bytes
harness failure is preserved; V2 reused its completed20bb query outputs.

Read STACK-CONTEXT-NATIVE-INTEGRATION-FINDINGS.md. No joint native training cycle
has passed yet. Next create a separately identified native-cycle control using
bridge='hu_sampled_allin_history_bridge_v1.exe', retaining all original budgets,
inputs and gates. Do NOT rerun V1/V2 or edit their executed sources. Use saved
history check evidence in the next registration. Existing pipeline need not
change for this bridge substitution. A V3 controller has NOT been created.

Next gates: complete joint collection/fit, whole-checkpoint restore, interrupted
publication replay and upstream preflop propagation. Then register a matched
scientific comparison; do not promote diagnostic/uniform-generation weights.
No production change, deployment or push. Old heartbeat paused; goal active.

## 2026-09-30: full native cycle reached collection; V4 now LIVE

Prior turn made concrete progress (fdf49143: native workers/history correction).
This turn created and ran native-cycle-control-v3 once. It is TERMINAL exit1,
session55659, PID105564/creation1790699956.5862389, registration
 e353640b298387822dedf8cfd6eebcce040b8351faf477f7630731428f890e00.
It completed200/100/20bb collections, then hit its4GB logical evidence cap during
the fourth context BEFORE fitting. Preserve failure/registration/source/store.
No GTOpen research workers remained at the subsequent actual process check.
QuiescentV3 store:4,225,860,545logical /1,029,974,984allocated bytes,2290files.
Completed context walls121.188/119.891/69.141s. Summed river-target worker times
202.640/197.608/107.984s dominate; other target/ingest/native work was much less.

A separately registered V4 IMPLEMENTATION check is now running, not scientific
model comparison. It corrects the inadequate artifact estimate to8GBlogical and
reserves8GB against the existing800GBglobal-allocated cap; disk40GB/RAM/CUDA2GB/
40minute bounds and all numerical gates unchanged. It repeats collection from
the incomplete V3 integration test; no completed scientific comparison or cached
parity diagnostic is repeated. V3 remains immutable, including its terminal failure.
Read STACK-CONTEXT-NATIVE-CYCLE-CONTROL-V4-PLAN.md for explicit rationale.

LIVE HANDLE: session12654, PID49032, creation1790728986.1064448.
Registration dc0145a4933f271a49579c9b4b5d4ac858bab9d9b24164942a2e24d18b749ba8.
Store S:\GTOpen-research\stack-context-native-cycle-control-v4.
Last authoritative live session poll returned running; two context collections
complete, elapsed362.984s, main status context-complete for100bb key86e0ebae...
Do not duplicate/restart on an observation timeout. Verify the actual handle or
identity. The expected remaining work is20/40/400bb, two fits, complete checkpoint
restore/publication replay and upstream river-intervention checks.

Prepared stack_context_native_cycle_readback_v1.py is now in tools/research and
syntax checked, NOT RUN. It targetsV4 and must only run after definitive main
success and owner release. It pins all retained inputs/artifacts, uses four CPU
workers to replay original deal/action streams, original weighted/river ingesters,
all reservoir arrays/RNGs, exact/root state and complete checkpoint identities.
It checks actual both-actor/all-street/2/3/4-action visit coverage and excludes the
final unplayed model from the played bank. It creates no fresh native labels or
fits; it is arithmetic/source replay using qualified ingesters, not a separate
poker oracle or independent reconstruction of every posterior/tree calculation.
Preserve any failure rather than weakening a check. If V4 fails, do not invoke
this success-only reader blindly. Read the terminal cause and proceed from evidence.

While V4 runs, a separate CPU feature microcheck passed19,002rows (all nine board
categories), exact float32 equality, card-order invariance, six malformed rejects.
New stack_board_relative_features_bulk_v1.py copied to tools/research; no live
pipeline imports it. Scalar1.06184s vsbulk0.20227s,5.25x for this component ONLY.
The executed check script remains in staging .work/board-recovery; its immutable
attempt/result evidence was copied underOUT with stack-board-relative-bulk-check-v1.
This is a possible later target-preparation optimization, not an end-to-end speed
claim and not permission to alter the active trial. Finish the joint-cycle and
readback gates first, then qualify any new faster adapter separately if worthwhile.

The user asked for an update during work and received the current facts: history
fix passed, first three V3 collections completed, artifact estimate failed, V4
running with a sufficient budget, no validated better ranges yet; production intact.
Old heartbeat paused. Broad goal remains active. No push/deployment.

## 2026-09-30: native joint cycle and readback PASSED; cached evaluator qualified

Previous goal turn was a verified wait: V4 controller session12654 was live.
This turn completed authoritative implementation evidence. V4 session12654
exited0. PID49032 and all direct children are gone. It completed all five fit
contexts20/40/100/200/400, both16-step fits, publication and interruption replay,
exact checkpoint restoration, and river-to-preflop connectivity. Whole invocation
835.625s; pipeline809.313s. Original caller state unchanged. Store5.711GB logical,
1.416GB allocated,2982 files; CUDA peak197MB. Preserve all V1/V2/V3 failures.
Main result SHA6990d0e7a78622182e55b6aee5ca6f9c0f284951f75a4733c65427a9e15ce591.

Executed the prepared success-only readback exactly once, session76840,
PID105356/creation1790729898.9036372, exit0. Four CPU workers,43.578s. Complete
arrays/RNG/local accumulators and original weighted/native source evidence
replayed at all five depths; both actors/all streets/2,3,4-action nodes covered.
Final unplayed model excluded. Main/readback locks absent and owners gone.
Readback result SHAc88b621f6a05ff399849824cc31f83f757102ef48bab66e1ecdda890c622fdda.
Read STACK-CONTEXT-NATIVE-CYCLE-FINDINGS.md. Do NOT rerun completed controls.
This uses qualified ingestion arithmetic, not a second independent poker engine.
The control's broad unsolved entry populations are NOT scientific opening ranges.

New cached complete-played-bank evaluator now qualified, separate from training:
stack_context_played_bank_v1.py encodes a query once per bank, retaining each
model's own complete table overrides and history-weighted reach. Its check ran
from staging .work/board-recovery, session11661 exit0. Passed28 CPU/CUDA cases
at both widths/all7depths against retained native-query reference arrays;10
invalid-input cases; max policy2.22e-16 /reach4.44e-16,10.75s. No fresh labels or
fits. Exact source/evidence copied to tools/research and OUT. Do NOT rerun this
completed check. Read STACK-CONTEXT-PLAYED-BANK-FINDINGS.md. This is a two-model
correctness check, not a claimed complete long-bank speed measurement.

No scientific comparison is registered or running now. Next prepare/register
matched362/387 full continuation learning using the integration plan. Bind the
actual entry populations explicitly; do not relabel the geometry-control ranges
or claim an inherited200bb entry range is correct at other depths. Keep five
fit depths and60/150 transfer, both seeds, common deals/boards, same optimizer
budget, fresh held-out predictions and complete played-policy value and upstream
preflop decisions. Prespecify uncertainty/tail rules before new labels.

Measured collection dominates cost (~801/809 pipeline seconds); optimizer phases
sum0.219s. Qualified lossless XZ retention already exists in
owned_research_archive_v1.py; reuse it for NEW explicitly owned scratch to stay
under the800GB global allocation cap. Do not delete/rearchive old evidence.
The separate bulk relative feature component is not integrated yet. A future
version can qualify it where it materially reduces target-preparation cost.
Production56708 unchanged; no push/deploy. Old heartbeat paused; broad goal active.

## 2026-09-30: matched full-continuation study admitted and training

The previous user-update turn was a status check while the goal was paused;
the goal is now active again. This turn made concrete progress and admitted the
actual scientific training comparison. Do not describe it as another diagnostic
or imply it was running during the earlier quiet period.

Population readback passed once: stack-context-population-v1-readback.json,
1.062 seconds. Seven depths, exact retained entry arrays and native geometry,
five fitting depths and held-out60/150. Sampler drops 3.8450197506053856e-8 of
BTN entry mass; support169/96. See STACK-CONTEXT-POPULATION-FINDINGS.md.

Lossless archive control passed once, session81361 exit0, source2,955files,
5,705,964,390bytes ->124,090,308bytes (45.98x). Changed duplicate refused and
interrupted retirement recovered; all legacy originals unchanged. Dynamic
scheduler check passed once, session15663 exit0: eight largest jobs,891MB,
byte-identical archives;49.734s compression/readback,3.10average CPUcores.
Both only copied/archived retained evidence; no new labels/fits. Their new-copy
raw files were retired after exact verification, never the historical originals.
Automatic approval initially rejected the first archive execution; read-only path
inspection established new-copy-only retirement, and the clarified execution was
approved. No unresolved permission block remains. Preserve registered sources.

LIVE SCIENTIFIC TRAINING: session77177, PID32368, process creation1790732866.143808.
Actual parent command and spawned workers verified. Admitted Unix1790732912.172981.
Registration SHA ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3.
Prefix stack-context-matched-learning-v1; store
S:\GTOpen-research\stack-context-matched-learning-v1.
Controller tools/research/stack_context_matched_learning_v1.py --run.
Last status: training A-baseline cycle1, staged; board and target workers live.
Verify the actual process/session and current outputs before subsequent decisions.
Do not duplicate/restart on an observation timeout; do not modify pinned inputs.

Read STACK-CONTEXT-MATCHED-LEARNING-PLAN.md and registration first. Two seeds x
362/387inputs,64jointcycles each, five contexts/cycle,169deals/context plus one
full root board, posterior64,32768visit reservoirs,256Adamsteps, equalcontext
weights, fourCPUtarget workers +oneboardworker and CUDA. Paired representations
must have identical source-generation/action-batch/board-plan identities. All
complete cycles are archived with source-byte authentication before raw duplicate
retirement; checkpoints/progress are published only at complete boundaries.
All64played generations0..63 must be evaluated with proper own-history weights;
generation64 is unplayed and excluded. No test-based checkpoint selection.

Fresh complete-policy evaluation protocol is frozen in the plan/registration:
4096physicaldeals/depth, seeds9309000+depth, seven depths, eight crossed profiles,
simultaneous bounded intervals over56contrasts. Its consumer implementation is
OUTSTANDING and must be pinned before fresh draws. Upstream averaged range
exports and separate correctly targeted continuation-prediction diagnostics are
also outstanding. Do not compare raw regret outputs against a single final
policy's EV, claim training loss is held-out accuracy, or relabel terminal
Fold/Call evidence as complete preflop accuracy.

This remains fixed-entry HU BB/BTN continuation research. Entry ranges come
from a retained200bb GTOpen approximation and are held constant acrossstacks;
they are not measured or stack-optimal openings. Wider-position/multiway/full
opening-range feedback and production promotion remain outside this trial and
necessary for the broad goal. No accuracy gain demonstrated yet.

Admission reserves45GBnewlogical against800GBglobalallocated;40GBSfree floor,
28GBRAMadmission/24GBrunning,2GBownCUDA. Twelve-hour invocations yield at complete
cycle boundaries; same attempt can continue with --run --resume after proving
the owner exited normally, not while it is still live. Overall training bound
72hours from admission. Terminal failure evidence forbids automatic scientific
retries. A complete but unadvertised cycle may be recovered from its actual
checkpoint/archive; no recollection of partialcycles. No deployment or push.
Production56708 unchanged; old heartbeat remains paused; broadgoal active.


## 2026-09-30: training continues; evaluation analysis/export/journal checks PASSED

Previous goal turn was a verified wait: actual PID32368/creation1790732866.143808
and its workers were confirmed live. This turn made concrete progress on the
independent evaluation consumer without changing the running scientific study.
At the latest check A-baseline and A-relative had each completed cycle1; B-relative
had started its first cycle. Session77177 remains the training handle. Actual
parent/child identities were rechecked; no failure artifact was present. All142
registered Python source hashes were checked unchanged. Do not restart/duplicate.

New checked helpers in tools/research:
- stack_context_matched_analysis_v1.py, check_v1: CPU synthetic56contrast checks,
  means/variance/tails and positive/adverse/inconclusive gates;7negativecases;
  0.11s, terminalexit0. Alpha=.05/7 per depth,4096deals,onefinal look preserved.
- stack_context_preflop_export_v1.py, check_v1: retained20/400bb nativecatalogs,
  syntheticpolicies vs independent1326x1326physicalcombo propagation;maxerror
  2.78e-15,zero-reach and6invalidcatalogcases;1.05s,terminalexit0.
- stack_context_evaluation_journal_v1.py, check_v1: CPU artificialcontext/fake
  payoff evidence,3recoverypoints/22rejections,exactchance/values/statistics;
  3.031s,295924logicalbytes,terminalexit0. Never touched actual scientific test
  hands, trained banks, native labels, CUDA or source evidence. No deletions.
  Store S:\GTOpen-research\stack-context-matched-journal-check-v1.

Attempt/result artifacts underOUT have prefixes stack-context-matched-analysis-
check-v1, stack-context-preflop-export-check-v1, stack-context-matched-journal-
check-v1. Preserve executed sources/results; do not repeat completed checks.
Read STACK-CONTEXT-EVALUATION-PREPARATION.md for evidence and consumer contract.
The journal's fixed32deal batches claim before sampling, pin exact intent, and
only commit authenticated seven-member evidence. It refuses automatic retries
of partial scientific batches. Openers must call prefix(verify_archives=True)
before new work; ordinary in-process prefix() avoids re-reading all packedbytes.

STILL OUTSTANDING: complete evaluator controller/source registration, final64
played-model bank selection (excludeunplayed64), combined/native evaluation
integration check on retained evidence, long-bank throughput, seven-depth fresh
4096deal evaluation, independentreadback, rangeexports and finalanalysis. Separate
correctlytargeted continuationprediction diagnostic also remains outstanding.
Do not run final evaluation before definitive training success and ownerrelease.
No new scientific experiment was launched, no push/deploy/production56708change.
Broad goal active; oldheartbeatpaused. No rangeaccuracygain established.

## 2026-09-30: complete evaluation consumer prepared; native integration PASSED

Previous goal turn was progress (a0292851: analysis/export/journal checks).
This turn implemented the complete final-bank selector, fixed-budget driver and
prepared evaluation controller. No scientific evaluation was admitted or run.
Training session77177/PID32368/creation1790732866.143808 was confirmed live again.
Latest status was B-baseline cycle1 archiving complete evidence; A-baseline,
A-relative and B-relative each had one committed cycle. No trainingfailurefile.

stack_context_final_bank_v1.py and check_v1 passed once:0.828sCPU,20rejects,
including the ACTUAL unfinished arm. Synthetic completion metadata verifiesall4
arms,64playedgenerations0..63,excluded64,weights1..64peractor(sum2080),matched
streams,registry partition and generation/source identities. Mockloader routing
read65references but returned64models. This is not actual64model scoring.

stack_context_evaluation_driver_v1.py connects the native8profile evaluator to
fixed32deal journal batches. stack_context_matched_evaluation_v1.py is prepared.
Default command is read-only readiness; --run requires definitive training
success/ownerrelease, unchanged inputs and all5implementation gates. --run --resume
is only the same admitted comparison at a normal complete boundary. No retry of
partial failed scientific work. Preserve frozen4096deals/depth,seeds9309000+depth,
alpha.05/7,all7depths and64playedmodels; do not change to a smaller/easier test.

stack_context_evaluation_integration_check_v1.py ran once, session65241, exit0.
Result13.047s/2,906,663newlogicalbytes. Retained2deal fixtures at20/60bb repeated
for32deal transport; synthetic routing models,2playedgenerations,4bankweight
combinations. Cached vsreference CPU complete policies,reach and actualnative
payoffs were EXACTLY equal in bothcontexts (296/622queryrows). Both nativeoutput
sets passed journal artifact checks. Separateinmemory drivercheck recoveredat64,
finishedexactly4096 with128calls,refusedpartialwork,verified finalarchive gate,
and reproduced finalanalysis. No actualscientifictesthands,trainedbanks,newfits,
GPU or productionchange. Store S:\GTOpen-research\stack-context-matched-evaluation-integration-check-v1.
The check's sourcepins/controllerhash bind the prepared consumer; do NOT edit
or rerun completed controls. Sources and attempt/result evidence are underTOOLS/OUT.

Read STACK-CONTEXT-MATCHED-EVALUATION-PLAN.md and
STACK-CONTEXT-EVALUATION-INTEGRATION-FINDINGS.md. Readonly default now reports
missing_checks:[], training_complete:false, research_owner_present:true,
scientific_evaluation_started:false. Restricted-shell Python could not see
installedpsutil; same command passed in full/escalated Python environment. No
packageinstallation or scientificretry was needed. All142registeredtrainingPython
sources were rehashed unchanged after preparation.

STILL OUTSTANDING: trainingcompletion, actual64bankthroughput/resourcebehavior,
scientific4096x7evaluation/rangeexports, independentresultreadback and plainEnglish
analysis. Prepare independentreader whiletrainingcontinues. Correctlytargeted
continuationprediction diagnostic remains separatelyoutstanding. Two-model native
integration is not an accuracyclaim or proof of long-bankperformance. No reason
to mark broadgoal complete. No push/deploy/production56708change; oldheartbeatpaused.

## 2026-09-30 12:40: terminal matching failure diagnosed; parallel work requested

Previous goal turn was a verified wait on session77177. This turn made concrete
progress on independent result auditing and responded to the user's explicit
request to parallelize independent comparison runs/use available hardware.

IMPORTANT: serial training session77177 definitively returned exit1. PID32368
is gone. Original failure at12:30:31 is preserved at
stack-context-matched-learning-v1-failure.json. A-baseline published cycle2;
A-relative finished/published its cycle2 checkpoint and metrics but failed before
archive/progress publication; its progress remains1. Both B arms remain1.
No scientific retry, restart, new evaluation or production change was made.

Read STACK-CONTEXT-PAIRED-CHANCE-FAILURE-FINDINGS.md. The cause is a false positive
in the raw paired_sources comparison: board-plan hashes include each arm's
parent_state_sha256, which legitimately differs after learning. Verified actual
archived baseline vs preserved relative cycle2 evidence: all70 other input hashes
match, all5 board draws/configuration/generations match, only parent_state_sha256
differs. Each plan equals the registered plan reconstructed from its OWN actual
generation1 model state. Proposed stack_context_paired_chance_v1.py plus one-shot
readback passed once in0.125s with30 rejected corruptions. Results/attempt under
stack-context-paired-chance-readback-v1*. No old records or markers changed.

Independent numerical/physical audit helpers also passed once: session71910,
exit0,18.547s,5synthetic payoff scenarios,56contrasts each,physical20/60/400bb
range checks,41corruption rejections. Prefix stack-context-independent-audit-
check-v1. Helpers perform no new deals/fits/native/GPU work. Full reader remains
UNEXECUTED DRAFT only at C:\Users\there\Documents\New project\.work\board-recovery\
stack_context_matched_readback_v1.py; not copied to repository or qualified.

Parallel prototype stack_context_parallel_continuation_v1.py was written to
reuse unchanged per-arm legacy training loops in4processes,20CPUtarget/board
workers total,2GBcuda perarm/8GBcombined,70GBtransientlogical reservation gated
by800GBglobalallocated cap. Source plan describes a normal12h legacyhandoff.
That plan is now OBSOLETE for this actual failed invocation. The one-shot
stack_context_parallel_continuation_check_v1.py failed its live-owner assertion
because training had already exited. Its failure evidence is preserved; it
performed NO CUDA check, no scientific work. Do NOT launch this v1 prototype,
edit executed sources, or pretend it qualified. A new adapter/control is needed.

Next: versioned correction and parallel continuation design; preserve failed
attempt; qualify chance-only cross-arm equality WITH own-parent identity checks;
recover only completed unpublished cycle2 artifacts without recollection; update
final-bank/evaluation/readback matching semantics and amendment provenance.
No automatic retry of a failed scientific cycle, no silent gate change, no new
experiment/push/deploy. Actual four-process GPU compatibility and full-cycle
throughput remain unmeasured. Production56708 unchanged; broadgoal active.

## 2026-09-30 13:02: four-arm continuation prepared; admission helper LIVE

Previous goal turn committed e7fceeb2 (diagnosis and independent audit).
This turn implemented stack_context_parallel_continuation_v2.py and its explicit
STACK-CONTEXT-PARALLEL-CONTINUATION-V2-PLAN.md. The original failed registration,
runner, failure and completed science remain unchanged. The v2 controller uses
separate immutable chance receipts: validate each plan against its own actual
parent, preserve all original raw source hashes, compare only matched chance
inputs across arms. New mismatches and undiagnosed partial cycles still fail.

The v2 CPU check ran once successfully, session92129 exit0, 21.14s. It restored
all actual completed prefixes (A-baseline2, A-relative1, B-relative1, B-baseline1)
and the already-complete unpublished A-relative cycle2. Its read-only dry run
executed the real recovery path with archive/publication mocked, forbade calls
to the scientific pipeline, stopped before cycle3, rejected nine wrong recovery
or chance identities, and verified old progress files unchanged. The printed
complete-cycle line in that check is MOCK PUBLICATION, not advanced progress.
Evidence: stack-context-parallel-continuation-v2-check-cpu-{attempt,result}.json.
Do not rerun or edit executed/pinned v2 sources/check/plan.

Four-process CUDA inference compatibility is STILL PENDING. No scientific
continuation has started and A-relative2 is not yet archived/published. The
GPU currently reports 100% utilization with about 16GB free; a heavy external
workload is running. Production port56708 was closed on inspection; we did not
start, stop or modify it. Normal desktop/video use remains allowed.

LIVE hidden admission helper: PID31052, creation1790739066.0216312, command
C:\Program Files\Python312\python.exe -B
T:\Dev\GTOpen\tools\research\stack_context_parallel_admission_v2.py.
Verified actual psutil identity and current status after launch; no failure.
Prefix stack-context-parallel-admission-v2; stdout/stderr logs under OUT.
Admission deadline1790782269.8999805, approximately 2026-10-01 01:01 Adelaide.
A scientific invocation admitted before that deadline may run beyond it under
its unchanged original deadline. Do not duplicate this helper or trainer.

Helper waits for three ready resource samples 30 seconds apart. Then it runs
stack_context_parallel_continuation_check_v2.py once (four simultaneous CUDA
scorers vs serial CPU reference using retained generation1 models/catalog).
If that passes, it invokes the v2 trainer --run. Read-only resource deferrals
may wait again; a started failed check/trial NEVER retries. Original failure
is recognized only through the pinned independent diagnosis. New terminal
failure requires review. On success four arm processes preserve per-arm cycle
order, with4target+1board workers each,2GBcuda/arm,8GBcombined. Logical reservation
70GB transient, still gated by800GBglobalallocated cap;24GBRAM/40GBS-free running
guards and original72h total/12h invocation bounds retained. User's heavier
workloads take priority. Expect conservative GPU waits during overlap; do not
silently loosen the guards. Measure actual completed overlapping cycles before
claiming a speedup. No speedup estimate or accuracy gain is yet demonstrated.

The v2 successful training result will be a NEW versioned path, leaving the
old failure intact. Outstanding: qualify CUDA/start verified parallel work,
recover existing cycle2 without recollection, complete64cycles/all4arms, update
final-bank/evaluation/independent-reader to authenticate chance receipts and
amendment (v1 consumers intentionally still refuse old failure/raw hash mismatch),
actual long-bank throughput, original4096x7fresh eval/rangeexports/analysis.
Do not launch old consumer, alter gates, discard failures, push, deploy or claim
broad goal complete. Independent reader draft remains only in local staging.
Goal stays active; old heartbeat stays paused.

## 2026-09-30 13:16: corrected continuation evaluator qualified, training still queued

Previous goal turn was progress: commit9a05539f implemented the guarded parallel
continuation, passed CPU recovery check and launched the live admission helper.
This turn made additional concrete progress while that helper waited on external
100%GPU utilization. Actual PID31052/create1790739066.0216312/cmdline reverified;
latest admission status was four seconds old, waiting-for-spare-resources, no
helper failure and no CUDA check/training started. Do not duplicate it.

NEW tools/research/stack_context_final_bank_v2.py authenticates corrected final
provenance without discarding raw hashes: all64cycles/fourarms, authentic complete
checkpoint trajectory, source hashes bound to archive plans, board manifests and
restored own-parent board plans, separate chance receipts and explicit amendment.
It preserves the original failure, all played0..63/weights1..64, and excluded64.
New terminal evaluation consumer stack_context_matched_evaluation_v2.py uses the
new versioned training result/store, retains original fresh4096x7/eight-profile
science, and requires the new provenance/transfer check in addition to old gates.
Plan: STACK-CONTEXT-MATCHED-EVALUATION-V2-PLAN.md.

One-shot CPU qualification stack_context_continuation_evaluation_check_v1.py
PASSED once, exec exit0,3.437s,20negative cases. Used synthetic64cycle selection
metadata plus actual retained A-baseline cycle1 archived board/model evidence
(receipt file transport mocked because append-only receipts are not published
until continuation admission). Reconstructed model/board provenance rejected
forged parents/boards even with changed receipt digests; raw differences with
identical chance were accepted; changed true chance, missing model/cycle evidence,
wrong correction IDs, invented recoveries and actual unfinished training refused.
No fits, fresh deals, native reruns or GPU scoring. This is implementation
qualification, not actual64model scoring or scientific improvement evidence.

The new consumer's Guard/evaluate/main parsed source is identical to v1; all
bound evaluation helpers/executables/constants match. The original native
integration's source inputs were reverified unchanged, and its result digest is
bound in the transfer check. We did NOT misrepresent that old check as directly
executing a new controller. New-check prefix stack-context-continuation-evaluation-
check-v1-{attempt,result}.json. Do not edit/rerun qualified/pinned versions.

IMPORTANT additional admission gate is explicit in the new consumer:
stack-context-final-bank-throughput-v1-result.json (NOT IMPLEMENTED/RUN YET).
It must bind SHA256(encoded(actual final selection)), be complete/passed,
full_played_banks_64=true,cuda_passed=true,reference_agreement_passed=true,
maximum_cuda_reserved_bytes<=2GB,new_scientific_deals=false,scientific_fits=false.
Use retained fixture hands for this implementation/resource check; not the fresh
scientific test stream. This prevents discovering a64bank memory problem only
after irreversible fresh-test admission. The gate producer must reconstruct
selection using final-bank-v2 helpers directly; controller.specification() itself
requires the gate and is not the producer. Selection loading/authentication and
corrected provenance helpers are callable independently after terminal training.

Still pending: waiting helper's CUDAqualification and four-arm continuation;
actual cycle2 recovery/publication;64cycles/allarms; actual64bank check; complete
fresh evaluation/rangeexports; independent readback + plain-English analysis;
separate targeted prediction diagnostic. Full reader remains UNEXECUTED v1 DRAFT
only at local staging .work/board-recovery/stack_context_matched_readback_v1.py.
It still references old result/raw equality and must be adapted/qualified for v2
before any use. No scientific evaluation admitted; no push/deploy/production
change. Broadgoal remains active; oldheartbeat remains paused.

## 2026-09-30 13:28: actual-final-bank resource gate producer prepared/CPU-qualified

Previous turn was progress:18b83573 added and qualified the corrected evaluation
consumer/provenance selector. The full independent reader is STILL an unexecuted
staging draft; 'reader' in the short final update referred to this consumer, not
completion of the independent scientific readback.

This turn prepared tools/research/stack_context_final_bank_throughput_v1.py,
its CPU check and STACK-CONTEXT-FINAL-BANK-THROUGHPUT-PLAN.md. --prepare ran once
successfully, exit0: froze the FIRST32 distinct complete physical hands from
A-baseline cycle1 at20bb, original order, authentic source-generation/archive
bytes. No new draws; no outcome-based selection; this is not two repeated hands.
Fixture under OUT/stack-context-final-bank-throughput-v1-retained-fixture.json.
All seven depths will reuse those32 already-recorded hands. No scientific test
stream is consumed; the batch seed0 identifies this fixed query fixture only.

stack_context_final_bank_throughput_check_v1.py ran once, exit0,0.547s,13negative
cases. Verified all seven depth/batch contracts, source fixture, deep-copy
isolation, probability/reach shape/normalization/finiteness/zero-support checks,
actual unfinished final-bank refusal, CPU-reference worker control flow and
.npy/result hashes using explicitly synthetic reference outputs, and failure/dead
worker propagation. No actual final models, GPU, native invocation, scientific
fit/deal, or parallel-process-runtime qualification. Evidence prefix:
stack-context-final-bank-throughput-v1-check-{attempt,result}.json.
Check store S:\GTOpen-research\stack-context-final-bank-throughput-v1-check.
Do not edit/rerun these executed/pinned sources, fixture or plan.

--run remains UNEXECUTED and gated until all actual64-cycle banks finish with
released ownership. Producer independently reconstructs exactly evaluation-v2's
bank selection (without calling its circular specification gate), verifies the
explicit correction and every authentic cycle/model/chance receipt. It will
load all four64-model CUDA banks together at each of seven depths, exactly as
in evaluation; score32 retained physical deals; compare with four persistent
CPU reference processes (one arm each, full.average, authentic models loaded
once, CUDA hidden). Save all probability/reach arrays, input identities, timings,
peak CUDA reserved bytes. Strict p error<1e-10/support<1e-8/samezero-support/
normalization checks,2GBCUDA cap,3GBnewlogical evidence/800GBglobal allocated cap,
4h check bound,40GBRAMadmit/24GBrun/40GBSfree. Heavier work/production has priority.
Only this check's read-only CPU children may be cleaned up on failure; never
scientific training/production. No automatically repeated failed check.

Future actual success writes exactly the throughput result path required by
evaluation-v2. The result binds SHA256(encoded(final selection)),all64played,
CUDA/reference agreement,peak<=2GB,and no fresh scientific deals/fits. Current
CPU check DOES NOT satisfy that actual-bank gate or prove full-evaluation speed.

LIVE admission helper PID31052/create1790739066.0216312/cmdline reverified at13:28;
status19seconds old,still waiting-for-spare-resources,GPU100%,~16.2GBfree, nofailure
or CUDAcheck/trainingstart. Do not duplicate helper. Originaldeadline/admission
window unchanged; no production/push/deploy. Goal remainsactive,oldheartbeatpaused.
Next independent work: adapt/qualify the full reader draft for v2 correction;
then monitor actual continuation, measure overlapping cycle throughput, complete
training,run actual-bank gate,originalfresh evaluation and independentanalysis.

## 2026-09-30 13:47: independent final reader qualified while parallel helper waits

Previous progress commit1b0d8d5b prepared the actual-final-bank resource gate.
This turn prepared independent full readback and passed its CPU implementation
check. Qualified reader is tools/research/stack_context_matched_readback_v3.py,
plan STACK-CONTEXT-MATCHED-READBACK-V3-PLAN.md, check/result prefix
stack-context-matched-readback-check-v3. It remains UNRUN on actual scientific
results: successful terminal training and fresh evaluation are still required.

The first v2 CPU check failed on its synthetic range fixture: it passed the
in-memory export with tuple paths to a reader expecting JSON list paths from
disk. Its source, attempt and failure are preserved. V3 changes the fixture to
serialize/parse actual JSON transport. Reader analysis is unchanged; only its
versioned output/plan/check paths differ. This was implementation qualification,
not a repeated scientific attempt, new sample, or change in comparison gates.
V2 reader is unqualified; do not use it for final analysis.

V3 CPU check ran once, session40458 exit0,19.937s,39 negative cases. It rechecked
retained native integration evidence at20/60bb and four two-generation model
banks; independently rebuilt physical catalog ancestry and full range-policy/
reach bindings using a synthetic64-generation policy; reconstructed actual
A-baseline cycle2 board draws from seed/generation and sealed own-parent state.
The real immutable cycle archive was read/authenticated; only the not-yet-
published chance receipt file transport was mocked. No GPU, native rerun,
scientific deals/fits, actual final64model review, or accuracy result.

New stack_context_independent_chance_audit_v1.py does not call the training
comparator or final selector: reconstructs PCG64/SeedSequence draws directly,
checks own-parent seals and actual original archived bytes, preserves all75raw
identities and compares only the5chance projections. Final reader will audit
all256cycles,65models/arm,896evaluationarchives,all8crossings/labels/payoff
bindings,14prespecified first/last test-batch CPU reference replays,28complete
physical preflop range replays,and independent56contrast/tail/normalized math.
It is not an independent native poker oracle, does not replay every postflop
policy row, does not claim strict board-disjoint draws, and leaves separate
prediction diagnostic/fullpreflopaccuracy unresolved.

Live parallel admission helper PID31052/create1790739066.0216312/cmdline was
reverified around13:47. Status12.8seconds old, waiting-for-spare-resources,
GPU100%,~16.2GBfree,control_complete=false,training_started=false. NVIDIA lists
HeroesOldenEra.exe among graphics workloads; don't interrupt it or infer exact
per-process utilization from listing alone. Normal desktop/video sharing stays
approved. No duplicate helper, no changed pinned runner/gates, no production
change. Admission deadline remains approximatelyOct1 01:01Adelaide. Published
prefix stillA-baseline2/A-relative1/B-baseline1/B-relative1; completed unpublished
A-relative2 remains recoverable without recollection. No actual parallel speedup
has been measured yet. Goalactive; oldheartbeatpaused; no push/deploy.

Next: allow existing helper to qualify four simultaneous CUDA scorers and admit
parallel training when resources permit; measure overlapping completed cycles;
finish64cycles/arm;run actual64-bank retained-fixture resource gate;original
4096x7fresh evaluation; qualified readbackv3 and plain-English analysis.

## 2026-09-30 13:53: parallel resource observer LIVE; original helper unchanged

Previous turn was progress:fbf9f822 qualified independent reader v3 against
retained evidence. At this turn's start, the same admission helper was verified
live with matching creation identity and current output; GPU still100%. No
CUDA check or scientific continuation had started, so no retry or duplicate.

Audited parallel CPU setup: four independent coordinators, each with four
river-target workers and one board worker; BLAS/OMP/MKL limited to one thread,
worker threadpool limits1 and coordinator Torch threads1. Native example entry
points have no explicit Rayon/par_iter calls in the inspected sources; this is
not a complete runtime call-graph/thread-utilization proof. Actual sampling is
needed. The inherited per-arm GPU guard can see other research arms' device-
wide work, so do not presume every reported high-GPU wait is external pressure.
Pinned runner/helper/guard and scientific gates remain unchanged. Measure actual
completed overlap before deciding whether a separately qualified scheduling
change is warranted. Reported arm status can remain after its phase finishes;
status labels alone do not measure current wait duration.

NEW read-only tools/research/stack_context_parallel_observer_v1.py tracks ONLY
helper PID31052/create1790739066.0216312 plus its verified child tree. Launched
hidden once: observer PID94544/create1790742127.8768475, --watch. Both exact
process identities verified after launch; .jsonl first sample exists, stderr
empty. Prefix stack-context-parallel-observer-v1 in OUT. Do not duplicate.
Samples every60s while waiting,15s with child work; maximum25h/25MB; reads process
CPU counters/RSS/threads, whole-device GPU/memory/power, host CPU/RAM, current arm
statuses and changed published cycle counters. Writes telemetry only, never
launches/stops research, modifies inputs/locks/gates, or touches production.
Short-lived children may be missed; GPU use is not attributed per process.
It ends when the exact tracked helper exits or its own telemetry bound expires;
a terminal state file does not alone establish process exit. An observer failure
is separate from a scientific failure. Observer first standalone snapshot's CPU
sample was unprimed; before watching, changed telemetry-only CPU sampling to a
bounded0.1s sample. Source digest is recorded in its attempt; study inputs were
not altered. No scientific test was run to check this low-impact telemetry tool.

Current hardware sample: GPU100%,about411W/~15GBVRAMfree,~96GBRAMfree; consistent
with substantial active GPU work, not the earlier low3D screenshot. Leave the
user's heavier application alone. Normal video sharing remains approved.
Next actual work remains existing helper admission, four-worker CUDA check,
parallel cycles, final64-bank resource gate and fresh registered comparison.
Goalactive; no push/deploy/production changes; source/results preserved.

## 2026-09-30: retained timing audit identifies the current bottleneck

Previous goal turn was a verified wait: the exact admission helper and observer
were confirmed live with current output; no trial was restarted. This turn
completed a timing analysis of all six cycles completed before the original
publication failure (five published plus complete unpublished A-relative2).
Evidence: stack-context-retained-timing-audit-v1.json and
STACK-CONTEXT-RETAINED-TIMING-AUDIT.md. All archived metric bytes and raw worker
reports were authenticated; 87 immutable input files are recorded. No new
samples, fits, native runs, GPU work, scientific inputs or production changes.

Six-cycle aggregate recorded pipeline time2822.421s; target collection2767.753s
(98.063%); GPU optimizer14.937s(0.529%). The impossible elimination of every
optimizer second gives only1.00532x for this early pipeline. In A-relative2,
river target construction is95.576% of summed worker elapsed intervals. Mean
worker elapsed overlap by context is2.63-3.00 with the existing four-worker
pool; board work already overlaps. These are not measured CPU utilization:
worker intervals include I/O/waits, collection includes inference/native/
preparation/serialization/resource waits, and pipeline timers exclude outer
archiving/publication. Early cycles do not predict later reservoir growth.

Implication: prioritize measuring four-arm target-preparation overlap over
additional GPU optimizer-kernel work. Actual completed end-to-end throughput
and observer telemetry must establish gains or identify contention/sibling
GPU waits before changing scheduling further. No claimed parallel speedup or
accuracy result. Existing helper and observer remain the only background jobs
for this continuation; keep pinned gates/inputs intact. Goal stays active.

## 2026-09-30: retained CPU profile completed; scoring preparation dominates

Previous turn was progress:a73ffc6b authenticated timing evidence from all six
completed early cycles. This turn profiled one predetermined retained chunk:
A-relative cycle2, first context, batch0, history/selected chunk0. Tool:
stack_context_retained_cpu_profile_v1.py; evidence prefix
stack-context-retained-cpu-profile-v1; plain-English findings in
STACK-CONTEXT-RETAINED-CPU-PROFILE.md. No native execution/new samples/fits/GPU
or changed study sources. One CPU math thread, below-normal process priority,
300s/24GBRAM running bound. Original helper was verified live and waiting at
admission; current GPU100%, about96GBRAMfree,CPU34.7% left headroom for one thread.

First diagnostic launch stopped BEFORE attempt creation due to slash/backslash
artifact-key lookup; corrected this unadmitted profiler's Windows path lookup.
No scientific attempt repeated. Successful run session57474 exit0,8.969s.
Ordinary replay:40534history rows,prepare2.2763s/infer0.3386s;5671selected rows,
prepare0.2470s/infer0.0394s. Preparation86.974% of combined scoring time. Fresh
instrumented replay matched original arrays too; both runs had probability
error0 and identical positive/zero support. All recorded inputs/profile hashes
reverified. CUDA not initialized. Pstats files retain full call data.

Instrumented history profile: four preflop-table apply scans1.018s cumulative,
CurrentPolicy._features2.010s(includes visible validation/card/public/relative
features),relative_features0.720s within that; neural infer0.340s. These nested
costs must not be added together; instrumentation changes timings. Tables scan
all rows before skipping postflop. Candidate for later qualification: apply
preflop-only overlays to preflop rows after preserving all shared validation,
indices and precedence. Do not silently change the pinned active pipeline.
This is a scoring fixture, not all river target-generation costs; native
transport/posterior/archives remain outside the profile. No measured parallel
speedup or scientific accuracy gain. Keep current helper/observer, GPU priority
policy,64-cycle horizon and comparison gates unchanged. Goal remains active.

## 2026-09-30: CPU routing candidate qualified, not installed in this study

Previous turn was progress:300c24d1 profiled an authenticated retained chunk and
identified redundant preflop-table scanning of postflop rows. This turn added
SEPARATE stack_context_current_policy_routed_v1.py and its one-shot CPU check.
Original CurrentPolicy, registered pipeline, helper/runner and final readers
remain unchanged. This candidate is not imported by scientific training.

Candidate inherits original model/feature/inference methods. prepare preserves
history validation and canonical feature/public-menu checks, retains the table
contract's one-action postflop rejection, then routes only preflop rows through
the original overlay.apply methods in original order. Maps local matched IDs
back to original full-query indices; original own-action links remain intact.

stack_context_routed_policy_check_v1.py ran once, session16456 exit0,24.015s.
76 exact equivalence cases:362/387inputs,initial/learned routing fixtures,all7
stack depths,all4streets,score-only postflop,all initial hand classes on5fitted
contexts.32 malformed-input checks preserve rejection,including a consistent
one-action postflop public menu. Features/keys/ancestors/masks/table values and
inferred probabilities match exactly. Existing real A-relative generation1
history40534rows/selected5671rows match original saved arrays exactly too.

Retained component timing,2repetitions per implementation in ABBA order,fresh
cache: original median2.823454s,candidate1.972043s; ratio1.43174x (~30.15% less
time). One CPU math thread/below-normal priority; CUDA not initialized. This is
not whole river-target generation, full-cycle throughput, GPU qualification,
native solver speedup or scientific accuracy evidence. It uses existing data
and fits; no new deals, fitting or native runs. Inputs reverified after check.
Evidence prefix stack-context-routed-policy-check-v1; plain-English note
STACK-CONTEXT-ROUTED-POLICY-CANDIDATE.md. Preserve fixed scientific inputs and
qualify any actual integration separately before adoption.

Current original helper PID31052/create1790739066.0216312 and observerPID94544
were reverified live; latest helper output still waiting-for-spare-resources,
GPU100%,about16GBfree,no scientific continuation admitted. Do not duplicate.
Keep user GPU priority/light-video policy and all comparison gates. Goalactive;
no push/deploy/production changes. Next scientific step remains parallel CUDA
qualification/admission when the user's heavier GPU workload frees capacity.


## 2026-09-30: batched CPU preparation candidate v2 qualified, not installed

Previous goal turn was a verified wait: the exact admission helper and observer
were live, with current GPU100% output, no CUDA check/training admitted. This
turn inspected remaining CPU preparation cost and reused the already-qualified
bulk river-feature implementation in a SEPARATE current-policy candidate.
Registered original sources, helper, runner and scientific gates remain intact.

Candidatev1 CPU check passed78cases/32negativecases, session97274 exit0. Inspection
then found row views could retain whole batch arrays; preservedv1 and implemented
v2 independent100-byte cache rows. v2 CPU check session79647 exit0,
30.797s passed78cases/32negativecases, including9000distinct visible keys+
64revisits, cold/warm cache eviction, exact original LRU order/cache values,
features/indices/overrides/probabilities. Both numerical evidence sets preserved.
The synthetic visible-query stress fixtures are not scientific sampled deals.

Retained v2 ABCCBA medians,2each: original2.837641s,
routed1.812890s,batched1.535005s;1.84862x scoring
throughput vs original,45.91% less time. Component only;
not full-cycle/parallel/native speed or poker accuracy. One CPU math thread,
below-normal priority; CUDA never initialized; no new fitting or native runs.
All249 inputSHAs reverified. Source/test prefix stack_context_*batched*,
evidence stack-context-batched-policy-check-v2,doc
STACK-CONTEXT-BATCHED-POLICY-CANDIDATE.md. v2 candidate NOT imported by registered
training. Any adoption requires qualified integration and explicit provenance.

At about14:27 the same helperPID31052/create1790739066.0216312 and observerPID94544
were verified live with matching command lines. Latest helper GPU100%,~16GBfree,
waiting-for-spare-resources;training_started=false,control_complete=false.
Leave heavy user workload alone; normal video sharing remains approved.
No duplicate helper, scientific restart, push, deployment or production change.
Next required work stays four-worker CUDA admission/parallel64cycles/actual64bank
resource gate/fresh4096x7comparison/readbackv3. Goalactive; oldheartbeatpaused.


## 2026-09-30 15:18: GPU check passed; parallel admission storage failure; lossless compression LIVE

User reported GPU available. The original helper ran its CUDA qualification
successfully (stack-context-parallel-continuation-v2-check-result.json): all4
scorers overlapped,5304rows each,maxCPUreferenceerror1.30e-14,combinedreserved
226492416bytes,9.547s. No fits/newdeals; original qualified sources unchanged.
Its childPID99304/create1790746721.89801 then exited BEFORE amendment/LOCK/any
scientific cycle, failing the global reservation check. Original helperPID31052
terminated with preserved stack-context-parallel-admission-v2-failure.json at
15:09:41. Its old observer also exited. Do not claim training resumed or restart
the failed helper. runner v2 itself has NO failure/amendment/invocation yet;
after diagnosis/resource recovery an explicitly reviewed admission may reuse
the unchanged qualified runner/control without repeating scientific cycles.

Read-only global inventory:745106644870allocated bytes; current study2149139595;
70GBreservation projects812957505275 against800000000000cap (12.958GBshort).
S: has325.64GBphysicalfree. Do not raise cap or reduce scientific budgets silently.
Saved readonly uncompressed candidate inventory in
stack-context-parallel-storage-candidates-v1.json. Completed checkpoint test
S:/GTOpen-research/checkpoint-long-v1 has36.577GBuncompressed; oldstatuscomplete,
oldreviewpassed, no live owner. Qualified per-file NTFScompress implementation
reused with all paths/hashes/sizes/mtimes preserved, no deletion/move/rearchive.

LIVE compression: session4008,PID32004/create1790747284.3366125,
tools/research/stack_context_parallel_storage_release_v1.py. Prefix
stack-context-parallel-storage-release-v1 in OUT. Four CPU compression workers,
below-normal parent,hidden compact.exe children,1800sbound,target18GBsavings.
Research LOCK owned by this compressor while active. BEFORE/AFTER records per
processed file preserveSHA256 and allocation; must inspect terminal result and
actual savings before admission. First4files saved425081824bytes; do not assume
18GBwill be achieved. If less, preserve all evidence and inspect other completed
files for byte-preserving storage recovery; do not treat this as a scientific
retry. Every existing checkpoint/negative fixture remains readable unchanged.

No new training cycle, change to settings/inputs, push/deploy or production56708
change. Next verify compression terminal outcome, remeasure globalreservation,
then reviewed readmission of UNCHANGED qualified parallel runner. No duplicate
live processes. Original64cycles/arms/fresh4096x7evaluation/readbackv3 unchanged.
Batched CPUcandidate6a9eda4d remains separate and not installed.


## 2026-09-30 15:29 Adelaide - storage recovered; unchanged parallel runner launched

Both compressors have exited and released their lock. V1 completed 161 byte-preserving file compressions, but ended with an explicit operational target-shortfall failure (2.641 GB incremental per-file savings versus its 18 GB target). Preserve that failure. V2 completed successfully: 284 files, 6,007,992,780 incremental allocated bytes saved, with paths, SHA256, lengths and modification times verified. Neither deleted files or repeated scientific work. NTFS compression also affects hardlink aliases: registered per-path allocation decreases are not a measurement of unique physical space reclaimed.

The independent three-root allocation scan now projects 797,740,117,788 bytes including the unchanged 70 GB study reservation, below the unchanged 800 GB cap. S: physical free space was 333.89 GB. GPU admission was available (23.19 GB free VRAM, 9% utilization) and RAM available was 101.89 GB. Existing scientific progress stayed A-baseline 2, A-relative 1, B-baseline 1, B-relative 1. No parallel scientific attempt had started in the failed launch; amendment, failure, result and invocation were absent.

A separate reviewed resource-readmission record binds the original pre-admission failure/log, compression receipts, registration and already-passed CUDA qualification. Do not rerun the qualification or failed admission helper. The unchanged qualified parallel runner was launched ONCE, hidden, at 15:28:52: PID 75720, creation 1790747932.4205804; command tools/research/stack_context_parallel_continuation_v2.py --run. At this writing it is completing its own admission and input checks; four active scientific arms are not yet verified. Logs: stack-context-parallel-resource-readmission-v1-stdout.log and -stderr.log. Verify exact process identity plus current arm statuses before claiming training is live. Preserve all old failures and incomplete evidence; no scientific retry, changed budgets, GitHub push, deployment or production changes.


15:31 Adelaide update: all FOUR arm workers verified live as direct children of PID75720 with matching creation times and fresh status. A-baseline PID98836/create1790747994.7217212 is on cycle3; A-relative PID100152/create1790747997.5592933 is archiving the previously completed cycle2 without retraining; B-relative PID94212/create1790748000.4328887 and B-baseline PID83740/create1790748003.4320004 are on cycle2. Parent status is parallel-training; both launch logs contain no errors. Snapshot saved as stack-context-parallel-resource-readmission-v1-live-confirmation.json. Measure actual completed-cycle throughput before claiming any speedup. Continue normal monitoring without duplication or input changes, then the registered 64-bank resource gate, fresh evaluation and independent readback after terminal training success.


## 2026-09-30 15:34 Adelaide - initial parallel resource measurement

Read-only 50.778-second sample saved as stack-context-parallel-live-resources-20260930-1533.json. The five full sampling intervals measured whole-machine CPU 54.9-68.3% (mean 63.18%); GPU samples were 7-9%, with about 3.5 GB VRAM used. Whole-machine CPU includes other applications. Surviving study descendants alone accumulated 477.188 CPU-seconds, at least 9.40 logical-core equivalents; that lower bound excludes terminated native child processes and the parent coordinator. Three fresh-cycle arms each advanced to context-complete while A-relative preserved/archived its already-completed cycle2. All four process identities remain live. This shows actual simultaneous target preparation, not a measured full-cycle speedup or a new accuracy result. Keep the existing run unchanged, measure full cycles after publication, and preserve the separate CPU candidate for a later qualified integration.


15:38 Adelaide: A-relative cycle2 is now durably published with recovered_without_scientific_repeat=true. Its checkpoint and archive metadata hashes were rechecked and its chance-input identity matches A-baseline cycle2. It moved on to fresh cycle3; the other three arms also remain live and advancing through contexts. The logged 542.906 seconds is the ORIGINAL recovered collection time, not a new parallel-cycle measurement. Readback receipt: stack-context-parallel-recovered-cycle2-publication-v1.json. No new failure, retry or deployment. Remaining: finish all64cycles/arm, final-bank resource gate, fresh seven-depth evaluation, independent readback, and the separately outstanding correctly targeted prediction diagnostic.


First NEW parallel scientific cycle durably completed: B-baseline cycle2. Checkpoint/archive metadata hashes verified, recovered_without_scientific_repeat=false. Collection-and-fitting took707.703seconds; this excludes subsequent archive publication. Current published counts A-baseline2/A-relative2/B-baseline2/B-relative1. Parent PID75720 remains identity-verified/live. Receipt stack-context-parallel-first-new-cycle-v1.json records exact observation/publication times and identities. Startup/recovery overlap and only one new completion make a full-throughput comparison premature. Do not count recovered A-relative2 as new work or infer accuracy from operational success. Continue the existing run unchanged.


## 2026-09-30 first complete parallel round

Read-only observer session14938 exited0 after440seconds, with all four new targets retained: A-baseline3, A-relative3, B-baseline2, B-relative2. Parent75720/create1790747932.4205804 remains live and the arms are proceeding. No observer or earlier wait session remains active.

Saved stack-context-parallel-first-round-observation-v1.json and -analysis-v1.json. Independent metadata checks authenticated each checkpoint and archive index/retirement, and paired chance identities matched for both A cycle3 and B cycle2. All four records have recovered_without_scientific_repeat=false. This is operational verification, not the final scientific readback.

Elapsed collection-plus-fitting / archive interval / start-to-retirement seconds:
- A-baseline3:912.735 /410.929 /1343.181
- A-relative3:834.016 /370.028 /1218.133
- B-baseline2:707.703 /313.953 /1039.057
- B-relative2:982.672 /422.149 /1421.932

The first-round makespan was1701.563seconds (28.36minutes), including A-relative's delayed start after recovery of old cycle2. First-round aggregate throughput8.46newcycles/hour is not a steady-state forecast. Summed individual intervals/makespan2.95 measures overlapping execution, NOT a speedup factor versus a matched serial baseline. Native workload changes with seed/generation/policy. Status messages are last-emitted events: a yielding label can remain after work resumes; the brief observed GPU waits cleared without intervention. No new failure or scientific retry.

Continue the unchanged parent. Still required: all64cycles per arm, the actual64-bank resource check,4096x7 fresh evaluation, independent readbackv3, plain-English analysis and the separately outstanding correctly targeted prediction diagnostic. Do not claim the broad goal complete or deploy from these timings. Separate CPU candidates remain uninstalled.


Prepared STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md during the unchanged live run. It clarifies that current outputs target a source-weighted mixture of training advantages, not final-policy action EV. A future separate supervised comparison would use identical fixed-teacher advantage labels for both representations, with A-baseline's complete played bank chosen before seeing results, no best-arm selection, strict postflop split semantics and an explicitly separate preflop holdout. It states the current extra25features are river-only. Exact budgets/seeds/native target semantics/teacher integration/source identities remain unimplemented and unregistered. No labels, fits, native jobs or new scientific experiment were launched. This design does not satisfy the outstanding prediction diagnostic by itself or alter the main fresh evaluation.

## 2026-09-30 16:20 Adelaide - parallel workers disappeared; recovery audit complete

The original parent75720/create1790747932.4205804 and all four exact child identities are absent. No normal runner failure, outcome or terminal result was recorded; stderr is empty. Last parent event was around16:08. The OS did not reboot. New Codex runtime processes appeared at16:08; this is a correlation, not an established termination cause. Training is NOT currently live. The stale research lock75720 is preserved pending controlled recovery, not blindly removed.

Read-only interruption audit succeeded: stack-context-parallel-interruption-audit-v1-result.json binds9,400 files/16,757,747,747logicalbytes and authenticates176worker manifests. It restored all previous checkpoints plus the complete unpublished A-baseline cycle4 and B-relative cycle3 checkpoints. Their archives contain68/211 and46/211 complete bundle/manifest pairs respectively; no orphans, no index or retirement yet. Published counts remain3/3/3/2 (A-baseline/A-relative/B-baseline/B-relative). A-relative4 completed3contexts and part of the fourth; B-baseline4 is partway through its first context. Preserve every original source, outcome and failed evidence.

Next: qualify and complete only missing archive transport for the two complete cycles, preserving raw files and existing bundles; qualify deterministic reconstruction of retained partial-cycle state before any continuation; arrange durable process lifetime before scientific readmission. No scientific cycle may be blindly repeated. Existing seeds, targets, budgets, original deadline, evaluation gates and production56708 remain unchanged. No new experiment, push or deployment. The correctly targeted prediction diagnostic is still design-only. Goal active; interruption recovery is in progress.

## 2026-09-30 16:49 Adelaide - qualified recovery launched through Windows Task Scheduler

Archive-only recovery completed successfully in434.875seconds: reused68+46 existing bundles, packed143+165 missing bundles, authenticated both ordered indexes. All6526raw files were retained, no native calls/fits/new samples, and progress was not published during that operation. Result prefix stack-context-archive-transport-recovery-v1.

Retained-state reconstruction check passed across all10contexts of A-baseline4 and B-relative3 in66.406seconds: reservoir arrays, sampler/action/reservoir RNG, root/exact accumulators matched their complete checkpoints exactly. Read-only transport checkv2 passed45.422seconds, preserving all original outputs and reproducing interrupted-fixture bytes for both representations. Original target math AST remains unchanged. Final GPU collector checkv2 passed46.718seconds: both representations restored exact retained arrays/RNG through the actual recovery collector, no native calls or fits in this successful check.

Preserve two failed qualification records: transport-checkv1 fixture incorrectly omitted the recorded native stderr (corrected only in v2 fixture); collector-checkv1 mistakenly submitted the original worker callback, whose native bridge launches rejected existing output paths. All9400interruption files were subsequently SHA-verified unchanged. Collectorv2 explicitly dispatches the retained-result callback. These were qualification defects, not discarded/restarted scientific cycles.

A hidden, triggerless45-second Windows Task Scheduler probe completed with exit0 and a Windows services parent chain; its invoking command had already ended. Probe task removed. This establishes independence from Codex's process tree; it did not simulate a reboot. Result stack-context-durable-lifetime-probe-v1-result.json.

Demand-started task GTOpen-stack-context-durable-recovery-v1 now invokes tools/research/stack_context_durable_recovery_entry_v1.py via pythonw.exe. No scheduled trigger, automatic retry, task restart or production changes. Admission prefix stack-context-durable-recovery-entry-v1. The entry first runs once-only interrupted-cycle recovery, then launches UNCHANGED stack_context_parallel_continuation_v2.py --run once, only after successful recovery and lock release. Actual live PID/status must be verified. Recovery first publishes the two existing complete checkpoints from their verified archives, then completes A-relative4 and B-baseline4 simultaneously using retained outputs and unchanged ordered state. Expected recovered counts A-baseline4/A-relative4/B-baseline4/B-relative3. Its reviewed ownership transfer records the old stale lock content/hash before atomically claiming it. Original72hdeadline,64cycles/arm,seeds/models/targets/fits/evaluation gates,70GBlogical and800GBglobal caps remain unchanged.

Before any final fresh evaluation/readback, extend their provenance checks to require the new interruption-recovery amendment/result and validate each recovered record. This is still required; don't silently skip it. No broad accuracy result, push, deployment or goal completion. Follow the durable-entry/recovery/training process identities plus fresh logs; do not duplicate/retry if an observation session disappears.

16:49 live identity check: durable scheduler entry84788/create1790752536.9318762 (Windows services parent2980), recovery parent96316/create1790752537.165662, workers85640/create1790752582.0532353 and98856/create1790752582.059226 are all identity-verified live. Both full checkpoints published without refitting (A-baseline4 and B-relative3), so current counts4/3/3/3. The workers have moved to the two partial cycles. A-relative is reconstructing completed contexts before finishing its retained partial context; B-baseline is finishing its retained first context. Logs currently have no errors. Four-way future-cycle training has NOT started yet; the durable entry will launch the unchanged v2 trainer only after recovery success/released lock. Current live confirmation saved in stack-context-durable-recovery-live-confirmation-v1.json. Continue by verifying process identity plus fresh recovery outputs, then update final evaluation/readback provenance while the unchanged trainer runs. Never assume an observer timeout means the actual scheduler-owned task stopped.

## 2026-09-30 17:23 Adelaide - interruption recovery complete; four-way trainer LIVE; final consumers qualified

The once-only interrupted-cycle recovery completed successfully at about17:00:42 in903.609seconds. It published existing full A-baseline4/B-relative3 checkpoints without refitting, and continued retained partial A-relative4/B-baseline4 work without resetting their streams or discarding results. All9,400 preinterruption file identities remain bound to the completed archive plans/original bundles. Original registration, seeds, fit budgets, gates, storage limits and deadline remain unchanged. Preserve all failures and the old stale-lock ownership record.

The Windows services-owned durable entry84788/create1790752536.9318762 automatically launched the UNCHANGED original parallel-v2 trainer once at17:00:43: PID94544/create1790753443.077002. It owns the research lock. Latest independent check verified its parent and all four worker identities plus fresh status: A-baseline100604/create1790753511.185391, A-relative93416/create1790753512.997676, B-relative104568/create1790753514.858373, B-baseline81788/create1790753516.790518. Published counts are now5/5/5/4 (A-baseline/A-relative/B-baseline/B-relative), so all four have completed new scientific work after recovery. No current trainer failure. Do not duplicate or restart it based on an observer timeout. Its scheduler-owned lifetime remains independent of Codex, but no OS reboot recovery is claimed.

Completed-boundary readback-v1 passed1.938seconds: exact four recovered prefix hashes, original audit9400members, archive/checkpoint/amendment bindings, retained original archive bytes and all pinned qualifications. Full new archive payload authentication remains part of the final reader; this receipt is not a scientific accuracy result.

Final consumers were extended in NEW versions; old registered/qualified source files remain intact. final-bank-v3 authenticates the recovered prefixes and translates only their four recognized marker fields before delegating to unchanged v2 selection. Evaluation-v3 retains identical Guard/evaluate/main AST, helpers, 4096x7 deals, seeds, selection/weights and confidence/gain gates. Throughput-v2 retains identical function AST and the exact original32-hand fixture. Reader-v4 retains the numerical/range/transport/model/chance audit math, with additional immutable recovery bindings. All qualifiers passed without native execution, fitting, new scientific draws or CUDA: provenance15negative cases; selection/evaluation23; resource plumbing13; independent reader39. Reader fixtures used actual retained native/model/archive evidence, with clearly recorded synthetic ranges/metadata and receipt transport. These qualification results do NOT review actual completed64-model banks or the future scientific comparison.

Source/test/evidence prefixes: stack_context_interruption_provenance_v1, stack-context-interruption-readback-v1, stack-context-continuation-evaluation-check-v2, stack-context-final-bank-throughput-v2, stack-context-matched-readback-check-v4. Final consumer receipt stack-context-recovery-consumer-checks-readback-v1-result.json authenticated all five controls/current source pins and live identities;90corruption rejections in total.

Next: leave the existing four-way trainer unchanged until64cycles/arm or its legitimate invocation/deadline boundary. Then, only after successful terminal training and released lock, run actual throughput-v2 --run once against the fixed retained fixture; admit evaluation-v3 --run only on its complete passing gate; run independent reader-v4 once after terminal evaluation/released ownership; write plain-English analysis. The correctly targeted prediction diagnostic remains design-only and separately outstanding. No new scientific experiment, push, deployment or change to production56708. Goal remains active; old heartbeat remains paused. Reverify actual process identity/current outputs before reporting liveness. Qualification sessions49024/66036 have both completed exit0; no observer exec session remains.


## 2026-09-30 17:40 Adelaide - prediction split building block qualified; main comparison unchanged

Previous goal turn made concrete progress: completed independent recovery authentication, qualified the versioned final consumers and committed their intended evidence locally as0d399905. This turn reverified exact trainer94544/create1790753443.077002, service-owned parent84788 and all four original worker creation times/command lines. Their current outputs remain fresh and they are advancing through cycle6 collection/archiving. Production is available, about97GBRAM is free, and no current failure is recorded. A yielding-to-heavy-GPU label can remain after the brief wait cleared; don't infer an ongoing pause from a last-emitted stage alone. No duplicate/restart/admission-policy change.

Prepared one reusable implementation for the separately outstanding prediction diagnostic: stack_context_flop_partition_v1.py and its check. Explicit configuration only, with no default scientific namespace, ratio, budget or seed. Partition the initial PUBLIC flop by full24-suit canonicalization; keep descendants on that same side; reject hidden future-flop assignment of preflop rows. Public geometry catalogue records physical suit-orbit multiplicities and each conditional split denominator, avoiding uniform canonical-group weighting. This source is NOT imported by the live study.

CPU qualification passed1.532seconds, below-normal/one worker, no native execution/fitting/CUDA/scientific draws: all22100physical flops,1755canonical groups,42120independent suit maps, six card orders per canonical representative,10530descendant checks, physical denominators and17corruption rejections. Synthetic namespace/buckets only; no actual diagnostic split admitted. Evidence prefix stack-context-flop-partition-check-v1. Documentation STACK-CONTEXT-PREDICTION-FLOP-SPLIT.md states exact scope and missing dependencies. The original design document and every registered main-study input remain unchanged.

Source inspection confirms the existing native two-stage conditional generator is river-only, requiring state.street==2 and no chance nodes; its selected-pair evaluator returns same-policy legal action values/baseline/advantages. Earlier-street common-teacher labels still need qualified hidden-card/future-board conditioning and exact all-in integration. Retained mixed-generation training-regret records cannot substitute for fixed-final-teacher advantages. The complete teacher is prospectively A-baseline played0..63, exclude64, after terminal training; its full-bank inference, preflop holdout, conditional targets, noise/statistics/fitting budgets and actual diagnostic registration remain OUTSTANDING. Do not call the diagnostic complete from this split.

Leave the existing trainer unchanged. Next scientific actions remain all64cycles/arm, actual throughput-v2 retained-hand gate, fresh evaluation-v3 4096x7, independent reader-v4 and plain-English analysis after definitive success/released ownership. No second scientific experiment, push, deployment or production56708 changes. Goal active, old heartbeat paused. These new qualification commands have completed exit0; no new observer session remains.

## 2026-09-30 18:29 Adelaide - all-street teacher-path and native payoff transport qualified

The existing four-way comparison remains live, identity-verified under the same Windows services-owned entry84788/create1790752536.9318762 and unchanged trainer94544/create1790753443.077002. All four original child creation times and parentage were verified again. Fresh parent status, no trainer failure, production available, about95.6GBRAM available. Published counts8/8/8/7 (A-baseline/A-relative/B-baseline/B-relative); workers are proceeding through cycles8-9. Registration SHA remains ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3. Do not restart/duplicate or change inputs based on an observer ending.

Prepared a second reusable building block for the outstanding prediction diagnostic: stack_context_teacher_path_v1.py. It reconstructs chronological BOTH-player public paths on all four streets, native24-suit card keys and original own-history links. Frozen teacher probabilities are inferred before interventions; all past actions and the target action are forced while future policies remain unchanged. Full deals are label-generation data, never network inputs. The existing Registry remains the feature contract.

Path checkv2 passed3.781seconds on CPU:918retained native rows,2918own-history links,1980actual native both-player river paths,2086legal interventions,298hidden-future invariance checks,24negative cases. Preserve failed checkv1/source/attempt: its fixture incorrectly required visible format2 and conditional-labelled format3 source strings to be equal. V2 only corrected their explicit separate binding/shared raw fields; implementation source stayed unchanged. No scientific cycle retry.

Native payoff checkv1 passed1.140seconds, four read-only invocations of the UNCHANGED CPU evaluator. It reused32-row batches at20bb/60bb, each repeating TWO distinct already-retained fixture deals;16targets cover both actors on all four streets. Original fixture utility replayed unchanged; teacher target mixes match legal action Q within8.89e-16. Every tested fold loses exactly invested chips; maximum forward cashflow7.11e-15 and conservation1.78e-15. Synthetic forward/reverse control separately demonstrates why target-only forcing, dividing contaminated root value by arrival, and forcing only one's own history are wrong. No fitting/new scientific deals/CUDA/production change/second scientific experiment.

Evidence: stack-context-teacher-path-check-v1/v2, stack-context-teacher-native-check-v1, stack-context-teacher-path-readback-v1-result.json. The final local receipt independently authenticated all consumed inputs and all16native replay artifacts (4,654,404bytes) plus current process identities. Explanation STACK-CONTEXT-PREDICTION-TEACHER-PATH.md records scope and outstanding dependencies. These helpers are NOT imported by the live study. Qualification teacher is an old fixture probability table, not the future64-model bank.

Still required for the separate diagnostic: original-teacher opponent posterior and legal future-board integration with blockers/draw multiplicities, noise controls, actual complete A-baseline played0..63 teacher binding (exclude64), public-flop split and separate preflop holdout, budgets/seeds/statistics and registration. Fixed-board action-value transport is not an integrated all-street learning diagnostic or an accuracy finding.

Main scientific sequence unchanged: all64cycles/arm, actual throughput-v2 retained-hand/full-bank gate after terminal success/released lock, fresh evaluation-v3 4096x7, independent reader-v4 and plain-English analysis. Broad goal remains active; no GitHub push, deployment or production56708 change. All qualification commands have finished; no new observer session or helper remains live. Original72-hour deadline and legitimate invocation-boundary behavior remain unchanged.

## 2026-09-30 19:25 Adelaide - conditional history and future-card building block qualified

The exact existing trainer94544/create1790753443.077002, service-owned parent84788 and all four original worker identities remain live. Independent readback observed published counts11/11/11/10 (A-baseline/A-relative/B-baseline/B-relative), fresh parallel-training status, unchanged registration SHA ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3 and no trainer failure. Workers are proceeding through cycles11-12. Around94GBRAM is free. No restart, duplication, input/gate change or production56708 modification.

New stack_context_teacher_conditioning_v1.py exports genuine chronological histories and visible-only policy rows for all compatible hidden hands. Its original-teacher posterior preserves the inherited PhysicalDeals entry weights/cutoff, uses opponent past-action likelihoods once, and records unsupported own-entry/history states. Unknown future cards are uniform physical draws with both private hands and public blockers removed, unordered flop/chronological turn-river. Explicit local RNG/checkpoints authenticate exact restart and replay. Every action shares the same plan; reduction retains multiplicity, takes an arithmetic mean and subtracts the original teacher baseline. No second posterior/entry/arrival weighting.

Conditioning qualificationv1 passed51.25seconds, CPU/two threads/below-normal:32combinations across20bb/60bb, four streets, both actors and362/387inputs passed the real registry/model preparation. Matching retained native policies agreed within1.1102230246251565e-16; two retained river posteriors matched exactly across1980native two-player paths. All32restart checks passed; checked17296physical preflop flops,1980flop runouts,44turn choices and completed river domain. Synthetic double-weighting control differs6.758149003749381e-6. All27corruptions rejected; globalNumPy/TorchRNG preserved. No native call, fit, scientific sample or CUDA execution in this qualification. It does not test accuracy.

Independent readbackv1 authenticated all75consumed input identities plus attempt/result/current reader source, rechecked scope/counts/controls and bound the verified live identities. Sources/results prefix stack_context_teacher_conditioning and stack-context-teacher-conditioning; explanation STACK-CONTEXT-PREDICTION-CONDITIONING.md. These helpers are NOT imported by the registered main comparison. Fixture teachers are retained two-model controls, not the prospective64-generation bank.

Still outstanding for the separate diagnostic: integrated native action-value labels on conditional plans, repeated-label noise, actual complete A-baseline played0..63 teacher inference (exclude64), public-flop split and separate preflop holdout, unsupported-state handling, declared seeds/budgets/statistics and registration. No new scientific experiment has been admitted or completed. Main scientific sequence remains all64cycles/arm, actual complete-bank throughput-v2 gate after terminal success/released lock, fresh evaluation-v3 4096x7, independent reader-v4 and plain-English analysis. Broad goal active; no push/deployment. Qualification/readback commands finished exit0; no new observer/helper remains live.
## 2026-09-30 19:49 Adelaide - conditional plans joined to native teacher action values

Previous goal turn made concrete progress: qualified the hidden-hand/future-card conditioning building block, independently authenticated all75inputs and committed it locally as a23d4f6c. Current turn implemented stack_context_teacher_native_plan_v1.py: explicit immutable teacher manifest and authenticated conditional chance plan, original-teacher history inference before intervention, full native visible-only queries, original history/target parity, consistent shared BOTH-player past forcing, unchanged future rows, original-target-mix control, complete immutable exact preflop all-in cache, native chip-ledger checks, arithmetic conditional action means and original-sigma advantages. Existing attempt folders are refused. No scientific teacher selection/admission in the adapter.

Native-plan checkv1 passed156.859seconds, boundedCPU/two threads/below-normal, with an old362-input two-generation fixture teacher (weights1,2), not the prospective64-bank teacher.16targets cover bothactors/allfourstreets/20bb and60bb; two explicit8-draw control streams each,32plans/256qualification draws/64native invocations. Maximum native original-target mixture error1.7763568394002505e-15, original history inference error1.1102230246251565e-16, fold cashflow error0. Shared profiles equal the independent union of per-deal qualified interventions and preserve future rows exactly.10corruptions/refusals passed. No fitting, CUDA or new scientific experiment.

Independent readbackv1 authenticated all77inputs and448artifacts, replayed chance plans, verified legal profile routing/native transport and independently recomputed action means/baselines/paired differences. Readback's mixture error8.881784197001252e-16 and fold error0. Original teacher inference parity is bound to the consumed qualification; this is not a second oracle evaluation. Descriptive two-stream label differences reach0.240469starting-stack units with only8draws. This flags target noise for the future diagnostic; it is neither a scientific noise-budget qualification nor a representation accuracy score.

Preserved all62,163,063original native artifact bytes locally. A7,386,683byte ZIP was independently member-SHA verified across all448files, with source bytes verified unchanged afterward. Archive/member receipt retained; no original evidence deleted. Compact ZIP and intended receipts/sources will be committed locally. Sources/evidence prefix stack_context_teacher_native_plan and stack-context-teacher-native-plan; explanation STACK-CONTEXT-PREDICTION-NATIVE-PLANS.md. No main-study source/import/input/gate change, push or deployment.

Main trainer94544/create1790753443.077002 remains identity-verified live under the same service-owned84788entry; independent readback verified allfour original child creation times/parentage. Final19:49check: fresh parallel-training status, no failure, published counts13/12/12/12 (A-baseline/A-relative/B-baseline/B-relative). New qualification session96074 and readback44139 both finishedexit0; no new observer/native helper remains live. Existing four-way comparison continues unchanged.

Still required: finish64cycles/arm; actual complete-bank throughput-v2 gate after terminal success/released lock; fresh evaluation-v3 4096x7; independent reader-v4; plain-English analysis. Separate prediction diagnostic still needs the actual prospectively fixed A-baseline played0..63 teacher binding/inference/resources, noise-aware scoring, actual public-flop split/preflop holdout, unsupported-state rules, data/fit/noise budgets/seeds/selection/statistics and registration. Broad goal remains active. These restricted fixture checks are not equilibrium/GTO Wizard/multiway accuracy or production readiness.
## 2026-09-30 20:11 Adelaide - noise-aware prediction/decision scoring qualified

Previous goal turn made concrete progress: qualified the conditional native action-value adapter across allfourstreets/bothactors/20bb/60bb, authenticated448artifacts and committed compact evidence locally as8961f7ad. Current turn prepared stack_context_prediction_noise_scores_v1.py for the separately outstanding prediction diagnostic. Two independent equal-budget common-teacher label means give legal-action observed squared error, half their squared difference as label noise, and cross residual as noise-corrected error. The latter can be negative and is not clamped. Shared-label paired predictor error differences cancel the common noise term. Decision payoff uses policies chosen from frozen clipped legal predictions, uniform exact ties, never the evaluation labels.

The scorer derives normalized label/prediction bounds from original native stack/dead-money ledger, explicitly records clipping and ignores illegal output slots in values/denominators. ClusterEvaluation takes one prospectively weighted convex descendant block per independent parent sample; every parent counts once, regardless of descendant count. It refuses duplicate/overlapping clusters, undeclared strata/looks, exhausted budgets and invalid metrics. Existing bounded paired interval math is reused unchanged with a declared family of7metrics times allstrata/looks. IID parent sampling, frozen predictions, independent labels, row weights and full source provenance remain caller requirements, not facts inferred from unique IDs. Canonical-flop splitting/preflop holdout are separate.

CPU qualificationv1 passed0.046seconds with no native invocation, fitting, CUDA or new scientific sample. Exhaustive16finite independent-noise pairs reproduced known true errors0.62/0.005, label variance0.02285 and paired synthetic decision gain0.5. These are synthetic controls, not learned-model results. Negative corrected score preserved; illegal padding ignored; clipping checked;108endpoint-bound controls; merged/sequential means and variances equal. Four parent clusters with138dependent rows retained a count of4 and equal-parent weighting, rather than pooled-row weighting.19corruption/refusal cases passed.16already-retained native label pairs were checked only for metric arithmetic using synthetic predictions; no native-fixture confidence or accuracy claim.

Independent readbackv1 authenticated all9consumed source/evidence identities, independently recomputed closed-form toy expectations and all7source-cluster interval means/variances/radii/family allocation. Sources/evidence prefixes stack_context_prediction_noise_scores and stack-context-prediction-noise-scores; explanation STACK-CONTEXT-PREDICTION-NOISE-SCORING.md. Current registered inputs/imports/models/gates and production56708 remain unchanged. No scientific diagnostic was admitted or completed.

The exact94544/create1790753443.077002 trainer, service-owned84788entry and allfour original worker creation times/parentage remain independently verified live.20:11fresh parent status is parallel-training with no failure; published counts14/13/13/13 (A-baseline/A-relative/B-baseline/B-relative). All new check/readback commands finishedexit0 immediately; no new observer/helper remains live. Existing four-way training continues. No push/deployment.

Still required: all64cycles/arm, actual complete-bank throughput-v2 gate after terminal success/released ownership, fresh evaluation-v3 4096x7, independent reader-v4 and plain-English analysis. Separate prediction diagnostic still requires actual fixed A-baseline played0..63 teacher binding/inference/resources, actual canonical-flop/preflop split and source sampling, unsupported-state handling, registered data/fit/noise budgets/seeds/initialization/selection, scoring-rule adoption and statistics. Scoring plumbing does not demonstrate better preflop ranges or satisfy broad goal completion. Goal remains active.