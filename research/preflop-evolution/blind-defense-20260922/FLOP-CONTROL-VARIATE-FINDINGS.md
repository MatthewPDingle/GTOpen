# Flop rank controls: no useful improvement in this diagnostic

Do not add this eight-feature candidate to the learner. The frozen-policy archived test did not produce a useful consistent reduction in variability. Call-minus-raise comparisons became slightly noisier for every bank. This is a negative result for this feature set, coefficient estimator and sample size, not a rejection of control variates generally.

## Completed comparison

Reused all 65,536 previously inspected deals and all four fixed self-play banks. Eight flop-rank indicators were centered by their exact expectations conditional on both physical private hands. Each class and bank used ridge coefficients fitted only on the opposite global-index parity half, with a fixed penalty of 1. The implementation and split were specified before running this diagnostic. No feature search or coefficient tuning followed the result.

Every exact feature expectation passed exhaustive enumeration of 17,296 possible flops for each of five fixed private-card fixtures. This establishes arithmetic on those fixtures, not an effectiveness result. The archived test then compared class variances, weighted by the original incoming class masses.

A ratio below 1 means lower descriptive variance; above 1 means higher variance. This is the ratio of weighted class variances, not an average of per-class ratios and not an end-to-end speedup.

| Bank | Call - fold | Raise - fold | Raise - call |
| --- | ---: | ---: | ---: |
| first-old | 1.0054 | 0.9889 | 1.0073 |
| first-new | 1.0078 | 0.9956 | 1.0166 |
| repeat-old | 0.9985 | 0.9945 | 1.0074 |
| repeat-new | 0.9984 | 0.9889 | 1.0106 |

Call-minus-fold variance barely changed. Raise-minus-fold variance fell only about 0.4–1.1%. Raise-minus-call variance increased about 0.7–1.7%. These small, mixed changes do not justify a fresh training trial for this candidate.

## Readback and scope

The separate reader authenticated and reconstructed all 65,536 centered feature rows from the original cards. It reconstructed coefficients using augmented least squares rather than the fitting routine's normal-equation solver, then recomputed means, variances and aggregate ratios with scalar sums. Maximum coefficient discrepancy: 5.28e-13; maximum moment discrepancy: 2.96e-12. The main diagnostic took 261.5 seconds including storage admission; readback took 108.0 seconds. Retained array storage is 4.45 MB, plus compact metadata.

Cross-fitted residuals share fitted coefficients, so ordinary independent-sample confidence guarantees do not apply. All outcomes were previously inspected; no confirmatory test was extended. Simulated opponent cards were used only to center training-target controls, never added to a player's observation or policy inputs. No production files or trained policies changed.

## Next direction

Investigate a stronger exact-mean control before expanding training: the actual five-card showdown result minus its exact expectation conditional on the two private hands. Unlike these coarse flop indicators, it sees how the entire board favors either hand. The authenticated conditional batches already retain exact win/tie/loss counts over all 1,712,304 compatible five-card boards, so this proposal would not require repeating that expensive enumeration.

The remaining prerequisite is a checked, isolated way to obtain the sampled board's showdown result, followed by the same fixed, opposite-half fitting protocol. Its practical variance reduction is untested. Any useful result would still need a fresh training experiment and an independent evaluation before it could justify different preflop ranges.
