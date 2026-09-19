# Existing engine comparison

Frozen before execution, 19 September 2026. No production changes.

Build heads-up SB/BB push-fold-only trees in the existing PreflopGpu engine.
Posts are 1 and 2 in the engine's chip units; stacks 3, 10, 50, 200. No rake,
limps or non-all-in raises. Balanced symmetric cached equities match the small
reference. Export average policies, CPU and GPU gaps/values after 1,000 and
10,000 iterations. These are offline five-node games, not timing benchmarks.

For each policy, independently reconstruct its values and best-response gap in
the independent-class game and the physically compatible hole-card game. Add
the SB's sunk post of 1 to the native root EV to match the reference's fold-zero
utility convention. Compute separate primal/dual solutions for both games.

Expected accounting checks: independent reference reproduces native average
values and the summed best-response gap within 0.0001 chip; LP dual errors
below 0.000001. No required size or sign for the model difference. Do not tune
fixtures after seeing results. Uniform ranges may hide a large conditional
error in a rare branch; this test does not replace the saved-range audit.

The runner checks production idle, hashes code/input/binary, and refuses to
overwrite results. No deployment or inference about full-tree speed follows.
