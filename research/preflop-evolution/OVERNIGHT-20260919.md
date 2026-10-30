# Overnight preflop accuracy research, 19–20 September 2026

The user authorized autonomous research until returning tomorrow morning.
Do not redeem reset credits or purchase usage. A one-time thread heartbeat
`resume-overnight-preflop-research` is scheduled for 00:15 Adelaide time,
after the reported 00:09 normal reset. Do not launch duplicate work if the
goal or a research process is already running. Codex and this computer must
remain available for the local follow-up to run.

## Current evidence

Read `integrated-coverage-20260919/RESULTS.md` and `SCALING.md` first.
All six prescribed connected-game development runs finished 2,000 iterations.
Numerical accounting passes; small board samples severely distort ranges.
AA call changes from 52.7% to 4.0% when the same two ranks and bet sizes gain
all suit relabelings. This is sample sensitivity, not a recommended AA range.
The ten-board panel gives 77 zero set flops and 99 about 43%, versus roughly
12% full-deck opportunities. More iterations cannot fix missing boards.

## Next priorities

1. Completed coverage study reviewed and pushed as `b69ea07c`.
2. Validate lossless future-card symmetry compression for changing external
   ranges. Check both ranges and lock symmetry; reject unsupported inputs.
   Compare CPU/GPU counterfactual values and accumulated strategies against
   uncompressed games before admitting larger experiments.
3. Investigate memory-bounded groups of board states without restarting their
   regrets or averaging independently solved preflop policies. Match the
   resident game's trajectory first. Measure RAM and transfer costs.
4. Preregister a more representative board set and stability tests before
   solving it. The existing 47-flop subset is a feasibility candidate, not an
   accuracy certificate. Preserve separately reserved validation cases.
5. Keep folded-card uncertainty integration separate and explicit. Never leak
   hidden folded cards to a postflop strategy or replace the joint posterior
   by unrelated marginal corrections.

## Operational constraints

- Repository: `T:\Dev\GTOpen`, research branch `codex/continuation-symmetry-research`. Explicitly stage owned files;
  many unrelated research logs and artifacts are untracked.
- Preserve production `http://localhost:56708`, all sessions and saves.
  Check `/api/preflop/status`, `/api/status`, `/api/reports/status` before GPU
  research and while it runs. Stop only owned research children if needed.
- One GPU job at a time. Preserve the production app's resident memory.
- Save input/source/binary hashes before each substantive experiment. Do not
  overwrite historical freezes after rebuilding.
- No production deployment merely because a research comparison passes.
- Research remains CPU/GPU correctness focused; CPU optimization is not a goal.
- Use `C:\Program Files\Python312\python.exe`. CUDA NVRTC DLL path is
  `.cuda-nvrtc/nvidia/cuda_nvrtc/bin`. Limit research CPU threads appropriately.
- Push with Windows OpenSSH:
  `git -c core.sshCommand=C:/Windows/System32/OpenSSH/ssh.exe push origin codex/continuation-symmetry-research`.

Update this handoff after each validated step. Keep routine unchanged status
quiet; report meaningful findings, failures or a need for user input.

## 16:45 progress checkpoint

The completed coverage study was committed and pushed as `b69ea07c`.
New research-only work in `symmetric-bridge-20260919` is NOT validated yet:
`gpu::SymmetricContinuationGpu`, test `continuation_symmetry`, and guarded
runner `tools/research/symmetric_bridge_validation.py`.

The input guards passed. Two-tone compact device arenas fell from 38.29 to
22.83 MB. But independent 100-iteration trajectories failed the strict value
gate; monotone fixtures also failed the same-state one-step gate. Rainbow
GPU results were identical. See `initial.log`, `diagnostics.log`, and freezes.
Do not relax thresholds or deploy the wrapper. Investigate internal policy
symmetry: root inputs are checked, but float arithmetic can break symmetries
inside the postflop strategies that the orbit plan assumes. This is a
hypothesis to test, not an established cause. Existing fixed-range GPU
isomorphism code has not been changed.

Next diagnostic adds root-average suit-asymmetry reporting. Build with
`cargo test --release -p solver --features preflop-research --test continuation_symmetry --no-run`.
Use the runner with the returned test executable, a fresh registration label,
`--nocapture --test-threads=1`. Preserve failed logs and hashes.
The research GPU runner leaves no process after completion/failure.

Current research branch: `codex/continuation-symmetry-research`. The new
wrapper and diagnostic tests are an explicitly failing research candidate,
not a change to deploy or merge yet. The policy audit confirmed internal
strategies can lose stabilizer symmetry. Next investigate exact orbit tying
of regret/average storage; see `symmetric-bridge-20260919/DIAGNOSTICS.md`.
Retain a fully enumerated reference with the same projection, so changes in
strategy constraints are not confused with chance-compression correctness.

Live hardware check found 128 GB system RAM (~96 GB free), so the older
64 GB AGENTS hardware note is stale. Board-state staging may be more feasible
than previously estimated. Verify again before allocating large experiments.

## 17:17 checkpoint: validation queue running

