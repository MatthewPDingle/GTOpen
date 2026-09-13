# Predictive RM+ convergence screen

Registered after numerical tests and exact-tree storage passed, before learning
results. Same fresh six-solver.json (23,038 nodes, six learning players), pinned
calibrated fit and equity table, coupled_deck_v1, no locks/overrides/hero.
Read-only busy guard on 56708; hardware work serial. No production changes.

Cases in order:
1. Normalized-pair gamma15 control, 64 samples, seed 42.
2. Predictive RM+, full 1024 samples, seed 42.
3. Prediction-disabled RM+ control, full 1024 samples, seed 42.
4. Predictive RM+ with pair-corrected 64 samples, seed 42.
5. Predictive RM+ with pair-corrected 64 samples, seed 314159.
6. Normalized-pair gamma15 control, 64 samples, seed 314159.

Predictive and zero-prediction controls have identical quadratic averaging,
retained selected-policy timing, update kernels and storage; only loaded
terminal predictions differ. They are not expected to replay the earlier
linear-average/native-policy RM+ screen. Other players use their most recently
selected policy. Numerical validation defines the update order explicitly.
Normalized-pair controls must still exactly replay prior trajectories/saves.

Cap 3000 iterations per case, 450 seconds for full particles and 250 seconds
for sampled cases; independent saved audit 60 seconds. Check every 25 iterations
with full 1024 canonical global gap <=0.005 bb and ALL six fixed conditional
paths passing the unchanged per-hand gate on TWO consecutive checkpoints.
No unreachable path passes. No extra iterations, tuning seeds or gate changes.
Archive all checkpoints, exact arena roundtrip and independent saved audits.
Complete time includes setup, quality checks and save validation; accuracy
failure cannot be presented as an equal-quality speed comparison.

Exploratory large admission: full-particle predictive case qualifies, and is
no slower than the prediction-disabled case if that case also qualifies; OR
both sampled predictive cases qualify within 2x their matched normalized-pair
controls. Any large experiment still needs separate registration and both
large accuracy requirements. This screen cannot establish a large speedup.
Both compatibility suites must pass before publication. No predictive save is
an ordinary resumable session: predictions are transient research state.
