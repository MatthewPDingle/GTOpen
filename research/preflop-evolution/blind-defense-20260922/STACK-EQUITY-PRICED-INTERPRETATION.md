# Interpretation: keep the reference arithmetic; do not adopt this fitted candidate

The independent CPU audit passed and confirms the scientific failure. The
candidate reduced ordinary held-out-depth decision loss by 3.54% and 41.89%
in the two seeds. The required 20% reduction in both seeds was not met.
Both seeds did satisfy the separate absolute mean-loss limit. These are
different requirements; passing one does not compensate for failing another.

The first seed is especially concerning: at 150bb, average loss rose from
0.12502bb to 0.12890bb, p99 rose from 3.5030bb to 4.2250bb, and the worst
observed decision loss rose from 47.8742bb to 92.8705bb. Its aggregate gain
therefore hides worse behavior at one depth and in the tails at both depths.

The deliberately unusual stress boards worsen in BOTH seeds:

| Seed | Baseline loss / stack | Candidate loss / stack | Increase in error |
| --- | ---: | ---: | ---: |
| 9297601 | 0.95190% | 1.26771% | 33.18% |
| 9297602 | 0.41516% | 1.18277% | 184.90% |

Those stress boards are intentionally unrepresentative. Do not pool them
with random boards to invent a population win rate. They nevertheless show
that the ordinary-board improvement is not robust across board structures.

No claim about overall preflop accuracy follows. This experiment fixes a
uniform legal opponent range at a terminal river Fold/Call decision. It
does not include ranges selected by betting, future actions or full-game
opponent adaptation. It also changes parameter count and model structure,
so it cannot isolate a single cause of the different results.

Independent readback checked 2,900 file identities, board-group separation,
validation-only model selection, complete context results and both gates.
It replayed 557,899,776 correlated decision rows in 1,587.969 seconds and
exited 0. The row count is not independent sample size. This is independent
numeric reconstruction using the retained qualified labels, not another
independent poker engine. All fixed tolerances and prior failed studies
remain unchanged.

Next: integrate the previously supported relative hand/board representation
into complete, history-conditioned continuation training, with explicit
stack inputs and the existing exact/root corrections preserved. The new
STACK-CONTEXT-TRAINING-INTEGRATION-PLAN.md lists the concrete missing pieces.
Do not launch another uniform-equity seed sweep, tune on these final boards
or install the diagnostic weights as an unrestricted strategy.

Main computation and readback are terminal; their locks are released.
Production 56708 is untouched. No GitHub push or deployment occurred.
