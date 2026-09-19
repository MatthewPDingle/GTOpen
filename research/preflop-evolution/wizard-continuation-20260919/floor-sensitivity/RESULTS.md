# Probe-weight sensitivity result

All 80 references passed both global convergence checks and the 0.05bb OOP
probe best-response diagnostic. The independent decoded-data audit reconstructed
range means within 0.00000000000002bb. See `validation.json`.

Raising AA, KQo, 55 and 76s from weight 0.001 to 0.01 added 0.2857% of the
prepared OOP combination mass. Other hand weights, the opponent range, boards,
and betting trees were unchanged. The paired changes in gross values are:

| Hand | 50% menu change (bb) | 75% menu change (bb) |
|---|---:|---:|
| AA | -0.629 | -0.489 |
| A5s | +0.014 | +0.006 |
| KQo | -0.130 | -0.147 |
| QJs | +0.003 | +0.000 |
| 99 | +0.003 | +0.003 |
| 88 | -0.003 | -0.016 |
| 55 | -0.139 | -0.056 |
| 76s | -0.232 | -0.105 |

AA's changes have paired 95% board-bootstrap intervals of [-0.803, -0.476]bb
and [-0.886, -0.229]bb. They are small relative to the original 33.7-36.0bb
gap against the fast model. Thus the large gap survives this specific tenfold
probe-weight change. It does not establish robustness to substantially wider
calling ranges or to a new preflop equilibrium.

Full estimates and intervals for all probes are in `summary.json`; numerical
inputs and immutable hashes are in `manifest.json`. The independent called
4-bet branch is the next queued test. No model or production changes were made.
