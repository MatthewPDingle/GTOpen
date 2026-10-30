# Root range comparison

Root action policies only, standardized to the same two-live-player entry prior. Distances do not establish strategic quality. Later-node arrival frequencies and heldout EV/deviation require separate accounting. Earlier folds remain omitted.

| Source | Fold | Call 18 | 4-bet 45 | All-in 200 |
|---|---:|---:|---:|---:|
| weighted500 | 75.261% | 6.638% | 12.364% | 5.737% |
| weighted1000 | 75.477% | 6.344% | 12.429% | 5.750% |
| weighted1500 | 75.667% | 6.119% | 12.442% | 5.773% |
| weighted2000 | 75.886% | 5.865% | 12.443% | 5.806% |

Policy distance measures how much action probability changes for the same physical hands. It is not an EV loss or an accuracy score.

- weighted500 → weighted1000: 0.522% prior-weighted root policy distance.
- weighted500 → weighted1500: 0.823% prior-weighted root policy distance.
- weighted500 → weighted2000: 1.117% prior-weighted root policy distance.
- weighted1000 → weighted1500: 0.314% prior-weighted root policy distance.
- weighted1000 → weighted2000: 0.614% prior-weighted root policy distance.
- weighted1500 → weighted2000: 0.302% prior-weighted root policy distance.

Source iterations and training-panel gaps are retained in the JSON evidence. Different training-panel gaps are not directly comparable quality scores.
