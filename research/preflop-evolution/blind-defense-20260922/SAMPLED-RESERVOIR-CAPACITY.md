# Larger retained samples in the matched finite control

Keeping eight times more examples improved this finite diagnostic. With exact
empirical means and a 262,144-example reservoir per player, all four runs ended
below the numerical 0.01 target and three passed the required two consecutive
checkpoints. With 32,768 examples, one ended below the numerical target and none
passed the two-checkpoint rule. No neural fitting or physical-poker learning was
performed in this comparison.

The registered change was reservoir capacity only. Game, seeds, traversal
counts, uniform priority retention, highest-regret fallback, ordinary iteration
weights, evaluation, checkpoint schedule and 2,048-update ceiling were retained
from [the matched table control](SAMPLED-TABLE-BANK-CONTROL.md). A full-visit
mean accumulator was collected for diagnosis only and never affected play.

| Rake | Seed | Final update | Final gap | Two-checkpoint target |
|---|---:|---:|---:|---|
| None | 17 | 2,048 | 0.00862820 | Yes |
| None | 31 | 1,024 | 0.00867470 | Yes |
| 5% capped | 17 | 2,048 | 0.00848383 | No, first crossing at cap |
| 5% capped | 31 | 2,048 | 0.00572747 | Yes |

At the shared 1,024-update checkpoint, all four larger-reservoir runs had lower
gap than their smaller-reservoir counterparts: 0.01342 vs 0.02218, 0.00867 vs
0.01812, 0.01362 vs 0.02123, and 0.01068 vs 0.01288. The early-stopped run is
not described as a 2,048-update result. Sampling paths subsequently differ as
policies change; these are matched-budget comparisons, not identical datasets.

Both reservoirs together hold 20,971,520 bytes of retained record payload
(20 MiB), before temporary arrays and other state. This estimate covers this
finite representation, which stores information IDs rather than full physical
poker observations. The four CPU runs completed in 141.09 seconds. Ten frozen
inputs verified, every stored policy normalized, and every evaluation
reconstructed with zero error. Evidence prefix: `sampled-reservoir-capacity-v1`.

The final seed-17/no-rake reservoirs were saved under `target/research-sampled/`
with hashes and sizes in the result. They allow a later fixed-data fitting
diagnostic without silently resampling a favorable dataset. This is not a
training-resume checkpoint: full sampler and optimizer state are not included.

## Implication for the next neural candidate

The original neural bank remains under its existing four-run registration.
Its first completed 2,048-update run reached gap 0.02791288, so merely keeping
its policy models and extending training did not meet the target in that run.
The larger-reservoir table result supports testing larger retention in the
neural learner, while leaving open the separate fitting-error problem.

Before committing to another long neural comparison, use the frozen larger
reservoir to check whether less noisy fitting batches reproduce its empirical
action advantages and decisions more accurately. A fit diagnostic cannot
replace a self-play convergence test. Any next neural comparison needs its own
frozen configuration and budget; all four current runs must be retained, and
no passing toy result alone qualifies the wide BB/BTN poker policy.
