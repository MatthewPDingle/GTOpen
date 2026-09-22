# Where the previous network's retained-data error remains

This diagnostic reads generation 77 of the **completed dense conditional-all-in
trial**. It is the last played network in that candidate's 78-generation average.
It does not inspect or change the currently running combined trial. It is a
training-fit diagnostic of one component, not a held-out policy evaluation.

The original count-weighted fitting loss was reconstructed using CPU float64
inference of the stored float32 weights. Differences from logged CUDA fitting
losses were 6.97e-8 for BB and 6.72e-9 for BTN. All retained observations were
included, with legal-action masks and the original normalization scale.

| Share of total fitting error | BB | BTN |
|---|---:|---:|
| Preflop | 0.12% | 0.15% |
| Flop | 8.75% | 21.19% |
| Turn | 28.70% | 37.39% |
| River | 62.43% | 41.27% |

The 512-step fit reduced overall normalized loss from 1.6620 to 1.1751 for BB
and from 1.5250 to 0.9235 for BTN. The remaining error is overwhelmingly in
postflop targets. This combines their greater representation in the reservoir
with much larger per-target residuals; it is not an equal-weight street test.

## Sparse observations limit what this establishes

BB retained 143,199 river visits spanning **143,199 distinct information sets**.
BTN retained 45,527 spanning **45,527 distinct information sets**. Turn visits
were also almost entirely distinct; flop repeats were scarce. Zero measured
within-information-set variance on the river consequently says nothing about
the underlying target noise: there is only one retained observation per key.
Hidden opponent cards, sampled runouts and changing historical policies can
all contribute to target noise. Residual training loss cannot be equated with
incorrect true values, and these results cannot separate representation limits,
optimizer limits and sampling variance by themselves.

## Small preflop score errors can still change decisions

Despite preflop's tiny contribution to squared loss, the network's regret-matched
policy differs substantially from regret matching on the retained empirical
means: retained-visit-weighted total variation is 0.3885 for BB and 0.3606 for BTN.
This measures disagreement with those empirical means, not with an equilibrium
or an independently known correct strategy. Regret matching can amplify small
score errors around zero and close action comparisons.

That supports testing the direct preflop tables already used in the running
combined candidate. It also explains why an improvement in overall regression
loss alone would not establish better ranges.

## Implication for the next controlled experiment

Keep the current combined trial fixed and finish its independent evaluations.
The prepared visible-board summaries are a defensible next representation test:
they explicitly describe made hands and rank/suit patterns without adding hidden
information. Compare them with the original representation under matched
initialization, fitting budget and new held-out evaluation. Do not call them a
fix before testing, overfit inspected individual hands, or replace the complete
played average with a selected late network.

Evidence: `sampled-physical-allin-fit-error-diagnostic-v1-registration.json` and
`sampled-physical-allin-fit-error-diagnostic-v1-result.json`. No model was fitted,
no new chance data was drawn, no GPU job was added, and production was unchanged.
