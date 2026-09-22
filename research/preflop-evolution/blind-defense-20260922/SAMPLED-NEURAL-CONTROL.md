# First bounded learned-policy control

**Result: the first neural candidate failed the registered strategic target.**
All four runs completed their budgets and all implementation checks passed.
The failure is retained; neither the preview nor production was updated.

This experiment asks whether learned action advantages and a learned average
policy can replace growing per-information-set tables without losing strategic
quality. It uses the existing finite, nonphysical four-card control and its
qualified exact best-response evaluator. It is not a new poker range, a Wizard
fit, or completion of the wide BB study.

## Registered candidate

Two seeds (17 and 31) are run in both the constant-sum and action-dependent-rake
versions. Every iteration draws 256 external-sampling traversals per updating
player. Both players use the same frozen policy for that iteration. The sampler
enumerates all updating-player actions, including actions with zero current
probability, and samples chance and the other player's actions once.

Each actual visit contributes one training record. Updating-player visits
produce instantaneous sampled action advantages; the other player's visits
produce average-policy examples. Four separate uniform priority reservoirs,
each capped at 32,768 records, retain duplicates and samples from all iterations.
The candidate uses ordinary equal iteration weights, not linear CFR weights.
It does not train on a final regret table or use final table rows as equally
supported examples.

Each player has an advantage model and an average-policy model. Inputs contain
only the observable public history, own card and visible public card. They
exclude opponent cards and unrevealed public cards. The finite tree's unique
public node ID represents its complete betting history; these features are not
yet a physical-poker representation. Each model has two 64-unit ReLU layers.

Advantage models are initialized afresh and trained for 128 Adam steps per
iteration, with learning rate 0.003 and minibatches of 512. A single positive
scalar normalizes advantage targets for numerical conditioning; it cannot
change regret-matching action probabilities. Predictions use positive regret
matching over legal actions, with uniform fallback when no positive advantage
is predicted. Negative training targets are retained.

Average models are initialized afresh at evaluation checkpoints and trained
for 512 steps using masked softmax probabilities and legal-action squared
error. Their predictions do not influence ongoing play. This separates the
advantage-learning trajectory from errors in approximating its average policy.

## Measurements and stopping

The primary measurement is the exact independently evaluated summed best-response
gain of the **learned average policy**. The unchanged finite-control target is
0.01 in control payoff units at two successive checkpoints. Checkpoints are
1, 16, 32, 64, 128 and 256 iterations, with a hard maximum of 256. A failed
candidate is retained as a failure; its target is not relaxed afterward.

Two additional policies diagnose where errors arise:

- The exact own-reach-weighted average of the played iteration policies.
- The cumulative average of all sampled opponent-pass visits before reservoir
  subsampling and neural fitting.

These two diagnostic tables are feasible only in the small control. They are
not substitutes for the bounded learned average and are not offered as scalable
poker storage. Prediction loss is reported separately and is not a convergence
criterion. The aggregate gap can underweight very rare information sets.

The earlier full-traversal and sampled tabular controls used different work per
update and up to 16,000 updates. Iteration counts are therefore not a fair speed
comparison. This is an initial approximation-quality screen, not a claim that
neural learning is faster than tabular learning on this tiny game.

## Implementation controls

Before training, an independent recursive sampler exactly reproduced all 288
supplied-deal/action-draw traversals, including 40 visits with zero own reach.
Both average-policy accumulation contracts agreed. Observable inputs were
checked against all 168 finite decision/deal combinations.

All 120 orderings of five reservoir priorities were enumerated. Every record
was included exactly 48 times in a size-two reservoir, demonstrating K/N
inclusion for that exhaustive control. Results were identical when the input
stream was batched differently. A separate check retained three distinct
targets at the same information set as three records, rather than merging them.

The registered sources and fixture are hashed before execution and checked
afterward. A continuous guard stops only the research child if production
becomes active, free RAM falls below 20 GB, free VRAM falls below 3 GB, or the
1,200-second deadline is reached. Partial results are retained, without an
automatic retry. Port 56708, its sessions and the experimental range preview
are unchanged.

Evidence prefix: `sampled-neural-v1`. The guarded run completed in 585.953 seconds.
Every saved policy evaluation reconstructed exactly and all eight registered
inputs retained their hashes. Each network contains 6,211 parameters; the four
full reservoirs retain 5,242,880 bytes of record payload in total, excluding
temporary fit arrays, allocator overhead and framework state.

## Matched table ablation

