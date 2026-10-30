# Where the finite neural candidate still loses value

This is a **post-hoc diagnostic of the completed no-rake/seed-17 CPU and GPU
runs**, not an independent qualification or a physical-poker result. Both
reached the registered 2,048-update cap. The CPU run passed its two-checkpoint
target; the GPU run did not. Neither stopping decision is changed here.

## Location of the remaining error

The diagnostic improves one player's strategy against the other frozen player,
first allowing changes at public-card decisions, then later preflop decisions,
then the root. Hidden states are combined before choosing an action. Each
restricted best response is checked by evaluating its explicit resulting policy.

| Additional improvement allowed, summed over players | CPU gain | GPU gain |
|---|---:|---:|
| Public-card decisions | 0.0034585192 | 0.0065237365 |
| Then later preflop decisions | 0.0003281601 | 0.0003168156 |
| Then the root decision | 0.0035732676 | 0.0035611495 |
| **Full exact best-response gain** | **0.0073599468** | **0.0104017015** |

These are payoff units in the four-card finite control. They are not measured
bb losses in the actual BB-versus-BTN poker context. The decomposition is
order-dependent, but reconstructs each full exact best-response gain.

The roughly 0.00304 extra GPU residual is concentrated in public-card decisions;
the root contributions are almost identical. This does not demonstrate a
general GPU accuracy penalty. Small arithmetic differences lead to different
self-play trajectories, and this comparison covers one seed and payoff setting.

## The two largest GPU public-card deviations

Changing only information set 21 (player 0, own card 1, public card 3) gains
0.0033944170. Its entry probability is 2.32%; the policy chooses action 1 at
38.75%, although action 1 is worth 0.3780 less than action 0 against the frozen
opponent's final averaged policy. This is not the deliberately rare own-card-3
state in the control.

Changing only information set 6 (player 1, own card 0, public card 3) gains
0.0019962160. Its entry probability is 5.73%; action 1 occurs 16.64% but is worth
0.2095 less than action 0 against the other player's final averaged policy.

These local gains overlap with other deviations and **must not be added** to
one another or to the sequential decomposition above. They were selected after
inspecting final errors, so they are exploratory examples, not reserved tests.

## The errors fluctuate rather than simply fading

A separate frozen diagnostic reconstructs all 60 information sets, both players,
and all 22 saved checkpoints across the two runs. Here are selected checkpoints
for those same two GPU information sets. A positive value difference favors
action 1; a negative value favors action 0.

| Update | Info 6: action 1 frequency | Info 6: value 1 minus value 0 | Info 21: action 1 frequency | Info 21: value 1 minus value 0 |
|---|---:|---:|---:|---:|
| 512 | 19.81% | -0.16345 | 40.05% | -0.01831 |
| 768 | 20.69% | -0.13771 | 38.47% | +0.07444 |
| 1,024 | 15.52% | -0.03659 | 35.76% | -0.51236 |
| 1,536 | 19.72% | +0.06223 | 33.06% | -0.02921 |
| 2,048 | 16.64% | -0.20950 | 38.75% | -0.37802 |

These compare each checkpoint's average policy with its contemporaneous
opponent average. They do not trace a fixed opponent, an individual network's
training loss, or the last-iterate policy. The CPU trajectories also change
sign. The observations rule out a simple description in which all of the
residual is a fixed early mistake monotonically diluted by averaging. They do
not distinguish approximation error, sampling noise, or self-play interactions
as the cause.

## Consequences for the next experiment

Continue the already registered four-run comparisons without extending or
restarting failed cases. The current GPU candidate cannot pass its all-four
gate because this completed case failed. Remaining cases still provide useful
evidence about stability across seeds and rake settings.

Before registering another long candidate, prioritize a controlled check of
continuation fitting stability. A useful comparison must preserve the game,
observation support, sampling and stopping rules, and change a specified
learning choice rather than patching these two decisions. If iteration
weighting is considered, both the fitted advantage objective and the retained
strategy average need a consistent, independently checked definition; merely
discarding early models after inspecting this result is not a valid repair.

The physical batch/CUDA integration check remains separate. Passing it would
show that the transport, fitter and reload agree, not that the new poker policy
is accurate. Physical self-play and independently reserved poker evaluation
remain required before changing the preview or production ranges.

## Reproducible evidence

- `sampled-neural-residual-v1-registration.json` and `-result.json` freeze seven
  inputs and preserve every final information-set deviation. Each local change
  is cross-checked with an independently evaluated modified policy.
- `sampled-neural-residual-trajectory-v1-registration.json` and `-result.json`
  freeze ten inputs and retain all checkpoint decompositions and local values.
  All 22 exact gaps reconstruct, full restricted responses match the existing
  exact evaluator, and final results match the first diagnostic exactly.
- Sources: `tools/research/hu_sampled_neural_residual_diagnostic_20260922.py`
  and `tools/research/hu_sampled_neural_residual_trajectory_20260922.py`.

Both diagnostics are read-only calculations on completed finite policies. They
perform no training, use no GPU, and leave production and the preview unchanged.
