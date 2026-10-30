# Coverage still leaves noisy action targets

The first completed, fully audited stratified run has observations for every
starting class on every update. Its saved targets nevertheless vary substantially
within the same class and update. This is a diagnostic of the observations used
to train it, not a completed comparison of playing strength or proof of bad ranges.

The diagnostic covers all 39,936 root decisions: 169 classes across 78 updates,
usually three observations per class/update. It subtracts action values on the
same deal before calculating dispersion. Fold and jam values are constant within
each class/update as expected; the varying call and raise continuations drive
these paired differences. Source importance weights are constant within each
class/update, so they do not change its conditional sample mean. Different
updates use different policies and their target means are not pooled.

| Last 26 updates, 53–78 | Call minus fold | Raise minus call |
| --- | ---: | ---: |
| Median within-cell sample standard deviation | 4.77 bb | 8.75 bb |
| Median sample standard deviation divided by square root of sample count | 2.73 bb | 5.02 bb |
| Class/update cells with both positive and negative samples | 70.94% | 73.99% |
| Mean entry-mass-weighted share with both signs | 71.18% | 74.25% |

The second row is a descriptive sample-standard-error calculation, **not a
confidence interval**. With only about three observations per cell, estimates
of variance are themselves very uncertain. Both signs can also occur when two
actions have similar expected values; this does not measure regret, equilibrium
mixing, the proportion of incorrect decisions, or the error of the averaged
strategy. Observations include changing opponent holdings, boards and sampled
continuations; this diagnostic does not isolate their individual contributions.

## Implication for the next decision

Stratification resolves missing-class coverage by construction. It cannot by
itself remove variation within each class. Finish the second run, the registered
fresh-deal payoff comparison and the full policy-trajectory analysis before
judging this candidate. Do not alter the ongoing fixed-budget study.

If completed results still show unstable ranges, a useful next small experiment
would hold the strategy fixed and measure paired action-target precision as the
number of observations per class increases. That separates observation noise
from changes in the policy being learned. Compare time per useful estimate and
memory/storage costs before committing to another long training run. Any
alternative estimator must retain physical card probabilities and pass an
expectation check; do not infer that simply multiplying iterations or forcing
smooth ranges will solve the problem.

## Evidence and resource use

- [Complete per-cell diagnostic](weighted-within-class-noise-v1-first-arm-result.json)
- [Input bindings and fixed scope](weighted-within-class-noise-v1-first-arm-registration.json)
- [Separate NumPy calculation](weighted-within-class-noise-v1-first-arm-numpy-review.json)
- [Completed source-arm audit](WEIGHTED-FIRST-ARM-AUDIT.md)

Four CPU threads read the already retained target files. The diagnostic completed
in about two seconds, used no GPU or new deals, and did not modify the live
training run. A separate regrouping from all bound raw files checked all 26,364
paired-contrast summaries, with maximum numerical discrepancy 2.85e-14. Known
answer checks covered constant values, changing signs and cancellation of
perfectly correlated action values; invalid/nonfinite samples were rejected.
This recomputation checks the descriptive arithmetic, not the poker engine.

These findings concern one training seed in the restricted 200bb BB-versus-BTN
research game. They do not establish a general accuracy improvement or authorize
production deployment.