Exact stabilizer projection now removes internal suit-policy drift. An
independent CPU test reproduced both hand averaging and public-runout
transport with zero storage error on turn and flop fixtures. Same-state
CPU/GPU and same-policy full/compact evaluations pass their thresholds.
The rapid-changing-range 100-iteration independent-trajectory value gate
STILL FAILS: about 0.02234 bb two-tone and 0.01656 bb monotone. Retain this
failure; do not merge/deploy the candidate as fully validated.

New fixed-range 2,000-iteration diagnostics pass: aggregate full/compact
EV differences 0.00004234 bb two-tone and 0.00001249 bb monotone. Both games
converge below their registered thresholds. The two-board connected game
also passes: max EV difference 0.000005687 bb, common-prior root policy TV
0.000008969, all independent accounting checks pass. This is evidence about
these games, not full-poker accuracy. See `symmetric-bridge-20260919`.

One guarded sequential process is now running:
`tools/research/overnight_reference_queue_20260919.py`.
Read `representative-coverage-20260919/validation-queue-status.json` and
its `.lock` PID before doing anything. Do not start a second GPU job.
The queue waits for the owned AB explicit run, runs AB compact and its
review, then paging unit tests, a paged two-board 2,000-iteration comparison,
and only if all gates pass a 20-iteration 47-board feasibility trial.
The queue stops on failure; inspect its log/status rather than retry blindly.
It freezes binaries/inputs and refuses changes to queued files.

Research-only paging implementation: `gpu/continuation_paging.rs`, test
`continuation_paging`, example `integrated_continuation_paged`. It parks full
F32 regrets/averages in CPU solvers and shares mutable GPU buffers between
boards. No compression, projection or numerical change is intended. It has
compiled, but has NOT passed runtime gates yet. The two-board unit comparison
requires bitwise CFV and arena agreement across 160 board/player switches.

47-board preflight: full host action arenas 35.256 GB, unpaged GPU arenas
plus reach/CFV staging 84.215 GB; future-card compact equivalent 63.645 GB.
These omit other metadata. The machine has 128 GB RAM. The paging runner
records resources and stops its own child below 20 GB host/3 GB GPU free.
Use the trial to decide feasibility and duration; no long run is queued yet.
See `representative-coverage-20260919/PAGING-PROTOCOL.md`.

Next after the queue: review all gates and resource measurements, register
a bounded larger-panel solve if feasible, then run it with production guards.
Do not change the ten reserved validation boards or use their strategic
outcomes to select this candidate. Preserve 56708, currently stopped at
preflop iteration 800, postflop idle, no active reports.

## 17:31 follow-up

The explicit ten-board comparison completed 2,000 iterations with total gap
0.00409276 bb. The compact version is running under the existing queue; do
not start competing GPU work. Last verified live queue PID 70128 and compact
child PID 72304; revalidate these before relying on them. The previous turn
made progress (new code/protocols and verified running experiments).

While that runs, prepared a separate frozen-policy evaluator:
`crates/solver/examples/continuation_transfer.rs`. CLI is SUBTREE MANIFEST
OUTPUT ITERATIONS SOURCE_RESULT. It freezes all preflop arrays bitwise,
updates only postflop states, and reports both restricted postflop residual
and unrestricted full-game deviation. It independently forward-propagates
branch reaches and sums postflop deviations to check the restricted recursion.
The executable is built but runtime validation is still pending.

Read `representative-coverage-20260919/HOLDOUT-PROTOCOL.md` and
`TRANSFER-CONTROLS.md` before using it. Four synthetic `transfer-control-*`
source policies are ready. First run each on existing development
`integrated-coverage-20260919/orbit-river.json` for 100 iterations, then the
old-two-orbits policy on its own two-board panel for 2,000. Review using
`tools/research/continuation_transfer_review.py RESULT SOURCE KIND`, where
KIND is fold/call/fourbet/jam/development-two. Do not solve reserved boards
until these controls and the registered runtime/convergence preflight pass.
Update the guarded runner's provenance list to include the transfer example,
reviewer and protocols before launching transfer controls, but NEVER edit
the runner while the existing validation queue has its inputs frozen.

Also built existing continuation regression tests for later sequential use:
`target/release/deps/continuation_bridge-574508f4b43b5330.exe` and
`continuation_bridge_accumulation-3de5c61f157d7d0b.exe`.

If the ten-board symmetry gate fails, preserve that result. Paging uses the
original fully enumerated unprojected path and can still be tested on its
own merits after the stopped queue is inspected. A symmetry failure need
not block lossless host paging or the broader reference study.

## 17:35 validation results

The ten-board full/compact comparison PASSED all registered gates and
independent accounting. Max EV difference 0.000012931 bb; common-prior root
policy TV 0.0000190505; total gaps 0.00409276 and 0.00417737 bb. See
`symmetric-bridge-20260919/connected-ab-review.json`. This does not erase
the earlier abrupt-changing-range stress failure or authorize deployment.

Paging unit test PASSED bit for bit: 160 alternating board/player sweeps,
including changing and zero own reaches, matched resident GPU CFVs and all
regret/average arenas. Shared workspace 127,093,360 bytes; 11.446 GB transfer
payload in the test. Runtime 5.78 seconds (includes the resident controls).

