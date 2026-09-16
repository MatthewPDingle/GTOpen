# N09: promising training result; prospective evaluation pending

The fixed recalibration passed its training-family screen. Mean error fell
31.8% versus original Balanced and 31.6% versus unchanged priors evaluated
with the same compatible-pair calculation. The worst family was 0.5% worse
than Balanced, within the predefined 5% allowance.

| Excluded training family | Balanced | Unchanged paired priors | Recalibrated priors |
|---|---:|---:|---:|
| Eight-player equal blinds | 22.827 | 22.476 | 14.583 |
| Eight-player straddle | 10.760 | 10.786 | 10.812 |
| Seven-player open | 14.835 | 14.751 | 7.568 |
| Six-player modeled | 11.570 | 11.768 | 7.928 |
| Equal-family mean | 14.998 | 14.945 | 10.223 |

Numbers are compatible-mass-weighted mean absolute hand-value errors as a
percentage of starting pot. This is model selection on the original 26
training cases, excluding whole families. It is not prospective validation.

This simple model is less accurate on these training-family checks than the
104-feature predictor (6.889% mean error). Its reason for consideration is
the possibility of cheaper inference: pairwise share matrices can be cached.
No GPU speed improvement has been measured for it yet.

The full fit is frozen at SHA-256
`7c324ecf383dc24cf9e95024851f9fed7b6b11aad545741f98e0c6a78383eb4b`.
No production cache or live app was changed. The fixed optimization used
600 steps without outcome-based tuning or early stopping.

The candidate is registered before N03's planned evaluation references exist.
The [prospective protocol](evaluation-protocol.md) permits reuse of those
unchanged future references, or identical physical queries in this study's
own directory if N03 skips evaluation. It preserves the N03 accuracy gate.
Independent GPU arithmetic, runtime and changed-policy checks remain necessary.

See [training scores](training-screen.json), [candidate freeze](candidate-freeze.json)
and [evaluation registration](evaluation-registration.json).
