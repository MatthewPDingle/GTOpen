# Large normalized pair-corrected qualification

Registered after all four fresh small-game seeds passed combined quality at
2.54–4.40x faster complete runtime than the full-particle control. This large
test remains necessary because full-particle normalization failed here and
several selected branches lost current reach.

Fresh 1,567,754-node eight-learning-seat fixture from
`03-preflop-20260910/user-session.json`, calibrated HU continuation and
canonical coupled_deck_v1. Gamma15, horizon 1,000, 64 particles, explicit
normalized pair correction with unchanged coefficient. No exploration,
branch copying, warm start, pruning or altered payoff model.

First run seed 42 to at most 3,000 iterations, 10,800-second guard cap, base
GPU budget 20,000 MiB and extra pair budget 1,024 MiB. Every 50 iterations,
perform the native full-1,024-particle global check and all 27 predeclared
conditioned paths. Stop only after two consecutive checks with gap <=0.005 bb
and all 27 conditional passes, otherwise at the registered iteration cap.
Retain every per-hand checkpoint and report unreachable paths as failures.
Save/reload exact arenas; independently audit the saved final game.

Run seed 314159 only if the first run passes independent combined-quality
verification. It uses the same cap and configuration. A single successful
large run is not multi-seed validation. Any failure is retained; do not
extend a running case, relabel an unqualified result or loosen a gate.

Use one workload and run07's live busy guard; do not change port 56708.
Record configuration, plan, source/executable/input hashes and component
times. The older large full-particle run never qualified, so its runtime
cannot supply an equal-quality speedup claim. This stage first establishes
whether the corrected candidate achieves large-game accuracy at all.
