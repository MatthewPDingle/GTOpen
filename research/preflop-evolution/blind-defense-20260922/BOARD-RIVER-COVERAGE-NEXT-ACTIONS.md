# Next: matched training with posterior64 river targets

Updated 2026-09-28. Goal active. No study process running at this checkpoint.
Read RIVER-WEIGHTED-STREAM-FINDINGS.md and RIVER-POSTERIOR64-FINDINGS.md.

## Evidence so far

- Earlier broader exact training: fresh local prediction error -16.28% and
  Fold/Call cost -36.28%, mixed subgroup results/generalization gap. Still no
  established full-preflop policy improvement.
- Posterior64 math and native generation qualified: 64 replacement draws from
  exact 990-compatible-hand posterior, complete future actions per selected pair,
  retained multiplicity and common draws across actions. Conditional estimator
  unbiased, covariance /64. Native generation 29.272 -> 11.578 seconds in eight
  cases (one repeat each), not an end-to-end training speed result.
- Actual weighted insertion now qualified: 131 visits, 54 river rows; other
  streets/weights/visit order/Algorithm-R state preserved; both actors overflowed.
  V1 failed replacement-coverage gate; continuous-reservoir V2 passed. Preserve
  both versions and all failure evidence.
- Memory transport qualified byte-for-byte, unchanged policy/target arrays.
  Conditional evidence 34,171,727 -> 675,122 bytes (98.024% smaller).

## Next work

Implement a versioned research worker/pipeline using
river_training_overlay_targets_stream_v1.generate and
river_weighted_overlay_ingest_v1.ingest. Keep the original worker/pipeline intact.
Qualify worker ordering/commit and rejection behavior with real fixtures, then
run a small preregistered matched training/evaluation experiment. Avoid repeated
standalone controls once required integration checks pass.

Authoritatively locate a complete checkpoint before choosing the starting
generation. Existing controlled models were last-played generation 77; completed
iteration 78 includes a different next-model boundary. Restore both arms from
identical full state/config/seeds, preserve the played bank, exact BTN and board
root update, and publish only the complete joint checkpoint. Keep K=64 fixed.

The old pipeline already replaces sampled postflop targets with complete future
action expectations at the sampled private cards. Overlay only visited river
rows AFTER that derivation; never double-apply source weights or propagate
visit-selected replacements into full-action ancestors. Unsupported posteriors
must explicitly fail, not receive invented probabilities.

Use valid complete ClassStratifiedDeals generation and DealWeightGeneration
even for bounded slices. Ordinary bridge queries use first_action_view with
board_training_policy_v1; conditional full-history exports use CPUCurrentPolicy.
Current-policy rows must match. Full all-in cache identity comes from
complete-private-allin-cache-v2-independent-review.json (47,478 canonical pairs).

Fresh evaluation seeds/deals must be registered before use. Spent final datasets
are not tuning inputs. Compare complete time including board targets, fitting,
checkpoint publication and retained evidence. Broader stack/rake/sizing remains
required under STACK-CONTEXT-PLAN.md; this one-context study cannot close the goal.

## Resources and boundaries

Global allocated research cap remains 800 GB; last full inventory 717.79 GB plus
bounded additions remains under 722 GB. Re-inventory before larger admission.
Keep conditional exports in memory; original traces/checkpoints still cost disk.
No historical deletion. Use bounded CPU worker pools and single-thread BLAS.

User authorizes sharing GPU with light desktop/video use. Qualified guard permits
<65% utilization, 4 GB own budget, 2 GB external headroom and 24 GB free RAM.
Heavy workloads and active production solves take priority. Latest GPU probe:
100% utilization, about 9.6 GB used; CPU-only controls performed accordingly.
Recheck load before training; do not silently relax the guard for heavy use.

Keep executed sources and registrations immutable; fixes get new versions.
No deployment, additional push, Jev, Serena windows or other app popups.

## Latest integration checkpoint

river_training_workers_v1.py and river_training_pipeline_v1.py now exist.
river-training-workers-control-v1 passed all 8 cases/131 events, serial versus
spawned-worker parity, original root integration and ordered insertion; five
negative controls. river_training_preflight_v2.py passed source restoration at
completed 78 for both arms and unchanged core-pipeline AST. The result filename
is river-training-preflight-v1.json. Original v1 had a pre-execution syntax error
and remains unregistered/untracked; no training or data changed in that attempt.

No live jobs. GPU still 100% occupied. Next implement and admit the full pilot
runner from RIVER-MATCHED-TRAINING-PILOT-PLAN.md, with fresh storage inventory,
full checkpoint/restart validation and a preregistered fresh evaluation. Source
states are authoritative completed-78 boundaries, next model 78, last played 77.
Two updates are needed for any changed model to enter the played-policy average.
Four source-object copies total 615,647,430 bytes; prospective study cap 8 GB
plus 2 GB reserve. Do not call this pilot started or quality-qualified yet.
