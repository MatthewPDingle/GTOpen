# Conservation-aware fitting: rejected

All three fixed candidates failed the training-family screen. The best of
them increased mean error from 6.889 to 7.274 percent of pot, a 5.6% regression.
Its worst family was 6.5% worse. No candidate was frozen for evaluation.

| Fit | Penalty | Equal-family MAE (% pot) | Worst family error ratio |
|---|---:|---:|---:|
| Original | 0.1 | 6.889 | 1.000 |
| Projected | 0.03 | 7.637 | 1.208 |
| Projected | 0.1 | 7.309 | 1.101 |
| Projected | 0.3 | 7.274 | 1.065 |

The two numerical tests passed: projected training is algebraically compatible
with the existing inference function, and a synthetic projected linear target
is recovered. Test tolerances allow binary64 summation roundoff; no solver
precision or reference stopping criteria changed.

This negative result means aligning the fitting equation with conservation
did not improve generalization on these four training families. It does not
prove conservation is unimportant. Limited coverage and regularization still
matter. No fresh evaluation labels were inspected and no app code changed.

See [predeclared protocol](README.md), [frozen implementation](implementation-freeze.json)
and [all per-case and per-family results](training-screen.json).