The validation queue is now running `paged-two` through 2,000 iterations.
Verified live child PID 71316, shared workspace 1,421,651,592 bytes; iteration
100 at 67.7 seconds. The queue will independently review it, then attempt
the 47-board 20-iteration trial only if it passes. Session handle 35647 is
the queue. Continue waiting on that same handle/process, not a duplicate.
All builds are complete; no compile is currently pending.

## 17:55 independent validation and streamed-evaluation preparation

The original ten reserved boards have no ace or nine, making them useful
stress cases but weak broad validation. Before accessing any reserved
strategic outcomes, froze a second, independent 95-board sample. It uses
one preregistered probability-proportional-to-orbit-size systematic draw,
excluding report47, old-two, A/B and all original reserved suit orbits.
See VALIDATION95-PROTOCOL.md, validation-95-freeze.json and structure audit.
The maximum pocket-pair opportunity error is 2.40 percentage points against
the eligible complement, versus 14.27 points for the old holdout against
the full population. This is chance coverage only, not strategic validation.
The excluded population is 4.525% of physical flops; do not call the new
sample an unbiased full-deck estimate or assign naive iid error bars.

Prepared a faster frozen-policy evaluation route: solve each flop's two
continuations resident on GPU, then combine terminal CFV vectors BEFORE
preflop maximization. This is valid only with EVERY preflop policy frozen;
it must never replace the coupled learning schedule. New example
continuation_transfer_streamed builds successfully. Aggregation script is
continuation_transfer_aggregate.py. Neither has passed runtime controls yet.
Read STREAMED-TRANSFER-PROTOCOL.md, run the deterministic river controls,
then compare two streamed boards against the paged frozen-policy evaluator
at 2,000 iterations. All heldout use remains gated on these controls.
Do not overwrite existing original/full/paged binaries during the queue.

The validation queue (session 35647) remains live on paged-two, then runs
only a 20-iteration report47 feasibility trial. Do not launch another GPU
process until it finishes. Compile-only work is safe. The new streamed
binary build session 62326 has completed successfully.

## 18:06 queued overnight reference and transfer plan

The paged two-board run PASSED: every checkpoint evaluation exactly equals
its original resident reference (max EV and root policy difference zero).
It took 1,199.1 seconds and transferred 9.013 TB through a 1.422 GB workspace.
The report47 20-iteration trial also passed independent accounting and
resource gates. Its slope estimates a 2,000-iteration run at 9.32 hours;
minimum free RAM/VRAM were 64.90/17.47 GB. See report47-trial-review.json.

The initial transfer control stopped on a Python reporting assumption:
synthetic policies have no `hands` display summary. Both actual solver
controls had passed. The aggregator now derives labels from class indices;
no numerical logic/tolerance changed. Failed attempt and source preserved;
see TRANSFER-CONTROL-RETRY.md. V2 reruns all controls under new names.
The active control queue is session 85000. It now proceeds to the two-board
frozen-policy 2,000-iteration comparison; expect about 20 minutes paged plus
roughly two minutes resident. Do not start another GPU job.

OVERNIGHT-RUN-PROTOCOL.md preregisters the next sequence: after all controls
pass, full report47 at 2,000 iterations (11-hour owned-child deadline), then
unchanged AB and report47 source policies on BOTH original reserved10 and
independent validation95, 2,000 postflop iterations per board. Use resident
streamed workers only after parity passes. Convergence gate is <0.01 bb for
reference/full gap and heldout/restricted postflop gap; report transfer
vulnerability separately. Stop starting work at 09:00 Adelaide tomorrow.
No arbitrary early-source substitution, no tuning to heldout outcomes.

The new outer runner is tools/research/overnight_accuracy_queue_20260919.py.
It waits for the existing controls, freezes inputs, checks gates and serializes
all GPU work. Check overnight-accuracy-status.json and its lock/process before
starting or resuming anything. It preserves production and stops owned
research if production becomes active. Existing validation queue session
35647 completed normally; do not resume it or rerun its completed trials.

## 18:06 live queue handles

All eight deterministic river solver controls (paged and streamed, each
fold/call/fourbet/jam) and the four single-board aggregation checks passed.
The v2 controls are now in the 2,000-iteration paged two-board comparison:
owned child PID 33992, session 85000. No reserved strategic result yet.

The registered outer overnight queue is live: session 3756, PID 72076,
currently waiting for those controls. It owns overnight-accuracy.lock and
has written overnight-accuracy-freeze.json. Do not launch a duplicate or
edit its frozen inputs. It will proceed automatically only if every control
passes. If it stops, inspect its status and existing outputs before retrying.

## 18:15 comparison reporting prepared

The transfer controls continue live (paged two-board child 33992); checkpoint
500 has restricted postflop residual 0.01313 bb and full deviation 0.02021 bb.
Target remains 2,000; no threshold or input has changed. Outer queue 72076
still waits on the same existing control process.

Added a chance-coverage graph to RESULTS.md. It shows why the original ten
training/reserved flops are weak samples and compares the unchanged report47
and independent95 with exact population opportunity rates. These are chance
statistics, not solved-strategy validation outcomes.

