# Exact-game diagnostic: results

This is a deliberately tiny two-round, three-card poker game. It has every legal deal enumerated and a full-game equilibrium reference. It does not run GTOpen's GPU kernel or establish Hold'em accuracy. Production on port 56708 was not changed.

## What the controlled comparison found

Both versions of the exact continuation interface pass the original 0.005-chip full-game error threshold with more iterations. The original 5,000-iteration failures remain failures at that budget. The basic split design can work in this game; the short-run outcome also depends on the equilibrium selected by the continuation solver.

| Approach | Full-game NashConv at 5,000 | At 20,000 | Frozen-value gap at 20,000 | Elapsed seconds at 20,000 |
|---|---:|---:|---:|---:|
| Full game | 0.002759 | 0.001365 | n/a | 3.6 |
| Exact continuations | 0.007225 | 0.003037 | 0.003037 | 124.9 |
| Exact + zero-hand completion | 0.005163 | 0.002578 | 0.002578 | 129.5 |
| Predicted values; exact completion | 0.084916 | 0.084957 | 0.000072 | 29.7 |

NashConv is the sum of the gains available to both opponents by changing their entire strategy. Lower is better; the normal-form LP reference is within 1e-8 of zero. These are chips in this miniature game, not big blinds or the overnight experiment's frozen-value gaps. Timings include checkpoint work and are not repeated production benchmarks.

**The clearest finding is false confidence from the stopping measure.** With predicted values, the frozen-value gap reaches 0.00007177, while true full-game error remains 0.084957. The weakest card bets 53.0% instead of about 33.3% with exact values. More iterations settle the approximate game without repairing this strategy error. This is a counterexample in the miniature harness, not proof that the same cause explains the overnight Hold'em result.

The predicted arm supplies only upper-tree hand values. For independent full-game evaluation, its final upper ranges are completed by fresh exact continuation solves. Therefore it is an oracle-completed policy, not a complete learned agent.

The fixed surrogate's registered practical screen **failed**. On 256 independent held-out range contexts, corrected hand-value MAE is **0.0756 chips**, 95th-percentile absolute error **0.3566**, and maximum **2.5255**. Raw MAE before physical projection is 0.0712. No model settings were selected using these results.

## Why averaging and absent hands need separate treatment

In the initial LP-backend run, averaging all intermediate exact continuation policies produced full-game NashConv 0.21334 at 5,000 steps, while completing the averaged upper ranges with a fresh exact solve gave 0.00387. The robust backend produced a different outcome. This is evidence that blindly stitching intermediate strategies can be misleading; it does not show that GTOpen currently makes that particular error. A separate rerun reproduced both outcomes and verified their full policies by tree and normal-form best responses. [Averaging audit](averaging-audit.json).

The follow-up completed actions only for hands with exactly zero own probability. Their actions are unconstrained by the continuation equilibrium objective, yet their values can affect earlier decisions. The change preserved the continuation's expected payoff on its input distribution. Its effect is shown separately; this is not the same as replacing an entirely empty range with a prior.

## What to do next

Use this miniature game as a permanent correctness fixture. Next match GTOpen's alternating discounted update schedule and actual value-transfer code, then add a richer exact game. The present independent harness uses simultaneous vanilla CFR. A passing toy test does not clear the production integration or solve the multiway approximation problem.

Before further large training runs, inspect prediction errors at the sparse range contexts actually reached during search and compare the frozen-value stopping number with true full-game error. Avoid concluding that lower average prediction error guarantees faster or more accurate complete-game solving.

## Reproducibility and failures

Default LP precision and then tighter tolerances alone each failed the 1e-8 continuation duality check before model fitting. Their completed controls and freezes are retained. An explicit interior-point backend without presolve passed all fixed label checks. The original 5,000-step experiment, the zero-hand follow-up and the longer extension each have separate preregistered inputs; none silently replaces a failed run.

The final audit verified 39 frozen-input entries, 12 result files, every stored full-game value and best response against both normal-form enumeration and a separate tree traversal, repeated upper policies, no exact training/test overlap, prediction error reproduction and physical projection.

[Protocol](PROTOCOL.md) Â· [Audit](audit.json) Â· [Graph](comparison.png)
