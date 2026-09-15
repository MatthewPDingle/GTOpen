# Overnight continuation research — corrected result extraction

This is the active continuation-value experiment. It replaces the incomplete
[original batch](../range-value-overnight-20260915/README.md), preserving its
ranges, source partitions, flops, postflop tree menus and model candidates.
Port 56708 is unchanged. No candidate is deployed by this experiment.

## Why references are being regenerated

The original worker stopped after 2,122 references on
`train-seven-open-04-QcJd9c`: its zero-rake values summed to 20.0020475bb
instead of 20bb. Full-precision host storage reproduced the discrepancy.
Materializing suit-equivalent branches and querying every branch explicitly
reduced the discrepancy to 0.00000005bb. The GPU symmetry shortcut's reported
gap was also slightly optimistic for this case: 0.09884% of pot versus
0.10388% under explicit CPU best-response evaluation at 275 iterations.

The corrected runner keeps GPU solving but uses explicit CPU policy/BR queries.
Both GPU and CPU gaps must meet the unchanged 0.1%-pot target. The problem case
passes after 300 iterations, with a CPU gap about 0.0844% of pot. The original
0.002bb pot-accounting threshold is unchanged.

All 3,200 references are regenerated under a new manifest and executable hash.
Earlier files are preserved for diagnosis and excluded from fitting. This
extends the run; successful original integrity audits did not establish that
the symmetry shortcut's per-hand values were correct.

## Frozen experiment

- 24 training range configurations from four source-game families, including
  four controlled perturbations; eight independent cases from two other families.
- 100 training flops and 100 distinct test flops, stratified by pairing/suits.
  Boards used by the earlier pilot/audit are excluded. Inclusion probabilities
  and suit multiplicities are recorded in the manifest.
- 3,200 heads-up GPU postflop references, zero rake, normalized 20bb pot,
  original SPR 1–20, 50% pot bets and 100% pot raises with one raise per street.
  Full turn/river enumeration; no added jam option. Maximum 2,000 iterations.
- Selected ranges and hashes are in fixtures.json. Source preflop values are
  not labels. Range cleaning drops at most 0.1% of source combo mass; tiny probe
  weights and their added mass are recorded.
- Model selection compares the predeclared range-shape and eight-component PCA
  encoders at four ridge penalties. Leave-one-source-family-out validation uses
  training families only. Test outcomes do not choose or tune the model.
- Final evaluation uses separate source games and flops. The point accuracy
  screen requires at least 15% lower range-weighted hand-value MAE than both
  Balanced and raw equity in each test family. Board-bootstrap intervals and
  per-hand best-response diagnostics accompany the result.

Independent integrity checks may read any completed checkpoint during
collection; those checks do not select model features or parameters.

## Operation

`tools/research/continuation_overnight.py` defaults to this directory.
`GTOPEN_CONTINUATION_RUN` can select a different run explicitly. The manifest
pins `target/range-value-reference-night2.exe`; it must not be replaced by an
unrecorded build. The old night1 executable and manifest remain intact.

The controller checkpoints each solve, runs four-job batches and waits between
batches if a preflop solve, postflop solve or report is running on 56708. An OS
lock prevents duplicate controllers. Verify process identities before resuming
after an interruption. A ten-hour reference budget produces a resumable pause,
not completion. Never discard a failed case or silently relax accuracy.

After all references finish, training and independent evaluation run
automatically and produce candidate.json, cross-validation.json, evaluation.json,
RESULTS.md and comparison.png. Completion requires an independent audit, rendered
graph review, measured-result review and GitHub push. Passing this value screen
would still require fresh preflop decision checks and GPU performance validation.

```powershell
python tools/research/continuation_overnight.py run
python tools/research/audit_continuation_overnight.py --partial
python -m unittest discover -s tools/research -p "test_*overnight*.py" -v
```

Run the audit without `--partial` for the completion gate. Its combinatorial
checks independently reconstruct board-blocked hand-pair masses, range values
and the CPU BR gap. The artificial-label pipeline test exercises final model
selection/reporting without reading held-out GPU outcomes.