Prepared tools/research/reference_policy_compare.py for the eventual AB vs
report47 root comparison under one exact compatible two-player entry prior.
It reproduces the earlier A/B policy-TV and standardized frequencies exactly
(38.7527653% TV), with independent accounting audits. The development check
is development-comparison-check.{json,md,png}; do not confuse it with a new
report47 result. After full reference completes, invoke the script with
panel-ab-result.json, report47-full-result.json, an unused output prefix,
and labels '10 flops' '47 flops'. It compares policy sensitivity, not truth.
The running queue and its frozen code/input files remain unchanged.

## 18:20 hidden-chance boundary control

Added a CPU-only synthetic utility test for the unchanged transfer aggregator.
It reuses validated physical-card reaches but replaces continuation payoffs
with two opposite artificial outcomes. Correct preflop deviation gain is
exactly 0 bb; maximizing after revealing the outcome would incorrectly award
1 bb. The existing aggregator returns 0, and independent pair/cashflow checks
pass. This validates aggregation-before-maximization, not any new poker data.
See transfer-information-control.json and tools/research/transfer_information_control.py.
No frozen queue input or solver executable changed. The owned control child
continues; final 2,000-iteration comparison remains pending.

## 18:32 transfer import failure diagnosed and corrected

IMPORTANT: earlier sessions 85000 and 3756 are TERMINAL, not still waiting.
The paged two-board transfer reached 2,000 and passed physical/chip accounting
with postflop residual 0.00135869 bb, but exact source identity FAILED.
820 probabilities changed by 1-2 ULP on decimal JSON import (max 1.11e-16).
Internal arrays stayed unchanged during learning. Both controls and outer
queue stopped on the gate; no full47 or reserved strategy run has started.
See transfer-v2-import-diagnostic.json and TRANSFER-CONTROL-RETRY.md.

A focused Rust regression reproduces the import error and now passes with
serde_json/float_roundtrip. Added a dedicated continuation-transfer-research
feature, used only by continuation_transfer and continuation_transfer_streamed.
Build those with:
cargo build --release -p solver --features continuation-transfer-research --example continuation_transfer --example continuation_transfer_streamed
Both new binaries are built. The original integrated_continuation_paged.exe
hash is VERIFIED UNCHANGED; its existing reference evidence remains valid.
The default application/research feature sets and production app are untouched.

Attempt 3 uses transfer-v3-* outputs and first runs two short full-policy
import checks against the actual mixed development policy, then reruns all
controls and the two-board comparison without changing any thresholds.
New registration is transfer-controls-v3-freeze.json. The outer queue was
revised to use overnight-accuracy-v2-freeze.json and record the dedicated
build feature/test; it must be launched once after confirming controls are
live. Former terminal statuses are retained as transfer-controls-v2-status
and overnight-accuracy-v1-status. No stale locks remain from those queues.

## 18:37 corrected runtime controls and faster controller

Attempt 3 is live as session 51620. Both new short mixed-policy import
controls PASSED exact external probability identity for the actual saved
policy. The deterministic controls are proceeding; two-board 2,000 remains
the required final gate. Do not restart or duplicate this queue.

Measured the controller's three production probes: localhost took 6.18 s
versus 0.031 s through 127.0.0.1, with identical idle results. The dedicated
loopback_research_validation.py wrapper preserves all three checks and
fail-closed behavior; five refusal cases, one idle case, and timeout behavior
were checked. It changes no system network or server settings. Only the
new outer overnight sequence uses this wrapper; current v3 controls retain
their frozen guard. This reduces per-worker scheduling overhead, not solver
mathematics or iteration counts. Both wrapper and base are in the new
parent freeze. The eventual full47 source and reserved targets are unchanged.

Launch tools/research/overnight_accuracy_queue_20260919.py once after the
current control process is confirmed live. It uses a NEW registration file
(overnight-accuracy-v2-freeze.json); old parent outputs remain preserved.

## 18:36 current authoritative handles

Corrected v3 controls: session 51620, parent PID 71152, active paged two-board
child PID 41320. Iteration 100 completed; both actual mixed-policy import
checks and all eight deterministic river controls passed. The strict
2,000-iteration source-identity/parity gate remains pending.

Corrected outer overnight queue: session 66965, PID 69280. It is live and
waiting on the same v3 controls, with overnight-accuracy-v2-freeze.json.
Do not duplicate either job or alter their frozen inputs. Old sessions
85000 and 3756 are closed/failed; do not wait on them or treat their statuses
as current. The original paged reference executable hash remains unchanged.

## 18:49 entering-decision diagnostics prepared

Current turn made progress without changing any frozen queue input. Added
transfer_decision_diagnostics.py and DECISION-DIAGNOSTICS.md for the eventual
complete held-out panels. It reports hand-level call-versus-fold value,
class action margins, and value lost by the entering decision alone. Later
own actions stay fixed; hidden chance is averaged before optimization.
Physical-combination gains are retained before class averaging.

CPU controls passed all four existing deterministic river fixtures and
synthetic checks for preserving later own actions and hidden information.
Evidence: transfer-decision-controls.json. These are diagnostic controls,
not additional poker accuracy outcomes. Do not interpret their deliberately
bad deterministic policies as realistic ranges. Once a reserved source/panel
pair completes, run the new script with its full per-board worker list and
an unused output prefix; the complete panel is audited before reporting.

