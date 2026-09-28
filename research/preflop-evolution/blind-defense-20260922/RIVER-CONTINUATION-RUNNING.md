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
