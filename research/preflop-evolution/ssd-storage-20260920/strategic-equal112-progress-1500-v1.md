# Root range comparison

Root action policies only, standardized to the same two-live-player entry prior. Distances do not establish strategic quality. Later-node arrival frequencies and heldout EV/deviation require separate accounting. Earlier folds remain omitted.

| Source | Fold | Call 18 | 4-bet 45 | All-in 200 |
|---|---:|---:|---:|---:|
| equal1000 | 73.151% | 8.545% | 11.502% | 6.802% |
| equal1500 | 73.206% | 8.485% | 11.520% | 6.790% |
| weighted1500 | 75.667% | 6.119% | 12.442% | 5.773% |

Policy distance measures how much action probability changes for the same physical hands. It is not an EV loss or an accuracy score.

- equal1000 → equal1500: 0.099% prior-weighted root policy distance.
- equal1000 → weighted1500: 5.985% prior-weighted root policy distance.
- equal1500 → weighted1500: 5.941% prior-weighted root policy distance.

Source iterations and training-panel gaps are retained in the JSON evidence. Different training-panel gaps are not directly comparable quality scores.