V3 long control remains live under PID 41320 and session 51620; outer queue
69280/session 66965 waits. No restart, source change, or production write.

## 18:59 transfer gate PASSED; full reference running

V3 control session 51620 completed successfully. All short controls, exact
source-policy checks, and the two-board 2,000-iteration comparison PASSED.
Streamed vs paged maximum differences: EV 2.665e-15 bb; full gaps 1.777e-15;
postflop gaps 1.998e-15; action frequencies 4.441e-16. Postflop residual is
0.0013586882 bb and full deviation 0.0026439076 bb. Both use the exact same
source policy. The streamed worker solve times total 98.435 s versus paged
1247.483 s; this speed benefit is for frozen-policy evaluation ONLY, not
joint preflop learning. All v3 artifacts are final and can be committed.

Outer queue session 66965 / PID 69280 automatically advanced at 18:57:29
Adelaide. Full47 child PID 34036, guard parent 45452, target exactly 2,000.
The original paged executable and registered source/panel remain unchanged.
At 84 seconds the child was live with roughly 64.8 GB host and 17.9 GB GPU
free. Status is report47-reference-2000; do not launch a duplicate. This is
the first full47 reference run, not a retry of an earlier completed solve.
The same outer queue will audit it and, if it passes, run the reserved10
and validation95 evaluations. Deadline and fail-closed safeguards unchanged.

Prepared hand-level diagnostic also ran successfully on the completed
TWO-BOARD DEVELOPMENT transfer: development-two-decision-diagnostics.json/md.
Root-only gain 0.0007763375 bb, below full OOP deviation 0.0015460624 bb.
This is an additional development sanity check, NOT reserved evaluation.
No independent held-out strategic outcome is available yet.

First full47 checkpoint is now present: iteration 1 at 86.7 seconds,
gap 73.805552 bb (initial learning state, not convergence). Independent
physical-pair audit of that snapshot PASSED: normalizer relative error
2.2595e-9, maximum terminal-probability error 1.3997e-8, cash/rake conservation
error 3.7968e-8 bb. This confirms initial accounting only. Full2000 remains
running and its final convergence gate is still pending. The generated
RESULTS.md / validation-progress.png now include the initial full-run point.

## 19:06 independent private-prior coverage audit

Added chance_prior_audit.py and PRIVATE-PRIOR-AUDIT.md without modifying any
frozen input. Exact supported physical-pair enumeration and all suit
permutations show joint private-prior TV versus full deck: old two 6.128%,
AB ten 3.957%, report47 0.541%. Independent95 versus its eligible target:
0.461%. Its eligible population differs from full deck by 0.0327% in this
private-prior metric; this DOES NOT remove its different chance population.
The sparse calculation reproduces earlier dense two/ten enumerations within
1.5e-16 and agrees with the running47 normalizer. No reserved strategic
outcomes accessed. Smaller prior distortion is not a strategy-accuracy or
postflop-opportunity certificate. Record retained as chance-private-prior-audit.json.
Full reference still runs under child34036 / queue69280, session66965.

## Richer betting-menu CPU feasibility completed

Reused the existing continuation_orbit_memory.exe (no rebuild and no CUDA
allocation) with a separate copy of report47 and a 50,75 bet/donk menu.
All94 continuations planned within the existing2M node cap, in39.375s on2
CPU threads. Frozen inputs, result and status use menu50-75-* names.
Full F32 host action arrays:97.3897GB vs35.2562GB for current50% menu.
Adding62.13GB to the present allocation would violate the20GB host reserve
before additional metadata. DO NOT launch the richer menu using the present
all-board full host arrays. See MENU-FEASIBILITY.md for exact scope/limits.
Packed future-card arena estimates are not a fix: host arrays remain full
and the compact bridge's abrupt-range stress failure remains unresolved.
Current47 run and frozen files are unchanged. This is resource planning,
not new strategic evidence or a registered follow-on solve.

## Lossless storage screen and iteration-100 checkpoint

Full47 remains active under child34036 / guard45452 / queue69280,
session66965. Iteration100: gap0.7754846501716042 at1648.5s. This is progress,
not a passed final convergence gate; target remains exactly2000.

Separate CPU-only turn-board fixtures and byte codecs completed successfully.
See representative-coverage-20260919/STORAGE-SCREEN.md and storage-screen.json /
fast-storage-screen.json. All codecs restored every bit, including special
float bit patterns. At iteration100, fast LZ4 stored86.63% of raw bytes;
byte-shuffled Zstandard1 stored69.58%. Zero omission alone was ineffective.
These small states cannot establish full-flop capacity or integrated speed.
No pager change, richer-menu launch, or production deployment was made.

New helper sources: continuation_storage_fixture.rs,
continuation_storage_screen.py, continuation_fast_storage_screen.py.
Generator binary isolated in target/storage-fixture-research. LZ4 4.4.5 and
zstandard0.25.0 installed only in target/storage-codecs. Four generated .gto
states remain local; their raw arena hashes are in the screen outputs.
Do not edit frozen generator/base-screen inputs without a new revision.
Main overnight accuracy queue and its25 frozen inputs remain unchanged.

