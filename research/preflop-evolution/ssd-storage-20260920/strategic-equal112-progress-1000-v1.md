# Root range comparison

Root action policies only, standardized to the same two-live-player entry prior. Distances do not establish strategic quality. Later-node arrival frequencies and heldout EV/deviation require separate accounting. Earlier folds remain omitted.

| Source | Fold | Call 18 | 4-bet 45 | All-in 200 |
|---|---:|---:|---:|---:|
| equal500 | 72.797% | 8.957% | 11.417% | 6.829% |
| equal1000 | 73.151% | 8.545% | 11.502% | 6.802% |
| weighted1000 | 75.477% | 6.344% | 12.429% | 5.750% |

Policy distance measures how much action probability changes for the same physical hands. It is not an EV loss or an accuracy score.

- equal500 → equal1000: 0.602% prior-weighted root policy distance.
- equal500 → weighted1000: 6.117% prior-weighted root policy distance.
- equal1000 → weighted1000: 5.905% prior-weighted root policy distance.

Source iterations and training-panel gaps are retained in the JSON evidence. Different training-panel gaps are not directly comparable quality scores.
