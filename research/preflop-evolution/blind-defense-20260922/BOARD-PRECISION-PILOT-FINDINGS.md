# Board integration: first precision and cost pilot

This fixed-policy pilot supports continuing with board-first root estimates.
Integrating private hands reduced measured action-value noise enough to offset
its higher computation cost. It does **not** establish a faster production
solver, improved ranges, convergence or playing strength.

All registered work completed: 32 uniform boards and 5,408 private-first deals
(32 per hand class), using the same audited arm's played generation-77 policy.
The original chance laws and all 169 classes were retained. Exact fold and
preflop all-in components were common to both methods. Nothing was trained.

## Fixed comparisons

RMS SE is the square root of entry-weighted per-class estimated variance of the
sample mean. It is descriptive; 32 boards do not support a strong uncertainty
claim. Lower values are preferable.

| Comparison | Private-first RMS SE (bb) | Board-first RMS SE (bb) | Board/private variance × work-time ratio |
| --- | ---: | ---: | ---: |
| Raise minus call — primary | 4.088 | 0.956 | 0.094 |
| Call minus fold | 2.805 | 1.073 | 0.252 |
| Raise minus fold | 4.367 | 1.253 | 0.142 |

Thus the measured variance-and-time metric was about 10.6 times better for the
primary comparison, 4.0 times for call/fold and 7.0 times for raise/fold. This
compares these two CPU research estimators, **not** the current GPU trainer's
throughput. It is a one-policy pilot and should be independently repeated.

Board jobs consumed 444.62 summed worker wall-seconds versus 258.19 for private
jobs. With four interleaved workers, total elapsed time was 182.75 seconds,
including common setup and scheduling. There was no GPU use. The main audit
continued in parallel, so these are not isolated benchmark timings.

## Regressions and mean differences

Measured board variance was lower for 168/169 classes in raise/call, 150/169
in call/fold and 164/169 in raise/fold. Those sets represent 99.1%, 88.9% and
97.2% of entry mass respectively. The raise/call exception was 63o. All class
results, including the other regressions, are published in
`board-precision-pilot-v1-all-classes.json`.

Entry-weighted mean differences (board minus private) were -0.430 bb for
raise/call, +0.039 bb for call/fold and -0.391 bb for raise/fold. This does not
prove equal means. Some class discrepancies remain large: AA's raise/call
estimate differs by 18.13 bb (about 3.24 descriptive combined SE), and 93o's
raise/fold differs by -8.68 bb (about -4.17 descriptive combined SE). Rare,
high-payoff continuations and noisy variance estimates make larger independent
samples necessary. Shared boards also correlate errors between classes; the
169 classes must not be treated as independent replications.

## Evidence and next decision

The review verifies all 117 jobs, source hashes, all chance-stream allocations,
full supported board ranges, 340 retained private transport artifacts, and
all native private value rows. Separate scalar moment reductions agree with
NumPy for every class and comparison. Prior controls compare the two value
paths against forward cashflow arithmetic. The pilot review does not re-run
every board or independently re-solve the game.

Next: register a larger independent repeat with the same fixed policy and
comparisons, new seeds, and more samples per class. Inspect both precision and
mean discrepancies before considering root-target training changes. Do not
extend or reclassify this completed pilot after seeing its results. The
existing stratified study's evaluation remains the priority.

Artifacts: `board-precision-pilot-v1-registration.json`,
`board-precision-pilot-v1-result.json`, `board-precision-pilot-v1-review.json`,
and the complete all-class table. Source plan: `BOARD-PRECISION-PILOT-PLAN.md`.
