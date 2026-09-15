# Overnight continuation research — 15 September 2026

This run addresses the coverage and noisy-label problems found in the
[first learned-value pilot](../range-value-pilot-20260915/README.md).
It is offline research; the live application on 56708 is unchanged.

## Frozen batch

- **32 range configurations:** 24 training configurations from four saved-game
  families, including four controlled perturbations; eight test configurations
  from two separate saved-game families.
- **200 distinct flops:** 100 training and 100 test flops. No overlap with each
  other or the 60 boards used in the earlier pilot/audit. Each side is stratified
  by pairedness and suit count, with inclusion and suit-multiplicity weights.
- **3,200 reference solves:** one per case and board in its partition. Full
  turn/river trees, 50% pot bets, one 100% raise per street, no extra jam option,
  zero rake, heads-up, SPR 1–20. Pot amounts are normalized to 20bb, preserving SPR.
- Source ranges come from approximate preflop solvers/models. Their payoffs are
  **not** used as labels; postflop values are recomputed. All descendants of a
  source save stay in its partition. Some source games have rake, but the new
  postflop reference game explicitly has zero rake.
- At most 0.1% of source range combo mass is truncated. Sixteen probe classes
  receive at least 0.0001 weight in both ranges; added mass is recorded per case.
  Raw extraction inventories stay local; selected ranges and source hashes are
  in [fixtures.json](fixtures.json).

The reference target is 0.1%-pot aggregate exploitability, at most 2,000
iterations. Per-hand best-response values for both players provide a separate
rare-hand quality diagnostic. A small aggregate gap alone does not guarantee
accurate values for every nearly absent hand.

## Candidate comparison

Two regularized predictors are compared: one adds range concentration and
hand-composition features; the other also uses eight principal components
of the complete 169-class range vectors. PCA and regularization selection use
training source families only, with leave-one-source-family-out validation.
The test labels are opened only after candidate selection is frozen.

Targets are policy EVs with an equity control variate. Compatible concrete-hand
counts weight range values. The learned residual is centered to conserve the
whole pot, while individual hand values may exceed the starting pot.

The accuracy screen requires at least 15% lower hand-value MAE than both
Balanced and raw equity in each independent source family. Results include
paired board-bootstrap uncertainty and rare-hand best-response checks. Passing
this screen would still require fresh preflop decision checks and GPU
time-to-target/memory measurements. This run **never deploys a candidate**.

## Operation and resumption

Started at approximately 20:06 Adelaide time on 15 September. The controller
has a ten-hour reference budget and checkpoints each completed solve. It checks
56708 between four-job batches and waits if a live solve is running. It never
stops, loads, rebuilds or restarts the user's sessions.

`status.json` records the controller and active child PIDs, progress and phase.
Verify those processes and command lines before treating a run as active.
An OS file lock prevents duplicate controllers. Resumption refuses to start if
the previously recorded reference child is still alive. Failed references or
accuracy failures stop with `attention_required`; they are not silently skipped.
Budget expiry produces `paused_time_budget`, not a completed result.

When all references finish, the controller automatically trains candidates,
evaluates the independent cases, and writes `RESULTS.md`, `evaluation.json`
and `comparison.png`. The goal remains incomplete until those artifacts and
their supporting jobs have been checked.

```powershell
cargo build --release -p solver --example continuation_range_inventory
cargo build --release -p solver --features gpu --example range_value_reference
python tools/research/continuation_overnight.py inventory
python tools/research/continuation_overnight.py prepare
python tools/research/continuation_overnight.py run
python -m unittest discover -s tools/research -p test_continuation_overnight.py -v
```

The retained runner `target/range-value-reference-night1.exe` is identified by
the manifest hash; recompilation to another hash requires a separate run.
The source inventory step requires the local saved games. The provided selected
fixtures/manifest are sufficient to reproduce reference solves without those saves.
