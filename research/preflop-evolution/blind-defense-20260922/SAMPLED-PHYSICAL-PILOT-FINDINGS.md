# Full-deck pilot: evaluated, but not ready for use

The first bounded physical BB-versus-BTN pilot completed its fresh-deal evaluation
and full independent readback. **The tested policy still has a profitable root
deviation and is not a production candidate.** This is a result about the new
physical learning prototype, not a finding that the existing UTG/LJ preview or
production ranges have the same error.

Training stopped at its predeclared hour after 78 complete iterations and 4,992
fresh deals. The tested strategy averages played generations 0–77 with each
model's own prior-action reach; generation 78 and interrupted iteration 79 are
excluded. The fixed experiment then used 8,192 different deals to choose one
root action per sufficiently sampled BB hand class, and 16,384 separate test
deals. All later play and the BTN opponent stayed fixed.

## Registered final result

Values are changes in BB's EV **per entry into this BB-versus-BTN spot**, in big
blinds. They are not win rates per randomly dealt hand. The intervals use the
registered conservative bounded estimator and a 5% family error budget across
these five comparisons, with one final look.

| Root decision rule | Mean improvement | Interval |
|---|---:|---:|
| Response learned on separate training deals | +2.080 bb | +0.080 to +4.080 |
| Always fold | +1.330 bb | -0.504 to +3.164 |
| Always call | +0.066 bb | -1.544 to +1.677 |
| Always raise to 6 bb | -2.749 bb | -4.198 to -1.301 |
| Always jam to 200 bb | -22.275 bb | -26.046 to -18.504 |

The learned response's lower bound is positive, exposing a profitable change to
the first decision. Its uncertainty remains substantial; 2.080 bb is a point
estimate, not an exact error size. This root-only test is a lower-bound witness
to exploitable play, never an upper bound on an unrestricted best response or a
joint-equilibrium certificate. The opponent does not adapt to the deviation.

The response had enough training support for **167 of 169 classes**. The other
two retained their complete baseline strategy on **94 of 16,384 test deals**
(0.57%). Neither sparse-class behavior nor the test outcomes were used to change
the predeclared support threshold, policy selection, sample count or stopping
rule.

## What changed in the response

The following frequencies use the exact compatible-entry class distribution.
They describe the tested bank and the separately trained response; they are not
recommended poker ranges.

| BB action | Tested bank | Trained response |
|---|---:|---:|
| Fold | 48.87% | 69.16% |
| Call the extra 1 bb | 21.18% | 6.67% |
| Raise to 6 bb | 16.16% | 8.83% |
| Jam to 200 bb | 13.79% | 15.34% |

A post-hoc decomposition of the existing held-out result attributes +2.496 bb
per entry to classes where training selected fold, +0.166 to call classes,
+0.111 to raise classes, and **-0.692** to jam classes. These sum to the published
+2.080; they are descriptive contributions, without new group-specific confidence
claims. They show why neither indiscriminate widening nor copying the response's
shove range is warranted. The responder itself has noisy choices and is not a
replacement equilibrium.

The tested bank's sample EV was -2.330 bb and the response's was -0.250 bb,
including the already posted BB. Always folding is -1 bb. The comparison remains
against this frozen experimental opponent, not against Wizard or a real pool.

## Training has not stabilized

A descriptive trace inspected every saved generation, using all 169 visible
root states and exact compatible-entry mass. It did not select a checkpoint or
run another strength comparison.

- The complete played bank jams 13.79%; the last ten played generations average
  8.34%. Early behavior still influences the average, but the initial uniform
  generation alone cannot explain the remaining jam frequency.
- Played generation 77 calls 23.88% and raises 11.58%; newly fitted, unplayed
  generation 78 calls 14.90% and raises 18.88%. A single update still moves these
  allocations substantially. Generation 78 was **not** substituted into the test.
- These traces indicate continuing policy movement; they do not prove that the
  late models are stronger or identify the sole cause of error.

The trial had only 4,992 training deals spread over preflop and postflop decisions.
Sparse/noisy targets, function fitting, early-policy averaging and the restricted
game can all matter. This evaluation does not isolate one as the cause. The
earlier UTG/LJ missed-call result came from another game and method; it should
not be used to prescribe a universal increase in calling here.

## Execution and audit

The persistent CUDA evaluator finished all **1,536 batches in 1,250.38 worker
seconds** (about 20.8 minutes; 1,253.91 seconds including controller overhead).
The CPU execution was deliberately superseded after 1,392 training deals, before
its responder or test stream. Both versions share the same registered seeds;
they are not independent confirmations. The GPU version passed the old-fixture
control and comparisons on 256 completed CPU training deals before proceeding.

The final readback took 319.64 seconds and verified **199 source/reference inputs**,
all batch artifact hashes, both chance streams, legal action probabilities,
pure root deviations with all later policies unchanged, training-only response
selection, all **81,920 paired differences**, and independently reconstructed
the final interval means, variances and bounds. Maximum root-mixture error was
2.85e-14 bb and forward-payoff discrepancy 7.96e-13 bb. Neural inference and native
traversal were not rerun during readback; their execution controls are separate.

Minimum recorded free resources were 99.03 GB host RAM, 22.32 GB VRAM and 190.37 GB
SSD space. Production and the range preview remain unchanged. The faster evaluator
is useful research infrastructure, not a speedup claim for the production solver.

## Next experiment

Keep this result as a failed-quality baseline. Do not patch individual hands from
the inspected test deals or relabel the trained response as GTO.

The next practical step is to reduce repeated GPU-training preparation work while
preserving the retained-data objective and checking gradients. That can fund a
larger, explicitly budgeted training trial with more fresh deals per update. Its
sample/iteration budgets and candidate-selection rule must be declared in advance,
and it needs new evaluation streams. Any altered averaging or fitting method is
a separate algorithmic change requiring its own check, not an unnoticed shortcut.

The current experiment has not closed the accuracy gap. It has established a
feasible full-deck train/evaluate path and produced an independently checked
failure that the next candidate must improve on.

Evidence prefix: `sampled-physical-root-study-gpu-v1-`, especially `result.json`,
`independent-review.json`, `interpretation.json` and `root-bank-trace.json`.
Training evidence: `sampled-physical-pilot-gpu-v1-independent-review.json`.
