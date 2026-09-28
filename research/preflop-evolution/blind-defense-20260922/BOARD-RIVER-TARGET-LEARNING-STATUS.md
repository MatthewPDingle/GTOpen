# Conditional-target learning: execution handoff

At 2026-09-28 16:44 Adelaide, collection was confirmed live as Python PID
99508 and unified exec session 20848. It had completed 152/1,728 cases.
Re-poll that handle or inspect the real process before deciding it stopped.
Do not restart merely because an observation timeout expires.

The preceding goal turn completed and independently checked the 80-state
conditional river diagnostic (commit 78591abf). The current turn selected 96
fresh physical deals and 1,728 states, registered the target-learning plan,
passed sampling/storage controls, and started collection. This is progress.

## Frozen current experiment

- Plan: BOARD-RIVER-TARGET-LEARNING-PLAN.md.
- Prefix: board-river-target-learning-v1.
- Store: S:/GTOpen-research/board-river-target-learning-v1.
- Training: 64 deals / 1,152 cases. Evaluation: 32 deals / 576 cases.
- Both frozen original 78-model banks; exact, sample-one and sample-16 targets.
- The selection and collection sources are frozen after execution. Do not edit
  them to repair a result. Preserve failure evidence and version code if needed.
- Sampling expectation/variance and archive corruption/recovery controls passed.
- First-eight resource admission passed: conservative projection 1.33 GB and
  4,433 seconds, including startup. Cap: 2 GB new files / two hours per collection
  invocation / 800 GB global allocation. Actual pace is faster than that bound.
- Four native exports and two archive writers can overlap GPU evaluation.
  Keep one GPU research owner. Light desktop/video sharing is authorized;
  active solves and heavier workloads take priority.

## Next steps

1. Poll collection session 20848. Current status is in
   board-river-target-learning-v1-status.json. Verify terminal success and the
   collection result before launching readback or another GPU consumer.
2. Run tools/research/board_river_target_readback_v1.py. It is syntax-checked
   but has not run yet. It independently reconstructs entry/history weights,
   conditional expectations/variances and seeded draws, and writes
   verified-dataset.npz. Its readback does not score a fitted held-out model.
3. Run tools/research/board_river_target_fit_v1.py --mode control. That source
   passed syntax/import/CLI checks only; CPU/GPU numerical controls are pending.
4. If controls pass, run the same script with --mode fit. It freezes all 36
   paired models at exactly 512 steps without scoring evaluation deals. An
   explicit --resume verifies completed model artifacts if interrupted.
5. Implement the separate final evaluation and independent metric readback.
   Follow the already registered metrics/gate, including all repetitions and
   the initialization-support breakdown. No tuning on evaluation results.
6. Report the feasibility result. An improved local target learner is not yet
   a valid CFR integration, whole-game improvement, or production candidate.

Use C:/Program Files/Python312/python.exe -B, workdir T:/Dev/GTOpen, and approved
background execution. Sources for readback and fitting are prepared but not
qualified yet; they may be corrected before their first execution. Preserve
the fixed data and plan. Shared research locks are intentionally held by the
running collector; do not remove them while it is live.

No production server changes or deployments were made. The broader goal remains
active. No new GitHub push was made in this turn.
