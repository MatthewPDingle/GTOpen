# Own-range value response (N26)

Training-input descriptive response only; no labels, fitting, accuracy or causal/convergence proof.

Two numerical checks passed. All432 prescribed mixtures completed; raw and Balanced own-hand values stayed unchanged within1e-12 in every case.

Values below are percentage points of pot per one percentage point of actual range TV. Signed changes are averaged over the original compatible hand mass before taking their absolute magnitude. This avoids mistaking positive/negative cancellation for unchanged hand values.

| Mixture amount | Model | Median signed own response magnitude | 95th percentile | Median absolute own response |
|---|---|---:|---:|---:|
| 0.100% | candidate | 0.3009 | 1.0891 | 0.4268 |
| 0.100% | linear_base | 0.2959 | 0.9093 | 0.3682 |
| 0.100% | balanced | 0.0000 | 0.0000 | 0.0000 |
| 0.100% | raw | 0.0000 | 0.0000 | 0.0000 |
| 0.010% | candidate | 0.3940 | 1.2450 | 0.5042 |
| 0.010% | linear_base | 0.4058 | 1.0357 | 0.4348 |
| 0.010% | balanced | 0.0000 | 0.0000 | 0.0000 |
| 0.010% | raw | 0.0000 | 0.0000 | 0.0000 |
| 0.001% | candidate | 0.4806 | 1.4177 | 0.5624 |
| 0.001% | linear_base | 0.4946 | 1.2101 | 0.5133 |
| 0.001% | balanced | 0.0000 | 0.0000 | 0.0000 |
| 0.001% | raw | 0.0000 | 0.0000 | 0.0000 |

The nonlinear candidate and its older linear base both show systematic shifts of existing hand values when only their own input range changes. This is therefore not unique to the added neural correction. Responses grow as the mixture size shrinks; many original distributions have zero-weight hands, and the encoders include entropy and clipping, so these finite differences should not be presented as a stable smooth derivative.

Own-range dependence can be legitimate. This label-free diagnostic does not tell us which shifts are accurate or prove the cause of the solve gap. Together with N24, it motivates testing value-vector consistency inside a small exact-chance heads-up game before expanding the model further. No predictor, gate or production setting changed.
