# Weighted 112-board study: interim iteration 100

The registered weighted run resumed from iteration 20 and completed its
iteration-100 evaluation. It continues toward the registered iteration-500
checkpoint. Neither the segment nor the full comparison is complete.

| Measure | Iteration 20 | Iteration 100 |
| --- | ---: | ---: |
| Within-training-panel total gap (bb) | 5.454921 | 0.823835 |
| Root fold | 76.722% | 74.448% |
| Root call | 8.421% | 8.734% |
| Root 4-bet | 11.708% | 13.159% |
| Root jam | 3.149% | 3.658% |

These frequencies are the native evaluator's training-panel aggregates, not
the separate common-physical-prior comparison. The lower gap shows progress
toward convergence within this restricted game; it does not establish
accuracy on unseen flops or agreement with a full preflop solution. The
iteration-100 gap remains well above the study's 0.01 bb criterion.

The immutable `strategic-weighted112-100-v1-interim-result.json` was copied
from the live output only after its complete iteration-100 evaluation was
available. Its companion review records the content hash and checks:

- Exact equality of the resumed iteration-20 evaluation to the saved seed.
- Frozen executable, segment inputs and registration dependencies.
- Finite values, normalized strategies, terminal probability and chip/rake
  accounting using the existing seed validator.
- All 224 RAM entries and 240 transfers per entry for the 80 new iterations;
  no per-iteration SSD reads or writes.
- Resource samples through this observation: at least 25.697 GB available
  host memory and 11.870 GB available GPU memory (decimal units).

The evaluation took 284.796 seconds. The log's `evaluation_seconds` value
is cumulative across both evaluations, not the duration of this one.

No experiment settings, iteration targets, production application, or
reserved comparison were changed. Final checkpoint verification, the
equal-weight control and the reserved-flop evaluation remain pending.
