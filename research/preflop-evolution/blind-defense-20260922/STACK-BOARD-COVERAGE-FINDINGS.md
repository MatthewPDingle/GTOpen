# Broader board coverage substantially improves the diagnostic, but misses its gate

The fixed-network comparison completed and its results independently replayed.
With the same network and update budget, 512 fitting boards reduced the average
cost of mistakes on fresh final-test boards by about92% relative to24 boards.
The result supports board coverage as a major limitation of the preceding model.
It does not yet meet the preset absolute accuracy threshold or establish better
full-game preflop strategies.

## Paired comparison

Both arms used the same362-input64/64 player networks, Adam0.001 and8192 updates
of4096 rows. Initial weights match exactly within each seed. The24-board set is
a prefix of the512-board set. All544 boards (512 fitting,16 validation,16 test)
exclude the preceding52 probe/learning groups. Every legal physical hero holding
retains its weight. Checkpoints were selected on validation and frozen before
final-test boards/labels were prepared.

The reference remains a uniform-opponent, terminal river fold/call decision.
It is not a betting-induced range or a full-game equilibrium. Fit depths are
20/40/100/200/400bb;60/150bb are excluded from fitting and selection. Their
geometries were examined in earlier experiments; these are fresh board tests,
not globally unseen stack configurations.

Primary averages give equal weight to60/150bb after normalizing each depth's
regret by starting stack. Regret means value lost by the actual mixed policy
relative to the exact better legal action, not simply the rate of wrong actions.

| Seed | 24 boards, mean loss / stack | 512 boards | Reduction |
| --- | ---: | ---: | ---: |
| 9296601 | 1.77836% | 0.13252% | 92.55% |
| 9296602 | 2.17827% | 0.17682% | 91.88% |

| Seed | Depth | 24-board loss, bb | 512-board loss, bb | Target, bb |
| --- | ---: | ---: | ---: | ---: |
| 9296601 | 60 | 0.99074 | 0.07775 | 0.060 |
| 9296601 | 150 | 2.85822 | 0.20318 | 0.150 |
| 9296602 | 60 | 1.22984 | 0.09893 | 0.060 |
| 9296602 | 150 | 3.46021 | 0.28314 | 0.150 |

Both pass the relative-improvement requirement, but both fail the absolute
requirement of<=0.001 starting stacks at each excluded depth. The gate remains
FAIL; its threshold was not relaxed after seeing the result. All five
fitting-depth slices on the fresh test boards also improve in both seeds.

Tail errors remain material. At150bb the broader models'99th-percentile losses
are6.91/8.73bb and maximum losses are about33bb. Small mean loss is not a guarantee
that individual hands or difficult boards are correct. The result retains every
depth, seat, price band, hand category and requested quantile. There are no
population confidence intervals or full-game best-response certificates here.

## Learning curves and cost

The broader models selected step8192 in both seeds. Their normalized validation
losses continue decreasing across1024/4096/8192 updates:0.003283/0.002449/0.002054
for seed1 and0.003208/0.002130/0.001756 for seed2. The narrower models instead
selected4096 and1024. These validation observations justify testing a larger
fixed learning budget on broad coverage; they do not justify continuing the
completed trial or treating its test as fresh validation.

Whole invocation520.078s (8.67min): global allocation inventory188.140s;
528-board fitting/validation preparation16.828s; four fits including validation
and checkpoints73.422/70.219/64.531/68.000s. Test preparation5.797s. Eight hidden
workers processed batches, avoiding a Python/Torch import for every board.
Both owned worker groups ended with no active descendants.

The broad CUDA dataset is806.56MB. Peak total CUDA allocation995.92MB; reserved
1015.02MB. New evidence19.38MB logical /16.64MB allocated,588 files. No historical
files were deleted and no production session changed. This measures a small
component experiment, not preflop solver throughput.

## Verification and next decision

Independent CPU matrix inference replayed46,491,648 final rows, verified734
input/artifact files, checked board identities/separation and paired initial
weights, independently selected checkpoints and recomputed both gate failures.
Maximum CPU/CUDA difference in context mean regret was6.48e-7bb.

Evidence: `stack-board-coverage-v1-registration.json`,
`stack-board-coverage-v1-result.json`,
`stack-board-coverage-v1-readback-v1.json`; retained inputs/checkpoints in
`S:/GTOpen-research/stack-board-coverage-v1`.

Next: a newly registered paired short-versus-long training-budget experiment on
the existing512-board fitting set, with fresh validation/test groups. Preserve
the network and feature definitions to separate an optimization-budget problem
from a representation problem. If it still misses the gate, analyze only its
training/validation errors before choosing a structured-board or value-head
change. A successful diagnostic must then advance to a multi-decision reference
with independent best responses. It would not by itself justify deployment or
complete the user's broader preflop objective.
