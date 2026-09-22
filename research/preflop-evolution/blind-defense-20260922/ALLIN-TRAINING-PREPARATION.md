# Conditional all-in trial admitted after the hybrid evaluation

The exact cache has now [completed and passed review](ALLIN-TRAINING-CACHE.md),
including all scheduled deals through the actual loader. The new trial has
cleared the hybrid study's evaluation and review prerequisites. Its frozen
[plan](SAMPLED-PHYSICAL-ALLIN-PLAN.md) changes the dense trial's preflop all-in
estimator while preserving its training recipe. It adds a predeclared BTN
response family to the fresh evaluation, so the BB root result is not the
only player-specific check.

## Completed preparation checks

- The adapter passed 1,824 private-pair label checks across suit permutations,
  within-hand order and independently enumerated player-swap fixtures. Player
  roles are preserved when constructing cache keys.
- Sixteen malformed or incompatible inputs were rejected, including missing
  physical pairs, altered labels, stale cache identity, illegal policies and
  old-format ingestion. A bad final record is rejected before any insertion.
- Format-3 native traversal verified 32 updater passes. Its 303 BB and 91 BTN
  advantage records produced exactly the same bounded reservoir arrays and
  RNG states as direct per-visit insertion.
- The pipeline audit compared the complete training-worker syntax tree with
  the dense worker after accounting for only the declared cache/estimator
  transport changes. Sampling, fitting and checkpoint progression match.
- The root evaluator matches the existing full-deal evaluator except that
  its family error allowance is 0.025, reserving another 0.025 for three BTN
  comparisons. The BTN selector's support, no-reach and tie cases, and the
  interval formula, passed executable controls.
- The sequential runner contains training, training replay, evaluation
  preparation, BB evaluation/readback and BTN evaluation/readback. It stops
  on a failed stage without automatic retry or candidate substitution.

These are preparation and correctness checks, not completed training or poker
accuracy evidence. Native tests and the earlier estimator noise results are
documented in [ALLIN-BRIDGE-CONTROL.md](ALLIN-BRIDGE-CONTROL.md).

## Active run

The [versioned admission update](ALLIN-ADMISSION-V3.md) requires the complete
repaired hybrid evaluation and subsequent readbacks. The v2 launcher stopped
before training because the child trainer also referenced the obsolete hybrid
evaluation. Its failure is preserved; the corrected trainer retains exactly the
same training worker. Ten earlier offline rejection cases and the subsequent
source-isolation/live-prerequisite checks passed. The v3 launch is now training.
It also enforces the cache review, shared GPU lock, reserves and idle checks:

```powershell
& 'C:\Program Files\Python312\python.exe' tools/research/hu_sampled_physical_allin_study_v3_20260923.py --run
```

The training trial is admitted; do not run this command again while it is live.
Its artifacts use `sampled-physical-allin-pilot-v1`,
`sampled-physical-allin-evaluation-v1`, `sampled-physical-allin-btn-evaluation-v1`
and `sampled-physical-allin-study-v3`. The completed hybrid trial retains its
sources, model and evaluation records. Production and preview are untouched.

Evidence: `sampled-physical-allin-protocol-control-v1-{registration,result}.json`
and `sampled-physical-allin-pipeline-control-v1-result.json`. The latter freezes
the prepared sources and plan; do not silently modify them after admission.
