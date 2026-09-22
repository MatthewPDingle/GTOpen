# Reducing all-in outcome noise during evaluation

The separate conditional preflop-all-in evaluator passed its fixed-policy
control. It replaces a sampled board's all-in winner with the exact average
over all 1,712,304 possible boards for the sampled four private cards. It changes
only terminals reached all-in before the flop. Postflop policies still see only
their visible information, and their outcomes still use the sampled board.

For fixed preflop policies this preserves the expected payoff: the chance board
is independent of decisions made before it appears. It does not provide either
player with the other player's cards. Private-pair equity is used to value a
terminal, not as a policy input. The existing audited exact-count cache supplies
the labels. No cache or policy was refitted for this control.

## Verified fixture result

Six fixed synthetic profiles were evaluated on 16 old training private pairs,
with 16 new diagnostic runouts per pair: 1,536 profile/deal comparisons. A
separate Python preflop path calculation reproduced both players' conditional
values from the original evaluator's outputs and the expected-minus-realized
all-in cashflow. Maximum discrepancy was 2.84e-14 bb. Expected rake and terminal
mass were unchanged; root-fold and root-call fixtures were exactly unchanged.

The native evaluator also compares reverse expectation with forward actual-
investment accounting and checks chip conservation. Six malformed transports
were rejected, including wrong private-card binding and invalid board counts.

| Synthetic profile | Conditional / sampled within-private-pair BB payoff variance |
|---|---:|
| Uniform | 0.0121 |
| Root fold | Both zero |
| Root call | 1.0000 |
| Root raise, uniform afterward | 0.0650 |
| Root jam, uniform afterward | 0.0000 |
| Hand-aware synthetic preflop mix | 0.0232 |

These are ratios of sums of sample variances across the 16 pairs, not a
population precision estimate. The pure-jam fixture becomes board-independent
conditional on private cards. The call fixture retains its postflop board noise.
This does not establish lower total paired-deviation variance for learned
policies: replacing one component can change covariance with another component.

A saved-artifact replay checked 127 source/artifact hashes, all 1,536 records,
the chance stream, preflop reach coefficients, correction arithmetic, unchanged
non-all-in paths, and variance summaries. It does not repeat native execution or
the exhaustive equity-cache calculation. During reviewer development, the raw
private-card lookup was corrected to account for canonical suit keys; the
original control and its registered outputs were unchanged.

## Completed learned-bank diagnostic

A separate CPU-only diagnostic applied the same comparison to the completed
78-model hybrid played bank in float64, using these same 256 diagnostic deals.
It measured the four fixed root-action differences against the baseline as well
as the baseline's payoff variance. No responder was fitted and no action was
selected using these outcomes.

| Paired comparison | Conditional / sampled within-private-pair variance |
|---|---:|
| Always fold versus baseline | 0.0264 |
| Always call versus baseline | 0.1092 |
| Always raise versus baseline | 0.0758 |
| Always jam versus baseline | 0.0029 |

Thus board-related variability fell about 89% to 99.7% for these particular
paired comparisons. The standalone baseline-payoff ratio was 0.0264. All 1,280
profile/deal values matched the independent correction calculation to within
5.69e-14 bb; root-policy mixtures also reconstructed. The 265.4-second run used
CPU inference and did not compete for the GPU training lock. Its saved-artifact
audit checked 146 hashes, all records, equal policies/deals, native accounting,
unchanged fold/call paths and independent standard-library variance summaries.

These results justify preparing this estimator for a future evaluation. They
do **not** justify dividing the previous full-population confidence widths or
sample counts by these fixture ratios. Only 16 private pairs were used; variation
between private pairs remains, and the eventual learned responder can choose
different actions. The new fixture means also differ from the sampled means,
as expected with only 16 boards per pair. Neither mean is a new strength result.

## Next step and scope

The active all-in **training** trial and its predeclared held-out evaluation
remain unchanged. Neither this evaluator nor the hybrid policy is deployed in
production or the preview. A future evaluation using this estimator needs its
own frozen protocol, independently selected chance stream and resource budget.
The cost of building exact equity labels for unseen private pairs must be
included; variance reduction is not automatically a wall-clock speedup.

Artifacts: `sampled-physical-allin-evaluation-control-v1-{registration,result,
status,independent-review}.json`; full fixture data are under the same prefix on
`S:/GTOpen-research`. The learned-bank diagnostic has the separate prefix
`sampled-physical-allin-learned-evaluation-control-v1`.