## Full-flop storage experiment launched (separate CPU job)

Session57281, guardPID60616, owned generatorPID67220. Helper:
tools/research/continuation_flop_storage_run.py. Its separate registration is
representative-coverage-20260919/FLOP-STORAGE-PROTOCOL.md and its freeze is
flop-storage-freeze.json. Do not restart while this child/guard is alive.

Two development boards only, no held-out strategic results: largest planned
full-arena case5c2h2d atpot39.5 and high two-toneAcQd9d atpot93.5. Fixed uniform
supported ranges; snapshots1,100,1000. Two CPU threads, one-hour total cap,
20GB host reserve,50GB disk reserve, production-idle guard. No GPU allocation.
First state was written successfully:1.898GB arrays,1,283,337 nodes,
309/105 hands. Initial free host62.3GB, disk288.2GB. Main reference still live.

After all six snapshots, the guard runs the unchanged fast-codec screen
automatically and writes flop-fast-storage-screen.json. Result and errors
go to flop-storage-status.json; progress to flop-storage-generation.log and
flop-storage-resources.json. Generated large .gto files stay local. Partial
states are not a passed complete experiment. All25 main overnight input
hashes verified unchanged after this launch. No richer47-menu launch cleared.

## Full-population transfer supplement prepared; weighting controls passed

New chance-only registration FULL-POPULATION-SUPPLEMENT.md prepares, but does
not launch, a follow-up combining the original95 eligible boards with all69
excluded orbits at exact physical multiplicities. Integer weights:21100
per eligible sampled board,95*m per excluded orbit, total2099500. Geometry
audit independently verified all1755 orbit multiplicities and22100 physical
flops. Outputs: supplement-excluded-69.json, combined-population-164.json,
full-population-supplement-freeze.json. No strategic outcomes were accessed.

Independent95 remains the primary unseen-board test; combined164 includes
training boards and is a separate full-population target approximation.
No unbiased ratio/max or precise full-deck exploitability claim is allowed.
New runtime registration and fresh checks are required before any compute;
do not extend the existing09:00 deadline. Existing reserved10 workers can
eventually be reused only with identical board strings/game/source, leaving
59 additional boards per source. No new GPU workers are queued now.

CPU weighted_transfer_controls.py exercised the unchanged aggregator on
completed TWO-BOARD DEVELOPMENT data with1:3 chance weights. After legal
private-hand conditioning they are18.1525:81.8475. Scalar EV agreement1.78e-15;
naive chance-only EV averaging differs0.158871bb. Common weight scaling and
worker-order reversal produced identical results; missing/duplicate boards
rejected; independent accounting passed. See WEIGHTED-TRANSFER-CONTROLS.md.

Separate full-flop storage generator reached iteration100 on its first
board in273.2s;1.898GB arrays. Session57281 remains active, not completed.
Main GPU reference remains under session66965 / child34036 with latest
scheduled checkpoint100. Check live handles before waiting or taking action.

## Rare-branch interpretation diagnostic prepared

Added continuation_reach_diagnostics.py and ran it on completed AB10 only.
No reserved outcomes or partial47 policy were used. Independent physical
pair/orbit normalizer agrees, terminal probabilities sum to1, synthetic
zero-reach and mixed-hand controls pass. See REACH-DIAGNOSTICS.md and
development-ab-reach-diagnostics.json.

AB call branch has12.09% actual entry probability;56.69% of OOP counterfactual
hand mass has own call probability<=1e-6. Called4bet branch actual entry5.27%;
low-own-reach counterfactual shares58.48% OOP and25.92% IP. These are NOT
fractions of hands actually arriving. Exactly-zero shares are0 in the
averaged source. Small weighted postflop gap does not certify every rare
decision. Counterfactual updates may still learn them; no error or biased
range is proved by this diagnostic. Do not add arbitrary action floors.
Use alongside pending full/root-only transfer diagnostics; do not alter
the frozen comparison or numerical gates. Source47 audit waits for2000.

Usage checked read-only at19:42 Adelaide:4% remaining; normal reset still
pending. No credit redeemed. Existing00:15 thread follow-up remains the
resume mechanism if capacity interrupts. Both guarded jobs continue without
the assistant needing to sample tokens; handles remain66965 and57281.

## Automatic research report refresh active

Bounded presentation helper overnight_report_watch.py follows verified
queuePID69280 (including its creation time). WatcherPID73792, session63526.
It refreshes RESULTS.md and the two existing graphs when a reference
checkpoint or complete transfer summary changes; stage-only refreshes are
limited to once per5minutes. It exits when that exact queue process ends,
or by09:05 Adelaide. It never starts/stops solves, alters inputs/gates,
accesses production, pushes Git or opens windows. It retries incomplete
JSON read/render attempts; failures are recorded, not interpreted as failed
scientific runs. First refresh succeeded at19:48 with zero failed attempts.

Evidence: report-watch-status.json and report-watch.log (evolving local
status, not final scientific artifacts). Source is committed; generated
report updates after later checkpoints should be reviewed and pushed when
the assistant resumes. Do not duplicate the watcher while73792 is alive.

