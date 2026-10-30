# Reading the short river pilot

Prepared 2026-09-28 while the first baseline arm was running, before any final
test deals or candidate results were available. This supplements the frozen
pilot plan; it does not change the runner, budgets or registered test.

## What can change, and when

The pipeline computes board-root targets from the current played model before
fitting the next model. The exact BTN first response to a BB shove also uses
the current root and current response. The next model is excluded from the
played-policy average until it has actually played.

Starting with the same complete state at iteration 78:

| Completed update | Newly fitted model | Earliest possible treatment effect | Last played model |
| --- | --- | --- | --- |
| 79 | 79 | River training targets can alter the postflop network | 78 |
| 80 | 80 | The changed postflop network can alter the BB root | 79 |
| 81 | 81 | The changed BB root can alter the exact BTN shove response | 80 |
| 82 | 82 | Both of those changed preflop components can now be in the played bank | 81 |

These are earliest possible effects, not promises of numerical changes or
improvement. Other preflop lookup rows/fallbacks may change differently. A
shared regression scale can introduce roundoff into otherwise unchanged table
rows; compare actual root/response policies and numerical accumulator state.

The current two-update pilot ends at 80. Its evaluated bank contains models
0..79. The paired BB root and exact BTN shove-response policies are therefore
still unchanged. Model 80 is diagnostic evidence only, since it has not played.
The one changed played model contributes weight 80/3240 = 2.4691% before
conditioning on a player's own earlier actions. This fraction is not a bound
on every displayed conditional decision's change.

Readback code checks those propagation expectations explicitly and reports
model 80 separately. Root provenance hashes can differ even if numeric regrets
match; comparing only file hashes would misidentify that as a range change.

## Statistical limits

The registered full-policy comparison uses 1,024 common physical deals, eight
contrasts, a single final look and conservative bounded empirical Bernstein
intervals. At the current 200 bb stack and 0.5 bb dead money, its fixed paired
payoff bound is +/-400.5 bb per entry. The interval's additive term alone is
11.80497 bb per entry at 1,024 deals, before its variance term.

That design can check execution, cost and descriptive effect direction. It is
not powered to establish a small poker edge. Report its original intervals,
including inconclusive results; do not call positive point estimates proof,
replace them with naive per-action sample counts, tune on the test set, or
interpret fixed-opponent gains as an upper bound on best-response exploitability.

An eventual more sensitive evaluation needs a prospectively justified design.
Possible rigorous improvements include exploiting the common unchanged part of
the played-policy mixtures to bound their paired payoff difference more tightly,
and increasing independent deals. The mixture argument requires proof against
own-history weighting and exact bank identities before adoption. It is not
implemented or used to reinterpret this pilot's registered confidence intervals.

## Next experiment decision

1. Finish the current full-update restart checks, matched training and frozen
   evaluation. Use river_matched_pilot_review_v1.py for CPU readback afterward.
2. Measure full update wall time, external GPU waiting and new evidence bytes.
   Report qualification/replay cost separately. Worker timing categories overlap
   and cannot be summed into end-to-end speed claims.
3. If the integration is valid and costs are affordable, continue matched arms
   through at least four new updates to expose preflop feedback. A substantive
   learning comparison should use a longer fixed continuation, provisionally
   16-32 new updates, sized from the measured runtime and storage rather than
   selected from favorable test outcomes. Register its actual budget and fresh
   evaluation before running it. Preserve every source state and failed attempt.
4. Assess complete policy gains and preflop range movement, then test equal-time
   budgets and additional stack/rake/sizing contexts. This single-context pilot
   cannot establish broad preflop accuracy or justify production deployment.

Sources inspected: board_training_pipeline_v1.py, river_training_pipeline_v1.py,
board_training_targets_v1.py, board_training_policy_v1.py,
exact_btn_regret_accumulator_v1.py, crossed_complete_policy_comparison_v1.py,
sampled_evaluation_intervals_v1.py. The registered runner and sources stay frozen.
