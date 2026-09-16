# Targeted continuation-data revision

This offline experiment follows the [probability/value interface study](../learned-interface-20260916/REVIEW.md).
Its accounting checks passed, but the frozen predictor missed the accuracy screen
on two ranges produced by its own preflop decisions. The live application on port
56708 is unchanged.

## Frozen experiment

1. Expand each of those two blind-call cases from 20 to 100 stratified flops.
   Reuse the 40 existing physical solves with explicit provenance and updated
   inclusion weights; generate 160 additional references. These cases are
   development data, not independent validation.
2. Fit exactly one revision using the original 24 training cases plus these two
   cases. Retain the 104-feature shape encoder and ridge penalty 0.1. No model
   selection or hyperparameter search uses the evaluation results.
3. Freeze that predictor before generating 100 evaluation references: 50 fresh
   flops each for `test-seven-straddle-00` and `test-eight-open-01`. Their source
   families remain excluded from fitting. These case identities were evaluated
   historically; the boards are prospective and disjoint from development and
   all earlier study boards. This is not pristine new-context validation.

The evaluation cases were selected from known input features: the deepest
available straddled held-out case and the deepest BB-as-OOP case from the other
held-out family. The fixed point screen requires at least 15% lower weighted
hand-value error than original Balanced **in each case**, with no more than 5%
regression against the previous predictor. Paired stratified bootstrap intervals
are reported. A point pass alone does not establish deployment readiness.

References retain the previous zero-rake heads-up postflop menu: 50%-pot bets,
one 100%-pot raise per street, and no extra all-in action. Both the GPU stopping
criterion and full CPU best-response audit must reach 0.1% of the starting pot.
This is a continuation-value study, not a full-preflop equilibrium or speed test.

## Sampling and provenance

The development set is a nested extension of the previous deterministic
stratified draw: 20 boards in each of five texture strata. Evaluation uses ten
fresh boards in each stratum. Analysis includes suit multiplicity, inverse
inclusion probabilities and compatible hand-pair mass. Earlier excluded boards
are not covered by these estimates; neither sample is claimed to be an unbiased
estimate over every canonical flop.

Original files are immutable. Development manifests record the path and SHA-256
of every reused result. Their physical configurations must match; only the
in-memory analysis sampling weights change. The revised candidate is stored
here separately from the original model. Its freeze record precedes all new
evaluation solves. The runner checks live solve/report activity before each
four-job batch and defers if the application is busy.

## Reproduce or resume

From the repository root, using Python with NumPy and the existing frozen
`target/range-value-reference-night2.exe`:

```powershell
python tools/research/continuation_policy_refinement.py prepare
python tools/research/test_continuation_policy_refinement.py
python tools/research/continuation_policy_refinement.py run
```

`run` resumes completed references, validates their configurations, fits once,
freezes the candidate and then evaluates it. It never calls an application POST
endpoint or rebuilds/restarts the server. `status.json` records progress.
Raw solve outputs retain convergence traces and per-hand best-response quality.
Rare hands can remain less certain despite a small range-average solver gap.
Bootstrap intervals condition on the fitted predictor and cached equities;
they do not include training uncertainty or source-family generalization.

The authoritative pre-outcome specification is [protocol.json](protocol.json).
