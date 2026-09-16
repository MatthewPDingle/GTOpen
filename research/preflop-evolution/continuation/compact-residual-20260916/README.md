# N18: half-width nonlinear correction

Preregistered while N15 fresh-reference generation is running, before its final
accuracy result is available. This hypothesis targets inference cost: replace
N15's two eight-unit networks with two four-unit networks. Keep the original
104-feature ridge base, output penalty 0.1, shrinkage 0.75, seeds 90210/20260916,
500 Adam steps at 0.01, float64 and original one-thread BLAS/two-thread Torch.
No grid or follow-up tuning is part of N18.

Fit on the original 26 training/development contexts only. Exclude each entire
source family in turn. Compare per-case scores against the frozen N15 training
screen and its original linear control. Keep a candidate only if:

- Mean family error improves at least 5% versus the linear control.
- No family is more than 5% worse than that control.
- Mean error and every family's error are at most 5% worse than N15.

The last limit is a maximum allowed training-screen regression for a proposed
cost reduction, not a claim that the smaller model is more accurate. Its final
accuracy and speed still need independent measurement. N15's fresh evaluation
outcomes, N09's outcomes and all other held-out labels must not enter fitting or
selection. Record input hashes before fitting and freeze the winner before
generating a separate, newly reserved 400-reference evaluation if eligible.
Do not reuse already generated N15 evaluation labels to qualify this candidate.

Use the same independent fresh gate: >=15% mean improvement versus Balanced in
each held-out family and no case >10% worse than the old conditional predictor.
GPU implementation, physical-hand oracle, repeated <=10% runtime overhead and
changed-policy validation remain necessary. No production changes or deployment.
CPU fitting is allowed during reference generation, never during GPU timings.
The fixed 20:49:02 UTC deadline applies.
