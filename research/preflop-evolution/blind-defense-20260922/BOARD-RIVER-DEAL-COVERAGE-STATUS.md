# Equal-budget coverage: live execution handoff

Snapshot: 2026-09-28 17:50 Adelaide. Broader research goal remains active.

## Live processes - do not duplicate

- Collection: unified exec session **32008**, Python PID **98124**.
  Command: `board_river_deal_coverage_collect_v2.py --mode study`.
  Both original 78-generation banks loaded. At this snapshot 18 of 1,344
  new cases had verified archive manifests. First-eight-case admission passed:
  conservative projection 1,227,632,327 bytes and 4,292.8 seconds.
- Serial continuation: unified exec session **83018**, Python PID **98396**.
  Command: `board_river_deal_coverage_pipeline_v1.py --collector-pid 98124`.
  Waiting on that specific collector process identity. It then runs independent
  eight-worker readback, verified old-training/new-data merge, 48 fixed fits,
  final evaluation, independent metric readback and report publication.
- Source/plan and training/evaluation controls are frozen. Do not rewrite them
  while the jobs run. Correct execution failures with a new version and
  preserve prior evidence; never change sampling or gates after seeing results.

Read live progress at `board-river-deal-coverage-v1-status.json` and
`board-river-deal-coverage-v1-pipeline-status.json` in this directory. The latter
contains exact completed stage identities. The former retains the earlier
fixture interruption until first collection progress is published, so compare
timestamps and the live process before interpreting it.

Store: `S:/GTOpen-research/board-river-deal-coverage-v1`. Per-stage logs go in
`pipeline/`. New cases are in `cases/` ZIPs and hash manifests. All historical
archives are unchanged; original training data is reused by identity.

The collector has a two-hour invocation cap and resumable per-case records.
The pipeline waits up to two hours for that collector, with a 9,000-second
overall cap. If a guard stops either process, inspect the saved failure before
continuation. Do not launch a second collector or GPU owner concurrently.

## Frozen question and design

Read BOARD-RIVER-DEAL-COVERAGE-PLAN.md. The primary question is whether more
distinct deals help at the SAME row budget: 1,152 rows across 64 versus 192
deals, matching actor/pot strata. Both have exact and sample16-target arms;
two banks, two actors and three paired seeds give 48 fits. All 512-step fits
freeze before scoring 576 states from 32 fresh final deals.

New collection is 768 broad-training plus 576 evaluation cases. Dense uses all
1,152 old TRAINING rows; broad reuses 384 of them. Old final cases are excluded.
Selection succeeded with 192 unique training board groups and 32 fresh final
groups and disjoint visible keys. No selected target was scored at selection.

The initial archive fixture correctly rejected the reused writer's old-store
ownership guard. The failed v1 collector and fixture remain preserved. The v2
collector uses the new-store-owned writer and separate control-v2 location;
archive integrity/corruption/recovery controls now passed. Details are in
BOARD-RIVER-DEAL-COVERAGE-ARCHIVE-CORRECTION.md. No historical files were touched.

Training controls passed with maximum CPU/GPU parameter discrepancy 5.44e-7
and gradient discrepancy 4.47e-8. Scoring controls passed with independent
NumPy/Torch forward discrepancy 5.33e-15 bb. These verify implementation only,
not scientific advancement. The fresh evaluation has not run yet.

## Completed earlier work

BOARD-RIVER-TARGET-LEARNING-FINDINGS.md: exact conditional targets beat sampled
targets in aggregate, but the fixed advancement gate failed one bank's cost
comparison against sample16. Do not reverse that gate.

BOARD-RIVER-GENERALIZATION-CURVE-FINDINGS.md: training-only expansion from 8 to
48 deals reduced development MSE 25.2% and local decision cost 33.1%. The large
train/development gap remained. This motivated the equal-row-budget comparison;
it was not a confirmation of improved preflop ranges.

Those prior jobs are terminal: sessions 20848, 23365 and 67158 exited 0.
Current local evidence commits include a54222d2 (completed results) and
9eac3a18 (new frozen plan/selection/controls). No new push or deployment.

## When the current pipeline finishes

1. Confirm terminal exit codes and all stage proofs, not merely progress text.
2. Inspect both separately registered coverage and target gates, bank/actor/
   pot subgroups, training-vs-final loss, support counts and independent readback.
3. View the generated plot and assess the actual findings. Commit exact
   evidence files and verify source bytes; preserve mutable progress separately.
4. Only if BOTH gates pass consider the separately controlled estimator
   integration described in BOARD-RIVER-TARGET-INTEGRATION-NOTES.md. These
   local binary regressors are not CFR regrets or complete poker policies.
5. If either gate fails, retain the failure and choose a development-only
   representation/regularization study or a justified alternative. Do not tune
   using the spent fresh final evaluation or quietly extend its data.

Keep one research GPU owner, 4 GB CUDA cap, 2 GB external headroom, 2 GB new
study storage cap and 800 GB global allocated-archive cap. Light desktop/video
sharing is authorized; active production solves and heavier work take priority.
No production change, Jev integration, historical deletion or new windows.