The non-frozen report generator now also displays any recorded queue stop
reason, final2000 reference gate, and per-panel entering action frequencies.
It labels the numerical comparison complete only for all four distinct
source/panel rows, passed residual gates, qualified2000 reference and the
queue's complete-awaiting-scientific-review state. Scientific review and
common-prior comparison are still separate pending steps. Current render
correctly says pending. Frozen scientific inputs remain unchanged.

## Full-flop storage test COMPLETE-PASSED

Session57281 exited0 at about20:24. Guard60616 and generator67220 / codec65100
are finished; do not wait on or restart those handles. All six registered
snapshots completed, then every codec restored all bytes exactly. Total
3072.953s (51.2minutes), generation2921.609s, codec screen151.328s.

At1000 iterations, combined2.203GB arrays: LZ4 stores85.04% of raw; shuffled
LZ4 76.82%; Zstandard1 76.94%; shuffledZstandard1 69.37%. The latter's separate
ratios70.28% largest paired board and63.73% smaller two-tone board. Its encode
8.460s + decode5.910s are concurrent single-pass measurements, not native
pager speed. Early1-iteration ratio12.48% overstated later savings. Minimum
free host62.13GB, disk283.42GB. Source and raw-arena hashes retained.

See FLOP-STORAGE-RESULTS.md, flop-fast-storage-screen.json, completed status,
logs and fixture metadata. Large .gto snapshots stay local. Do not launch
the richer47 menu: changing ranges, all-board capacity, native parity and
whole-solve time are untested; naive inline compression may be expensive.
Main47 remains live under session66965 / child34036 / queue69280. Automatic
report watcher73792 / session63526 remains separate and active.

## Additional coherent-range diagnostics compiled, NOT executed

New separate continuation_coherent_symmetry.rs and
symmetric-bridge-20260919/COHERENT-RANGE-PROTOCOL.md preserve the original
stress fixture and its failure. Original stress passes use different input
range pairs for the two player updates; the new controls use one coherent
pair, either abruptly changing or smoothly interpolated. Same-state and
independent-trajectory checks remain separate. Non-finite comparisons fail.

The release compile-only preflight passed (session93797 exited0). Build log,
executable/source hashes and explicit compiled-not-executed status are in
coherent-build.log and coherent-build-status.json. No GPU test was launched.
Future execution needs a separate bounded frozen run, verified production
idle and no active reference/transfer worker. Do not interrupt the current
queue or extend its deadline to run this diagnostic. Passing it would not
replace the original failed gate or clear compact storage for production.

At this checkpoint the main47 worker34036 and watcher73792 remain alive;
all25 frozen current-queue inputs verified unchanged. Last completed
reference checkpoint is100. Await500/2000; no held-out outcome yet.

## Per-board residual reporting prepared and controlled

Read-only transfer_board_diagnostics.py now reports local numerical residuals
and their private-card-weighted contributions for a complete audited panel.
This supplements, never changes, the registered aggregate gate. The helper
uses the complete source/manifest/worker audit before reporting. Apply it
to both sources and both reserved panels when complete; do not selectively
extend difficult boards or use incomplete panels.

Development unequal-weight controls pass: aggregate0.0013922120bb,
largestlocal0.0014201266bb. A constructed rare-board case demonstrates that
a1bb local residual at0.1% mass remains visible despite a0.001bb aggregate.
This is a synthetic control, not a measured poker anomaly. NaN/negative
residuals rejected; worker-order invariance verified. See
representative-coverage-20260919/BOARD-RESIDUAL-DIAGNOSTICS.md and
board-residual-controls.json. No reserved strategies were accessed.

## Entry-support probability audit completed

entry_support_audit.py exactly enumerates compatible physical private pairs
before/after the unchanged1e-5 cutoff. It retains322/106 combinations from
positive1326/1326 source support but removes only3.08444e-6 of full-deck
joint entering mass (0.00030844%). Report47 removes3.09254e-6 and validation95
3.09191e-6. Explicit normalized-distribution TV agrees with removed mass;
suit-invariance and monotonic sensitivity controls pass. No reserved strategy
outcomes used. See ENTRY-SUPPORT-AUDIT.md and entry-support-audit.json.

This quantifies a small pruning-induced population change for this one
input, not correctness of the original entry ranges, rare-hand play or
equilibrium strategy stability. Do not alter the current cutoff or frozen
protocol from these descriptive results. Main47 remains active at this
checkpoint, with100 as its last written iteration.

## 500-iteration reference checkpoint passed accounting

At21:07 Adelaide the main run wrote iteration500: combined full deviation
0.0526529724bb, elapsed7758.827s. It is still above the registered0.01bb
final gate and remains incomplete. Do not use500 as the frozen transfer
source. All registered independent accounting checks pass across the four
recorded checkpoints; max cash error1.9549e-7bb, terminal probability
error1.3997e-8, normalizer relative error2.2595e-9. Evidence and canonical
record hash: report47-checkpoint500-review.json. Audit session80209 exited0.

