# Normalized pair-corrected GPU learning: combined-quality screen

Registered before learning runs. The fixed-state conditional pair screen
passed all three cases with decision-regret variance ratios 0.2951–0.3098.
That warrants testing an explicit, separately validated combination of the
existing normalized regret update and pair correction. No coefficient tuning,
exploration, branch copying, payoff changes or production deployment.

Fresh 23,038-node, six-learning-seat fixture from the preceding particle
quality screen; calibrated HU continuation and canonical coupled_deck_v1.
Candidates: 64 and 256 particles, each with pair correction plus normalization,
seeds 42 and 314159. Controls: full 1,024-particle normalization without pair
correction, once per seed (the seed does not alter full-particle draws).
Gamma 15, horizon and cap 1,000 iterations. No history warm start.

Run order: control seed 42; 64 seed 42; 256 seed 314159; control seed 314159;
64 seed 314159; 256 seed 42. One GPU workload at a time, 300-second process
cap per case, GPU base budget 4,096 MiB, pair extra cap 1,024 MiB. Use the
run07 live busy guard and unchanged port 56708.

Every 25 iterations, evaluate the native full-particle global gap, sync, and
audit all six `exploration-diagnostic-paths.json` branches with the existing
independent conditioned evaluator. Stop only after two consecutive checks
with total gap <=0.005 bb and all six conditional paths passing, otherwise
at iteration 1,000. Preserve all per-hand checks. Save/reload exact arenas and
perform a separate saved-game audit. Independently recompute all acceptance
decisions and compare the full-control histories to the prior control.

A candidate qualifies on this small fixture only if both seeds pass combined
quality and each complete wall time (setup, learning, checks and save) is at
least 1.25x faster than its matched full-particle control. A failed control
prevents the speed claim. Do not extend a cap or use an easier stopping rule.
This is not large-game qualification; that remains outstanding.

Before learning, tests must verify corrected regret increments divided by the
actual opponent-prefix mass, unchanged strategy-sum and value behavior for a
single sweep, exact fixed constraints, capture/eager identity, and native
full-reference evaluation. Keep ordinary separate-mode rejection behavior;
only the explicit combined entry point may enable this tested combination.
