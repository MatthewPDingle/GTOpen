# Training-only coverage diagnostic

The completed conditional-target probe fitted exact training answers closely
(MSE 3.312 bb squared) but had much larger held-out error (4088.710). Its
registered integration gate failed because exact targets increased decision
cost against bank A relative to 16 samples. Do not deploy, integrate the
regressor, change that gate, or tune on the 32 evaluated final deals.

This next small diagnostic uses only the original 64 TRAINING deals. It asks
whether adding distinct training deals helps the unchanged network generalize
within that development pool. It is exploratory, not fresh confirmation.

## Fixed design

- Order deal indices 0-63 by SHA256 of `9289941|deal_index`.
- First 48 are candidate fit deals; final 16 are development validation.
- Fit nested prefixes of 8, 16, 32 and 48 deals, using every previously selected
  state of each deal. Keep both banks and both actors separate.
- Use exact conditional targets only. Reuse the original visible 302 inputs,
  64/64 network, output1-minus-output0 contrast, scale 400.5, full-batch Adam
  0.003 and exactly 512 steps.
- Use three fresh paired initializations: 9289951, 9289952 and 9289953. The same
  seed initializes each prefix model; do not warm-start the larger models.
- Freeze this design before fitting. There are 48 fits in total. No model or
  feature choice is selected from the original 32 final evaluation deals.
- Retain weights and development predictions. Report training and development
  MSE, local two-action decision cost, direction agreement and signed bias for
  all banks, actors, repetitions and sample counts. Plot the aggregate learning
  curves with all three repetition means; no confidence claim.

## Checks, interpretation and limits

Revalidate the qualified contrast-training control and input hashes. Verify the
nested deal sets, disjoint validation set, fixed number of examples per actor,
and exclusion of every original evaluation deal. Independently reconstruct
final predictions in NumPy and Torch CPU double precision, and decision costs
with scalar arithmetic. Preserve failure evidence; never overwrite a fit.

A falling development error with more deals would support broader coverage as
a useful next direction, but 48 deals cannot establish a scaling law. A flat
curve would motivate representation or regularization controls. In either
case, the substantial training-to-validation gap must be reported. No change
to self-play or production is qualified by this diagnostic. Any later candidate
needs separately frozen settings and new final evaluation deals.

The work reuses the existing dataset, adds no native collection, and is capped
at five minutes of computation and 20 MB of new artifacts within the existing
2 GB study directory limit and 800 GB global storage ceiling. Use one GPU
research owner and the existing 4 GB/2 GB headroom guard. Light desktop sharing
continues; production solves and heavy workloads take priority.
