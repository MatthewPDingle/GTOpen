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
