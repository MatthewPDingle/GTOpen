# Regret matching+ convergence screen

Registered before learning runs, conditional on RM_PLUS_PLAN numerical tests.
Fresh six-player, 23,038-node six-solver.json; calibrated HU fit pinned;
canonical coupled_deck_v1. Every player learning, no overrides or locks.
No changes to payoffs, ranges, samples used by validation, or local gates.

Serial cases, all with explicit seed, same executable and recorded file hashes:
1. Existing normalized-pair gamma15 control, 64 samples, seed 42.
2. Native-payoff RM+, full 1024 samples, seed 42, no pair correction.
3. Native-payoff RM+, pair-corrected 64 samples, seed 42.
4. Native-payoff RM+, pair-corrected 64 samples, seed 314159.
5. Existing normalized-pair gamma15 control, 64 samples, seed 314159.

Each case stops at 3000 iterations or two consecutive combined passes. Check
every 25 iterations with full 1024-particle global gap <= 0.005 bb and all six
fixed exploration-diagnostic-paths passing the existing per-hand conditional
gate. Unreachable paths do not qualify. No edits to gates after observation.
Process cap 300 seconds per run and 60 seconds per independent saved audit.
Every checkpoint and final saved audit independently recomputed; controls must
exactly replay prior normalized-pair-tail trajectories. Include setup, checks,
and save validation in complete elapsed time. A slower failed solve is not a
qualified speed comparison. Save all rejected evidence.

Exploratory large admission: either full-particle candidate qualifies within
the cap, or BOTH sampled candidates qualify with complete time <= 2x their
matched controls. This only authorizes a separately registered large test;
it is not the final large performance target. The full-particle branch can
establish algorithm viability even if noisy updates fail. Reject a branch
that fails these gates; do not extend its budget or tune on these seeds.
Port 56708 read-only busy guard remains active throughout. Hardware workloads
run singly. No deployment or alteration of CPU performance paths.
