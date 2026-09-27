# Independent readback of board-root training

The separate native-board check passed on 27 September 2026. It reconstructs
all four retained public boards and all 169 BB hand classes under the existing
synthetic policy fixture. This checks the checker before using it on learned
models. It does not establish playing strength.

| Check | Maximum absolute difference |
|---|---:|
| Independently reconstructed preflop policies | 1.11e-16 |
| Scalar exact preflop cashflows | 2.84e-14 bb |
| Dense forward public-board cashflows | 7.46e-14 bb |

Four CPU workers completed in 91.17 seconds while the main GPU evaluation
continued. They used no CUDA. The slower, dense forward calculation is an
audit reference, not a proposed training implementation. No production state
or running evaluation inputs changed.

Evidence: `board-training-readback-control-v1-registration.json` and
`board-training-readback-control-v1-result.json`. The source is
`tools/research/board_training_readback_support_v1.py`; the qualification is
`tools/research/board_training_readback_control_v1.py`.

## Full trained-state audit prepared; not yet run

`tools/research/board_training_pipeline_readback_v1.py` waits logically on the
successful result of `board-training-pipeline-control-v1`. Its `--check-ready`
currently reports that this prerequisite is pending. The existing queue runs
that GPU control after the complete fresh evaluation and its readback.

After the prerequisite passes, run:

```powershell
& 'C:\Program Files\Python312\python.exe' tools/research/board_training_pipeline_readback_v1.py --workers 8
```

The audit is capped at 30 minutes. It uses up to eight physical-target CPU
workers plus four board workers, with one math-library thread per child and
at least 24 GB available RAM in the coordinator (20 GB in workers). It starts
only below 50% CPU utilization with production idle; continuing guards check
production and memory. No GPU fitting occurs. A failed audit requires
inspection, not automatic retry or admission of a learning study.

For both completed trained generations it will verify:

- Physical deal selection, importance weights, action seeds, native sampled
  targets, conditional postflop targets, and played policies.
- Every board request and regenerated native tree hash, complete compatible
  private-card support, board chance weights and dense forward cashflows.
- Independent scalar exact preflop terms and accumulated BB and BTN regrets.
- Reservoir contents, replacement RNG state, the physical sampler boundary,
  played-model history, complete checkpoint and final unplayed model exclusion.
- Model/plan/evidence identities and immutable source/artifact bindings.

The existing physical-target readback is reused; its sampled BB root updates
are checked but are **not** added to the new board-root accumulator. The public
board estimates are the only BB root update in this method.

Shared limits remain: native poker engine, feature representation, physical
sampler and reservoir implementation. This is not an independent poker engine,
independent optimizer refit, convergence proof, or a range-quality result.
The full reader has passed import/syntax and prerequisite checks only so far.
Only a successful trained-state result can qualify the complete pipeline for
a separately registered matched learning experiment.
