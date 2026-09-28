# Conditional-target learning: execution handoff

At 2026-09-28 17:03 Adelaide, collection was confirmed live as Python PID
99508 and unified exec session 20848. It had completed 1,104/1,728 cases.
Re-poll that handle or inspect the real process before deciding it stopped.
Do not restart merely because an observation timeout expires.

The serial continuation is also LIVE: Python PID 99264, unified exec session
23365, running board_river_target_pipeline_v1.py --collector-pid 99508.
It verifies the collector process identity and terminal success, then runs
readback, fit controls, all 36 fits, held-out evaluation, and report readback.
DO NOT launch any of those stages separately while this pipeline is live.
Its status is board-river-target-learning-v1-pipeline-status.json; a state file
alone is not proof of liveness. Poll session 23365. Stage logs are retained in
S:/GTOpen-research/board-river-target-learning-v1/pipeline/.

The preceding goal turn completed and independently checked the 80-state
conditional river diagnostic (commit 78591abf). The current turn selected 96
fresh physical deals and 1,728 states, registered the target-learning plan,
passed sampling/storage controls, and started collection. Subsequent work
implemented the held-out evaluator and passed its numerical controls while
collection continued. The latest turn prepared an independent report readback
and plot, and launched the serial continuation to eliminate idle gaps between
stages. No fits or final held-out scoring had run at this snapshot.

## Frozen current experiment

- Plan: BOARD-RIVER-TARGET-LEARNING-PLAN.md.
- Prefix: board-river-target-learning-v1.
- Store: S:/GTOpen-research/board-river-target-learning-v1.
- Training: 64 deals / 1,152 cases. Evaluation: 32 deals / 576 cases.
- Both frozen original 78-model banks; exact, sample-one and sample-16 targets.
- The selection and collection sources are frozen after execution. Do not edit
  them to repair a result. Preserve failure evidence and version code if needed.
- Sampling expectation/variance and archive corruption/recovery controls passed.
- Evaluation controls passed: hand-calculated metrics, independent NumPy/Torch
  CPU inference, and batch/row inference on 97 real visible inputs. Maximum
  discrepancy was 7.11e-15 bb. No GPU or final evaluation data was used.
  board_river_target_evaluate_v1.py is now executed and frozen by its control
  artifact's source hash; corrections require a new version.
- First-eight resource admission passed: conservative projection 1.33 GB and
  4,433 seconds, including startup. Cap: 2 GB new files / two hours per collection
  invocation / 800 GB global allocation. Actual pace is faster than that bound.
- Four native exports and two archive writers can overlap GPU evaluation.
  Keep one GPU research owner. Light desktop/video sharing is authorized;
  active solves and heavier workloads take priority.

## Next steps

1. Poll pipeline session 23365 and collection session 20848. Current status is in
   board-river-target-learning-v1-status.json. Verify terminal success and the
   pipeline stage result. The remaining numbered steps are what the live
   pipeline is queued to do, not instructions to launch duplicate work.
2. Run tools/research/board_river_target_readback_v1.py. It is syntax-checked
   but has not run yet. It independently reconstructs entry/history weights,
   conditional expectations/variances and seeded draws, and writes
   verified-dataset.npz. Its readback does not score a fitted held-out model.
3. Run tools/research/board_river_target_fit_v1.py --mode control. That source
   passed syntax/import/CLI checks only; CPU/GPU numerical controls are pending.
4. If controls pass, run the same script with --mode fit. It freezes all 36
   paired models at exactly 512 steps without scoring evaluation deals. An
   explicit --resume verifies completed model artifacts if interrupted.
5. After all 36 models are frozen, run
   tools/research/board_river_target_evaluate_v1.py --mode evaluate. Its control
   already passed; do not rerun --mode control. It reconstructs each prediction
   in independent NumPy/Torch CPU paths and every metric with scalar formulas.
   All repetitions and initialization-support breakdowns are retained.
   No tuning on evaluation results.
6. Report the feasibility result. An improved local target learner is not yet
   a valid CFR integration, whole-game improvement, or production candidate.
   board_river_target_report_v1.py independently reconstructs the two primary
   metrics from all 36 retained prediction files and checks the advancement
   decision. It writes BOARD-RIVER-TARGET-LEARNING-FINDINGS.md and the plot.
   Inspect the actual results and render the plot before drawing conclusions.

Use C:/Program Files/Python312/python.exe -B, workdir T:/Dev/GTOpen, and approved
background execution. All five stage sources are frozen by the pipeline
registration even if not executed yet. Do not modify registered source bytes.
Preserve failures and version corrections. Preserve the fixed data and plan.
Shared research locks are intentionally held by the running collector; do not
remove them while it is live. The waiting pipeline does not hold another lock.

No production server changes or deployments were made. The broader goal remains
active. No new GitHub push was made in this turn.
