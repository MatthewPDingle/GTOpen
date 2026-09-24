# Root-retained policy: exact endpoint findings

The fixed 78-update trial completed and its independent training reconstruction
passed. The exact all-in checks show smaller remaining profitable deviations
for the preselected linear/linear policy than the prior exact-initial pilot.
This is encouraging evidence in a restricted test, not proof of accurate
calling ranges or a deployable general preflop model.

## Preselected comparison

Gains are bb per entry to the fixed BB-versus-BTN 2 bb-open, 200 bb context,
with 5% rake capped at 2 bb and the registered incoming ranges. Lower is better.
Both the old and new profile use all 78 played generations with linear weights;
the unplayed final generation 78 is excluded. These are finite-population
endpoint calculations, not sampled confidence intervals.

| Player | Prior pilot gain | Root-retained gain | Reduction |
| --- | ---: | ---: | ---: |
| BB | 0.013793494 | 0.007994039 | 42.0% |
| BTN | 0.013539927 | 0.010040248 | 25.8% |

For BB, the test only reallocates the policy's existing fold/jam probability
between those two actions, preserving its call/raise probabilities and later
play. BTN's test replaces its response to that initial jam. These are different
restricted opportunities for the two players, not a full best-response gap.
The eligible action mass and opponent policy also change between profiles;
this comparison does not isolate a universally better decision rule or prove
robustness to a different training seed.

## All registered averaging pairings

Every pairing is reported; none was selected after seeing its result. The
broader call/raise test still uses the preselected linear/linear policy.

| BB averaging / BTN averaging | BB gain | BTN gain |
| --- | ---: | ---: |
| equal/equal | 0.074293866 | 0.017245660 |
| equal/linear | 0.074823422 | 0.002504435 |
| linear/equal | 0.005367388 | 0.018745897 |
| linear/linear | 0.007994039 | 0.010040248 |

## Verification and next step

The full CPU/CUDA policy checks passed. Independent scalar readback reconstructed
all four pairings over the 47,478 canonical private-card cases representing
776,650 physical pairs, using the existing complete all-in runout cache.
Maximum scalar discrepancy was 2.88e-16 bb;
maximum chip-accounting conservation discrepancy was
1.42e-14 bb.

The separate wider evaluation has not completed. After the candidate-specific
numerical/storage admission and a fresh global storage check, it will train a
new class response on 43,264 deals and test six fixed alternatives on 131,072
independent deals. Its independent readback is required before interpreting
calling/raising weaknesses. Keep unfavorable results and all uncertainty
intervals; do not change the registered sample or select an averaging schedule.

No production deployment follows from the endpoint result. Other positions,
stack depths, sizes and multiway play remain unvalidated.

## Wider-evaluation admission

The complete 78-model numerical control passed on 64 independent control
deals. It checked 29,027 observations across all four
streets, including 28,774 rows with prior actions.
Maximum CPU/CUDA policy discrepancy was
2.49e-13; reach discrepancy was
1.77e-11; payoff discrepancy was
2.13e-14 bb.

The one-batch output projection, including a 50% margin, is 112.45 GB logical
and 43.24 GB allocated, within the registered 120 GB logical and 46.09 GB
allocated caps. Extrapolated batch time is about 5.4 hours for evaluation,
excluding its independent readback and startup. One batch is not a timing
or storage guarantee; runtime limits remain in force. The study is being
launched through the separate global 800 GB storage gate, which remeasures
all three research roots before permitting the full run.

These checks establish compatibility and resource admission, not strategic
accuracy. The evaluation's fixed samples and stopping rules are unchanged.

## Evidence

- Exact registration SHA-256: `bddd724c836090bca25ef8e9cdaffb1cd973b0974cdb78dcaa4f7fd1bd264f42`.
- Exact result SHA-256: `b44e9b076340b8e34b0ff55d3fec358e7f3fad445a14f45f4f10769d96d5d768`.
- Independent review SHA-256: `97cb5ed8350fe571cbc554db9e3a4b6d5fde2d375ab7c407374a7749a0128e29`.
- Training review: `root-retained-fresh-pilot-v1-independent-review.json`.
- Broader protocol: [ROOT-RETAINED-WIDER-TEST-PLAN.md](ROOT-RETAINED-WIDER-TEST-PLAN.md).
