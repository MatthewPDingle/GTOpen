# The small network also loses information at the first preflop decision

This is a training-only diagnosis of the old pilot's **unused generation 78**,
not a new strength test or a replacement for its evaluated 0..77 policy bank.
The running larger-data candidate remains unchanged.

The BB model's first decision has 4,992 retained visits across all 169 hand
classes. Class counts range from 7 to 66, with a median of 22. Its fitted
four-action advantage scores differ from the empirical grouped training targets
by **13.68 bb RMS**, weighted by retained visits and legal actions. Those targets
are noisy historical regret samples, not independently known action EVs.

The disagreement changes action selection substantially. Matching positive
empirical mean regrets gives a visit-weighted mix of approximately
**47.1% fold / 24.0% call / 16.6% raise / 12.3% jam**. The fitted network gives
**56.4% / 14.4% / 19.5% / 9.8%** on those same visits. Per-hand total-variation
distance averages 0.419: the aggregate mix conceals larger hand-level differences.
Neither policy is established as good poker, and these frequencies are not the
own-reach-weighted played bank used in the completed strength evaluation.

## Where the fitting objective spends its weight

| BB subset | Share of legal training targets | Share of grouped squared fitting error |
|---|---:|---:|
| All preflop decisions | 10.27% | 2.12% |
| Flop | 11.48% | 12.08% |
| Turn | 25.34% | 32.44% |
| River | 52.91% | 53.36% |
| First preflop decision (subset of preflop) | 7.76% | 0.84% |

Most retained postflop observations are unique. Their targets contain sampling
noise, but the shared network still fits them alongside repeated preflop states.
This creates a plausible fitting compromise. The decomposition does not isolate
capacity, optimizer budget or data noise as the sole cause. It also does not
establish that changing the loss weighting will improve held-out poker strength.

## What to test next if extra data is insufficient

Finish the preregistered larger-data trial first. A subsequent controlled variant
could represent the small preflop observation set directly, while retaining the
network for the enormous postflop state space. That would remove preflop network
approximation error without assigning ranges by hand. It would still inherit
noisy regret estimates and imperfect postflop play, and needs fresh evaluation.
No such variant has been trained, substituted or promoted by this diagnosis.

The diagnostic reconstructs retained observation groups and runs fixed-weight CPU
inference only. Aggregate losses agree with saved CUDA fit losses within 1.1e-8.
All source inputs were rechecked. It neither consumes test outcomes nor tunes the
ongoing experiment. Root targets, predictions, counts and noise estimates are in
`sampled-physical-pilot-fit-diagnosis-v1-result.json`.
