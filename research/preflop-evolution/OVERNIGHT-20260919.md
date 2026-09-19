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
