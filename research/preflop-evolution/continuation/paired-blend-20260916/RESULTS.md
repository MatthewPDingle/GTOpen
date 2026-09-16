# Paired blend training-family screen (N34)

All 26 full-N15 held-out errors reproduced within 1e-9. All paired endpoint and
blend pot-conservation checks passed without centering. Frozen inputs remained
unchanged. CPU fitting completed before N32's GPU work.

| Learned share | Mean family MAE (% pot) | Improvement over paired Balanced | Weakest family improvement | Error relative to full N15 |
|---:|---:|---:|---:|---:|
| 0% | 14.9455 | 0% | 0% | 2.3784x |
| 12.5% | 13.2785 | 11.15% | 10.22% | 2.1132x |
| 25% | 11.7853 | 21.14% | 19.64% | 1.8755x |
| 50% | 9.1552 | 38.74% | 33.82% | 1.4570x |
| 100% | 6.2837 | 57.96% | 36.84% | 1.0000x |

The preregistered smallest qualifying strength is **25%**. It sacrifices accuracy
relative to full N15 deliberately; this is not a better standalone predictor or
a pass of N15's distinct selection gate. No evaluation labels were read.

Next test: a separate GPU blend, exact frozen-policy linearity checks against
the two endpoint kernels, then a bounded same-start settling comparison. New
reference accuracy and end-to-end runtime qualification remain necessary. The
inference still evaluates the neural model, so no speed benefit is assumed.
