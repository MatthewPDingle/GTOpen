# Training range diversity: results

**Rejected by the training-family screen. No evaluation labels were generated or used.**

Port 56708 is unchanged. This is an offline continuation-value experiment, not a deployed preflop solver.

## What changed

Added 36 synthetic training contexts between concentrated and broad ranges from four existing training families. Each pair is tested at stack-to-pot ratios 4, 10 and 16, using 20 new stratified flops. These are controlled training examples, not measured player profiles. The model retains the same 104 features and ridge penalty 0.1. Original data, new blind-call data and the bridges total 62 fitting cases.

## Training-family screen

Each family is excluded in turn, including its related synthetic and development cases. The eligibility score uses only the unchanged original 24 validation cases. It requires at least 5% lower equal-family mean error and no family more than 5% worse.

| Excluded training family | Original predictor | Expanded training |
|---|---:|---:|
| train-eight-equal | 8.474 | 9.029 |
| train-eight-straddle | 8.374 | 9.992 |
| train-seven-open | 5.407 | 5.914 |
| train-six-modeled | 5.614 | 6.944 |

Mean improvement: **-14.39%**. Worst family error ratio: **1.237**.

Errors are compatible-mass-weighted mean absolute hand-value errors, as a percentage of starting pot. Training-family screening selects a candidate; it does not establish prospective accuracy.

## Reference integrity

| Partition | Audited / planned | Maximum CPU gap (% pot) | Maximum GPU gap (% pot) | Maximum pot-sum error (bb) |
|---|---:|---:|---:|---:|
| training | 720 / 720 | 0.09998 | 0.09994 | 1.62e-06 |
| evaluation | 0 / 400 | 0.00000 | 0.00000 | 0.00e+00 |

Persisted references are checked against their immutable manifests and both numerical stopping gates. Per-hand compatible masses and weighted values must reconcile with aggregates; zero-rake player values must sum to the starting pot. Evaluation outputs must follow the candidate freeze.

All references retain the fixed half-pot postflop menu. Low range-average best-response gaps do not certify every rare-hand label. These value errors do not measure action-frequency accuracy or full-game exploitability. Multiway card-removal approximation, broader bet menus and range evolution remain limitations.

See [frozen protocol](README.md), [training screen](training-screen.json), [reference audit](reference-audit.json) and [status](status.json).
