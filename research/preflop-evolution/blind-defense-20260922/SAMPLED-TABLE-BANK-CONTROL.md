# Separating retained-sample noise from neural fitting

The longer neural comparison needs a matching diagnostic baseline. This control
uses the same tiny game, two seeds, rake settings, 256 traversals per player,
frozen policy for both passes, highest-regret fallback, ordinary iteration
weights, checkpoint schedule and 2,048-update cap. Primary evaluation is exact
own-reach averaging of played strategies, matching the retained-model bank.

Two finite tables remove the neural fitting step: one keeps all sampled regret
updates; the other calculates exact empirical means from the same 32,768-example
uniform reservoir per player. These are diagnostics, not scalable storage
proposals for physical poker. Policy trajectories differ because the estimators
differ; matching seeds does not imply identical later sampled visits.

Stop at summed exact deviation gain <=0.01 for two consecutive checkpoints, or
at the update cap. This rule was frozen before running the comparison.

| Control | Rake | Seed | Final update | Final gap | Two-checkpoint target |
|---|---|---:|---:|---:|---|
| All sampled visits | None | 17 | 2,048 | 0.00876820 | No, first crossing at cap |
| All sampled visits | None | 31 | 1,536 | 0.00618874 | Yes |
| All sampled visits | 5% capped | 17 | 2,048 | 0.00795112 | Yes |
| All sampled visits | 5% capped | 31 | 2,048 | 0.00684670 | Yes |
| Reservoir means | None | 17 | 2,048 | 0.01453239 | No |
| Reservoir means | None | 31 | 2,048 | 0.00915106 | No, first crossing at cap |
| Reservoir means | 5% capped | 17 | 2,048 | 0.01504645 | No |
| Reservoir means | 5% capped | 31 | 2,048 | 0.01228468 | No |

All eight runs completed in 67.66 seconds on CPU. Nine frozen input hashes
verified; every stored policy was normalized and independently re-evaluated
with zero reconstruction error. Evidence: `sampled-table-bank-v1`.

## Interpretation

The sampled learning rule can approach the target within this budget when
there is no fitting or retained-sample approximation. A fixed small reservoir
already introduces a measurable limitation: none of its four runs met the
two-checkpoint rule, although one crossed the numerical threshold at the cap.

At update 1,024 in seed 17/no-rake, the three matched-budget gaps were
0.01411562 (all visits), 0.02217607 (reservoir means) and 0.03568577 (neural bank).
Both retaining only a sample and fitting that sample matter in this comparison.
These differences are not additive causal error estimates, because subsequent
learning trajectories change. The neural bank's full four-run result remains
pending; do not extrapolate this one prefix to all runs.

The next candidate should address training-sample and fitting accuracy under a
registered budget, rather than merely extending the current run or accepting a
visually attractive chart. A larger reservoir and lower-noise fitting batches
are plausible separate tests. Neither is justified for production until the
finite controls and then independent physical-poker evaluation pass.
