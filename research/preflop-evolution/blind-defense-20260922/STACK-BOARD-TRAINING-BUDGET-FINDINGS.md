# Extra training does not reliably clear the remaining accuracy gap

The paired 8192-versus-32768 update comparison completed in 694.531 seconds.
The longer budget improved fresh-test normalized mean regret by 26.34% in one
seed, but worsened it by 1.10% in the other. Neither seed met the unchanged
absolute accuracy requirement. Do not promote these models or extend this
finished trial.

## What was compared

Both budgets used the same 512 fitting boards and unchanged 362-input, 64/64
networks, labels, optimizer, sampling and legal-action conversion. Each of two
fresh seeds ran one 32768-update chain; the short arm could select only its first
four checkpoints. Selection used 32 new validation boards. All four identities
were frozen before labels were prepared for 64 new final-test boards. The 96
new board groups excluded all 596 earlier probe/learning/coverage groups.

The reference is a terminal river fold/call decision against a uniform legal
opponent hand distribution. Fit depths were 20/40/100/200/400bb; 60/150bb were
excluded from fitting and selection. Their geometry was studied previously;
they are not globally unseen stack settings. This is not a full-game equilibrium
or a direct measurement of preflop range accuracy.

| Seed | Short selected step | Long selected step | Short loss / stack | Long loss / stack | Reduction |
| --- | ---: | ---: | ---: | ---: | ---: |
| 9296701 | 8192 | 16384 | 0.23943% | 0.24206% | -1.10% |
| 9296702 | 8192 | 32768 | 0.28944% | 0.21320% | 26.34% |

These primary means weight 60/150bb equally after normalization by stack.
The first seed fails the relative improvement test; both fail the absolute
limit of 0.1% of starting stack at each excluded depth.

| Seed | Depth | Short mean loss, bb | Long mean loss, bb | Required maximum, bb |
| --- | ---: | ---: | ---: | ---: |
| 9296701 | 60 | 0.13202 | 0.13493 | 0.060 |
| 9296701 | 150 | 0.38826 | 0.38886 | 0.150 |
| 9296702 | 60 | 0.15951 | 0.11685 | 0.060 |
| 9296702 | 150 | 0.46953 | 0.34748 | 0.150 |

Tail errors remain substantial. Long-budget 150bb models have 99th-percentile
losses of 12.57/11.26bb and maxima of 158.40/99.19bb. A small mean is not reliable
hand-level performance. These are new boards and seeds, so absolute errors must
not be compared directly with the preceding 24-versus-512-board study as if it
were a paired regression. All original per-depth/seat/price/category summaries
and adverse outcomes remain in the result.

## Cost and interpretation

The two chains, including validation/checkpoints, took 269.25 and 272.91 seconds.
The qualified storage inventory took 35.875 seconds. Batched preparation took
1.250 seconds for 32 validation boards and 1.844 seconds for 64 test boards.
Both worker groups finished with zero active descendants. Peak CUDA allocation
was 982.56 MB and reserved memory 1002.44 MB. New evidence used 5.44 MB logical
and 4.78 MB allocated storage. Production was unchanged.

The first seed's validation regret improved only slightly from step8192 to16384
and then worsened at32768. The second continued improving. More optimization
alone is therefore not a consistently successful repair under these settings.
The earlier board-coverage gain stands, but neither result yet qualifies an
accurate general continuation model.

Independent CPU replay completed successfully: 796 files verified and
185,966,592 final decision rows reconstructed. Maximum CPU/CUDA context-mean
difference was 7.97e-6bb, below the unchanged 1e-4bb tolerance. Board separation,
shared initial weights, paired checkpoint prefixes, validation-only selection
and both failed gates were independently checked. This verifies implementation
and the negative outcome; it does not convert the failure into a scientific pass.

Next: use the separate
STACK-BOARD-ERROR-DIAGNOSIS-PLAN.md to inspect only existing fitting/validation
errors. It will distinguish board generalization, price sensitivity and action
conversion issues without further training or using final-test labels to choose
a fix. Any new representation or value-head experiment needs a separate frozen
comparison and fresh test boards. The broader preflop goal remains active.

Evidence: stack-board-training-budget-v1-registration.json,
stack-board-training-budget-v1-result.json and
stack-board-training-budget-v1-readback-v1.json. Checkpoints and inputs are retained under
S:/GTOpen-research/stack-board-training-budget-v1.