The100-to500 slope is15.2757seconds/iteration. Linear extrapolation gives
30672.4seconds total (about8h31m, roughly03:29 Adelaide finish); this is an
estimate, not a convergence forecast or guarantee. Independent transfer
still waits for a qualified2000 result. Queue66965/69280 and child34036
remain active. Watcher73792 refreshed the graph automatically with no
render failures. Both graph and report remain explicit about incomplete
numerical convergence and absent held-out strategic outcomes.

## Deferred paged-transfer optimization identified

Read-only audit matches actual500 counter52.884TB to exactly3 times the
35.256GB arena set per iteration (105.769GB/iteration). Training reads both
regret policies but only the traverser's average sums; uploading the other
player's average sums appears unnecessary on this specific wrapper path.
An UNAPPLIED patch would reduce counted arena traffic by1/6 to88.140GB/iter.
No GPU run or measured speedup, and no host-memory-capacity benefit claimed.

See PAGING-TRANSFER-AUDIT.md, paging-transfer-audit.json and
paging-own-average-candidate.patch. Application-only preflight passes;
the baseline/frozen source is untouched. Qualification requires bitwise
160-switch parity plus full2000 two-board checkpoint parity, independent
accounting and uncontended timing. Only after the current accuracy queue
releases the GPU, in a separately frozen candidate build. Do not alter the
active queue or extend its deadline for this experiment.

## Deferred candidate exact-checkpoint checker prepared

The separate tools/research/paging_candidate_review.py now enforces exact
saved scientific-content equality at every registered checkpoint, not just
final EV/policy tolerances. Only elapsed time and the predicted five-sixths
arena counter may differ. It also runs the independent accounting audit and
requires the complete 1/20/100/500/2000 sequence and final gap below0.01bb.
CPU-only fabricated-candidate controls pass and reject13 corruptions. These
are checker controls, not candidate GPU parity or timing results. See
representative-coverage-20260919/PAGING-CANDIDATE-REVIEW.md. The frozen main
queue and candidate binaries are unchanged; GPU qualification still waits.

## Isolated transfer candidate compiled, not GPU-tested

Separate worktree T:/Dev/GTOpen-paging-research, branch
codex/paging-own-average-research, based on04c36d327a0f5818c182126274f80468ecb79d98.
Candidate commit234c7d03 is pushed to that separate branch; not merged.
The candidate patch is applied ONLY there. Its original160-switch bitwise
test also asserts unchanged opponent host arrays and the exact2.5-times
arena-byte traffic formula. Compile-only cargo sessions43814 (test) and78382
(connected example) both exited0. Two build jobs, separate
target/paging-own-average-build. Candidate checkout has explicit
PAGING-CANDIDATE-STATUS.md, paging-candidate-build-status.json with hashes,
and both logs. No candidate GPU test or solve has run. Do not treat a compile
as numerical qualification. Main source/binary freeze remains unchanged. Qualification
must wait until the accuracy queue releases the GPU; no deadline extension.

## 47-flop reference completed; independent evaluation started

At02:58 Adelaide Sep20, the main reference completed2000 in28832.023s with
gap0.0074238271bb, passing the0.01 gate and all independent accounting checks.
The full file SHA is a1dbdd97d585e7603b8e117c2055c4be3b19804208b11c406e7ecf3c5c3afc22.
Its iteration500 canonical record still matches the previously reviewed hash.
The outerqueue69280/session66965 remains live and started streamed reserved10
evaluation automatically. Main child34036 and its guard45452 have completed;
do not poll those old PIDs as the current worker. Watcher73792 refreshed the
graph successfully. No frozen source or production changes.

Common-prior comparison completed:10 vs47 flop sources redistribute26.7163%
action probability. Frequencies are70.76/12.79/16.45/~0 versus
80.88/0.055/9.94/9.13 percent fold/call/4bet/jam. This is sensitivity, not
proof the47-flop policy is better. Rare-branch audit completed: actual call
branch0.055%, called4bet3.056%; inspect report47-reach-diagnostics.json.
See REPORT47-REFERENCE-REVIEW.md and ab-vs-report47-common-prior.md.

User checked in briefly at01:06 then explicitly said to carry on until morning.
Normal usage reset verified00:17 (0%used, all3resetcredits untouched).
Continue the original reserved10+validation95 queue and review complete panels
before interpretation; candidate GPU qualification still waits until GPU free.

## Original reserved10 comparison completed,95-panel evaluation running

At03:14 Adelaide Sep20, both complete reserved10 sources passed exact-policy
preservation and independent accounting. Postflop residuals: AB0.0009835581,
report470.0001405743bb, both below0.01. Full combined deviation gains are
4.4738595712 and3.6948940655bb respectively. Root-only OOP gains are
3.3857475229 and2.5213975693bb. Largest board-local residuals0.0017904576 and
0.0002825674bb; all below0.01. Small residual does not certify rare/off-path
hand values. This low-board-heavy panel is not a full-deck accuracy estimate.
See RESERVED10-TRANSFER-REVIEW.md and both sets of board/decision diagnostics.

Queue69280/session66965 automatically started held-validation95-ab-000 at
03:14:25. No95aggregate yet. Dynamic streamed-worker PIDs change each board;
query by executable/parent rather than old reference PID. Watcher73792 remains
active. Keep all original inputs and fixed2000/board protocol unchanged.
