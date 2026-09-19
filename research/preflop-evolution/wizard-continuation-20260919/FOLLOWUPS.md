# Continuation follow-ups

Both complete 80-board/menu panels passed the specified global and OOP probe convergence checks. These are controlled diagnostics, not deployed models.

## Range-weight sensitivity

Raising the four tiny diagnostic hand weights from 0.001 to 0.01 added 0.2857% to the prepared OOP combination mass. The table gives changes in gross values with paired 95% board-bootstrap intervals.

| Hand | 50% menu change (bb) | 75% menu change (bb) |
|---|---:|---:|
| AA | -0.629 [-0.802, -0.476] | -0.489 [-0.886, -0.229] |
| A5s | +0.014 [+0.004, +0.024] | +0.006 [+0.002, +0.010] |
| KQo | -0.130 [-0.168, -0.090] | -0.147 [-0.209, -0.092] |
| QJs | +0.003 [-0.006, +0.014] | +0.000 [-0.007, +0.007] |
| 99 | +0.003 [-0.010, +0.012] | +0.003 [-0.005, +0.014] |
| 88 | -0.003 [-0.036, +0.019] | -0.016 [-0.045, +0.001] |
| 55 | -0.139 [-0.265, -0.057] | -0.056 [-0.096, -0.023] |
| 76s | -0.232 [-0.385, -0.119] | -0.105 [-0.156, -0.063] |

## Called four-bet branch

UTG raises to 45bb and LJ calls. Pot 93.5bb, stacks 155bb. These values use that branch's own ranges; they are not imported from the smaller call pot.

| Hand | Fast gross value | 50% menu gross value [95% interval] | 75% menu gross value [95% interval] |
|---|---:|---:|---:|
| AA | 76.83 | 83.70 [76.47, 92.41] | 84.07 [76.44, 93.33] |
| A5s | 29.17 | 56.65 [50.89, 62.84] | 53.74 [47.76, 60.19] |
| KQo | 26.35 | 56.58 [48.62, 64.41] | 55.42 [47.94, 62.54] |
| QJs | 28.67 | 56.49 [49.23, 63.91] | 54.17 [46.45, 61.94] |
| 99 | 31.96 | 57.63 [46.94, 69.64] | 55.38 [44.28, 67.86] |
| 88 | 29.32 | 50.90 [41.63, 61.28] | 49.19 [39.61, 60.04] |
| 55 | 28.48 | 50.55 [42.66, 58.88] | 48.11 [40.37, 56.55] |
| 76s | 26.46 | 50.79 [42.69, 59.37] | 48.74 [40.74, 57.49] |

## Relevance to AA's preflop decision

In the saved approximation, AA's 4-bet is worth 40.1196bb and its jam 40.1042bb relative to folding at that decision. LJ calls the 4-bet 41.07% of the time. Holding every response fixed, a 1bb change in AA's value in the called branch changes its 4-bet value by about 0.411bb.

| Menu | Change in 4-bet value (bb) [95% interval] | Hypothetical 4-bet value (bb) |
|---|---:|---:|
| half | +2.82 [-0.15, +6.40] | 42.94 |
| large | +2.97 [-0.16, +6.78] | 43.09 |

This applies only the measured leaf-price difference, including the documented tiny range preparation changes. It is not a re-solve: an actual change to the model would alter opening ranges, 4-betting ranges, and LJ's responses. It therefore cannot establish the final strategy or how much closer the complete game would come to Wizard.

Intervals describe sampled flops within restricted postflop betting trees. They omit range/model uncertainty and finite-sample equity-cache error. The small-floor check does not validate substantial range changes. Future rake and physical card removal also differ from the fast continuation approximation.
