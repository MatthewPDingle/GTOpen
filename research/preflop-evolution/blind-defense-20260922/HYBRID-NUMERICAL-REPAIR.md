# Numerical repair of the frozen hybrid evaluation

The original evaluation stopped during its CPU/CUDA agreement controls. Training
and its independent replay remain valid. The failed evaluation, its artifacts,
sources and registration are preserved. No held-out test deals or trained
response had been generated; three 16-deal training batches completed and the
fourth failed. The 256-deal CPU control had completed.

## Identified cause

At training offset 48, two of 7,272 observation rows exceeded the registered
policy tolerance. The maximum averaged-policy difference was 0.038989, with a
maximum checked payoff difference of 0.002776 bb. Preflop differences on that
batch were at most 0.0000001061; the largest difference was on the river.

The diagnostic reconstructs both stored averages exactly, generation by
generation. At the discrepant row, generation 6 had two negative legal scores
whose double-precision difference was only approximately 8.9e-10. Float32 CPU
and batched CUDA arithmetic reversed their ordering. The existing all-negative
fallback chooses the highest score, so this rounding difference changed that
generation from pure call to pure fold. It propagated into the averaged policy.
No tolerance was relaxed and no individual hand was edited.

## Versioned repair and completed controls

Evaluate the same stored float32 weights after exactly widening them to float64.
The network layers, regret-matching/fallback rule, direct preflop tables,
own-reach averaging and played generations 0-77 stay the same. Training is not
repeated. This changes numerical evaluation precision, not the fitted weights;
it can change actions at numerically ambiguous boundaries, as this example
demonstrates. Generation 78 remains unused.

A separate NumPy float64 reference and CUDA float64 bank passed all 256 existing
training-fixture deals and 116,384 observation rows. The maximum policy
difference was 1.33e-15 and checked payoff difference was zero. An independently
computed scalar forward pass at the failing row agreed within 2.23e-16. The
control retained the original 1e-4 policy and 1e-3 bb payoff thresholds.
Independent artifact/arithmetic readback verified all 160 control artifacts.

The control took 132 seconds, including 103 seconds for CPU batches and 14.3
seconds for CUDA batches. These small-fixture timings are not a complete
evaluation speed claim. The existing two-hour evaluation budget is retained.

## Assessment remains fixed

The replacement is `sampled-physical-hybrid-evaluation-v2`, with separate stores,
registration and final review. It keeps the same completed candidate, response
selection rule, 8,192 response-training deals, 16,384 test deals, five comparisons
and statistical error allowance. It reuses reserved seeds 69101/69102 because
the original test stream was never drawn; the repair was chosen from numerical
controls, not poker-strength outcomes. The evaluator's complete sampling,
response-learning and interval loop is unchanged. Fresh controls run again
before test sampling.

After the final audit, compare every hand class with the dense baseline and run
the separately labelled supplementary BTN response diagnosis. These diagnostics
do not alter the candidate or establish a full best-response upper bound.
The dense candidate used float32 evaluation, so descriptive comparisons must
also disclose this precision difference; no paired improvement claim is made.

Any new failure stops the new run with its evidence preserved. Production and
the range preview remain unchanged. No accuracy conclusion follows from this
numerical repair alone.

Evidence: `sampled-physical-hybrid-numerics-v1-{registration,result}.json`,
`sampled-physical-hybrid-precision-control-v1-{registration,result,independent-review}.json`,
and the preserved `sampled-physical-hybrid-evaluation-v1` terminal records.