`sampled-neural-table-v1` reuses the exact same sampler, chance probabilities,
random seeds, batch sizes, simultaneous updates and 256-iteration budget in
eight finite-table runs. One variant retains every sampled update in a table;
the other uses the same bounded priority reservoirs as the neural candidate
and directly calculates their per-observation means. Both accumulate average
policies through opponent-pass visits. They do not share neural trajectories:
different fitted policies lead to different later sampled actions. This is a
controlled method comparison, not a replay of identical training examples.

The direct-mean variant isolates the effect of reservoir retention from neural
prediction error. Its lookup table is deliberately a diagnostic for this tiny
game and cannot solve the full poker storage problem. The runs independently
stop at the same target or registered maximum; a failure of all methods at
this shorter budget does not erase differences in their remaining gaps.

## Follow-up fitting diagnosis

`sampled-neural-fit-v1` is a post-hoc optimization probe, not another strategic
evaluation. It reconstructs the completed no-rake, seed-17, bounded-table
trajectory and requires exact agreement at all saved average-policy checkpoints.
The final two advantage reservoirs are then held fixed and retained as artifacts.

For each player, the same initialized network is trained with three fixed
budgets: 128 steps with batches of 512; 128 steps with batches of 8,192; and
1,024 steps with batches of 8,192. Training loss is decomposed exactly into
sample variance within identical observations and error in predicting those
observations' sample means. This prevents irreducible payoff noise from being
misreported as network underfitting. The diagnostic also compares the action
probabilities implied by the predicted and empirical-mean advantages.

Better fit in this probe would identify a candidate training change. It would
not prove that change improves self-play, generalizes to unobserved poker
states, fixes the initial UTG response, or meets the full BB target. Its data
comes from the table trajectory, not from the failed neural trajectory.

## Completed results

All gaps below are exact summed best-response gains in **finite-control payoff
units**, not bb in the target poker study. All runs used 256 iterations; none
reached the 0.01 target twice within that budget.

| Payoffs / seed | Neural average | Exact average of neural play | Bounded table means | All-visit table |
|---|---:|---:|---:|---:|
| No rake / 17 | 0.240430 | 0.214514 | 0.052629 | 0.044793 |
| No rake / 31 | 0.246605 | 0.228931 | 0.050179 | 0.032938 |
| Rake / 17 | 0.231820 | 0.205823 | 0.046141 | 0.040768 |
| Rake / 31 | 0.195510 | 0.217186 | 0.036091 | 0.029386 |

The neural candidate leaves 4.57–5.42 times the gap of the bounded table means.
Its exact reach-weighted averages remain poor, so fitting the average-policy
network is not the sole explanation. Retaining bounded examples causes a much
smaller deterioration than fitting this neural candidate. The longer earlier
tabular control reached its target; these shorter runs do not contradict it.

The fitting probe held the two advantage datasets fixed. Increasing the batch
from 512 to 8,192 at 128 training steps reduced the excess mean-prediction MSE
from 0.070362 to 0.016512 for player 0 and from 0.018204 to 0.004476 for player 1.
Running 1,024 large-batch steps produced 0.002321 and 0.005304 respectively;
extra training was not uniformly better. Irreducible empirical variances were
11.884790 and 3.786522, much larger than the fitting error. Lower total training
loss alone would obscure the decision-relevant differences.

The saved rows reveal a concrete problem with the original uniform fallback.
For the common player-0 root observation `(0, 0, -1)`, empirical mean advantages
were approximately `[-1.10447, +0.000552, -0.07833]`. One fitted model predicted
`[-0.98060, -0.04709, -0.10741]`. Although it correctly ranked the second action
highest, all predictions were negative, so standard regret matching returned
one-third on every action. This is an approximation-sensitive decision rule,
not hidden-card leakage or a reason to delete a legal action.

Deep CFR uses the highest-regret action in this case to reduce approximation
effects ([Brown et al., equation 4 discussion](https://proceedings.mlr.press/v97/brown19b/brown19b.pdf)).
Applying that rule to the fixed predictions greatly reduces player-0 probability
differences from empirical-mean regret matching, but helps player 1 less. These
are post-hoc probability differences, not exploitability gains; nearly indifferent
actions can have different probabilities without an important value difference.

## Next isolated comparison

`sampled-neural-max-v1` changes only the all-nonpositive fallback to the highest
legal predicted advantage. The initial uniform strategy, architecture, seeds,
sampler, reservoir capacities, fitting budgets, averaging and target remain
unchanged. Masking and ties have separate controls; an illegal high score cannot
win. The original failed sources and results remain frozen.

This comparison has been started under the same live production guard. It must
earn its own independent strategic result. Better fitting, a published rationale
or the fixed-prediction diagnostic cannot qualify the new self-play policy in
advance. The full BB study and the original UTG response remain uncompleted.
