# Conditional-target learning: execution handoff

At 2026-09-28 17:27 Adelaide, BOTH experiments below had completed successfully
as execution jobs. Their scientific findings do not qualify a production model.
Unified exec sessions 20848 (collector), 23365 (serial pipeline), and 67158
(training-only coverage curve) all returned terminal exit code 0. Do not poll
or restart those jobs as though they are still running. No new study job has
been launched at this snapshot. The broader goal remains active.

## Completed fresh-deal target-learning probe

- Plan: BOARD-RIVER-TARGET-LEARNING-PLAN.md.
- Prefix: board-river-target-learning-v1.
- Store: S:/GTOpen-research/board-river-target-learning-v1.
- 96 new physical deals: 64 / 1,152 training cases, 32 / 576 final cases.
- All 1,728 cases collected in 2,411.7 seconds, retaining 514.1 MB at collection.
- Independent eight-worker CPU readback checked 5,686,889 observations in
  22 seconds; maximum arithmetic discrepancy 5.09e-11. All cases supported.
- CPU/GPU contrast-training control passed. All 36 matched fits completed;
  fitting itself took 53.3 seconds. Final scoring took 6.25 seconds.
- Every saved prediction and both primary metrics passed independent readback.
- Final aggregate exact / sample16 / sample1 MSE: 4088.710 / 4239.416 / 6610.802.
- Corresponding local decision costs: 13.114 / 13.703 / 18.166 bb per selected
  decision, NOT per dealt hand. Exact training MSE was only 3.312.
- The fixed advancement gate FAILED: bank A decision cost was 13.277 for exact
  versus 13.117 for sample16. Do not revise the gate or claim qualification.
- Full findings and inspected plot: BOARD-RIVER-TARGET-LEARNING-FINDINGS.md
  and board-river-target-learning-v1.png.

## Completed training-only coverage curve

- Plan: BOARD-RIVER-GENERALIZATION-CURVE-PLAN.md.
- Prefix: board-river-generalization-curve-v1.
- Artifacts: original store / generalization-curve-v1 (4.64 MB added).
- ONLY the original 64 training deals were reused. Hash-defined 48 fit / 16
  development deals; the original 32 final deals were not scored again.
- Nested fit sets: 8, 16, 32, 48 deals. Same network / targets / 512 steps.
- All 48 fits completed in 63.92 seconds. Saved-weight readback passed, max
  prediction difference 1.71e-13 bb and metric difference 1.82e-12.
- Development MSE: 5613.440, 4917.872, 4753.082, 4198.306.
- Development local costs: 20.339, 16.078, 15.520, 13.603.
- The large training/development gap remains. Bank/actor trends are not all
  monotone. This exploratory curve does not reverse the original failed gate.
- Full findings and inspected plot: BOARD-RIVER-GENERALIZATION-CURVE-FINDINGS.md
  and board-river-generalization-curve-v1.png.

## Next action

Read BOARD-RIVER-TARGET-LEARNING-DECISION.md. Pursue a bounded, newly registered
comparison of more diverse deals at the same total training-row budget. Reuse
eligible existing TRAINING labels where possible, reserve new final deals,
and freeze sampling/model/evaluation settings before new labels or fitting.
Do not tune on the spent 32-deal final evaluation or launch whole-game self-play
training from these local regressors. The next comparison is not yet designed
in executable detail or launched; do that work next rather than repeat results.

BOARD-RIVER-TARGET-INTEGRATION-NOTES.md records requirements from the actual
walker and primary CFR papers. It is not an executed estimator or an approval
to bypass the failed integration gate.

## Execution constraints

Use C:/Program Files/Python312/python.exe -B with workdir T:/Dev/GTOpen. Keep
registered source bytes immutable; version any correction and preserve failure
evidence. One GPU research owner. Light desktop/video sharing is authorized;
production solves and heavier work retain priority. Existing CUDA cap is 4 GB
with 2 GB external headroom; global archive ceiling is 800 GB. This study used
well below its 2 GB added-storage cap. Preserve historical archives.

No production deployment or new GitHub push was made. The broader goal remains
accurate and flexible preflop play across positions, stacks and trees.
