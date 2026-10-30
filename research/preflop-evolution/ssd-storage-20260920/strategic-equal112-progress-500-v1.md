# Root range comparison

Root action policies only, standardized to the same two-live-player entry prior. Distances do not establish strategic quality. Later-node arrival frequencies and heldout EV/deviation require separate accounting. Earlier folds remain omitted.

| Source | Fold | Call 18 | 4-bet 45 | All-in 200 |
|---|---:|---:|---:|---:|
| equal100 | 72.307% | 10.882% | 12.345% | 4.465% |
| equal500 | 72.797% | 8.957% | 11.417% | 6.829% |
| weighted500 | 75.261% | 6.638% | 12.364% | 5.737% |

Policy distance measures how much action probability changes for the same physical hands. It is not an EV loss or an accuracy score.

- equal100 → equal500: 6.564% prior-weighted root policy distance.
- equal100 → weighted500: 8.613% prior-weighted root policy distance.
- equal500 → weighted500: 6.129% prior-weighted root policy distance.

Source iterations and training-panel gaps are retained in the JSON evidence. Different training-panel gaps are not directly comparable quality scores.
