# Matched small-game accumulated-opponent screen

Registered after both numerical tests passed and the forced-age large averaging
diagnostic was independently verified. Averaging alone failed; nine of the
27 checked paths had zero current opponent reach in both large saved states.

Use the existing fresh 23,038-node six-learning-seat calibrated fixture,
canonical coupled_deck_v1, gamma15, horizon 1,000, 64 particles and unchanged
normalized pair correction. Compare the accumulated-opponent extension off/on.
No other optimizer, policy seeding, exploration, payoff changes or tuning.
Pin/hash calibration and equity inputs explicitly.

Run serially with one binary: control seed 42, candidate seed 42, candidate
seed 314159, control seed 314159. Each case has a 3,000-iteration/300-second cap.
Every 25 iterations use native full-1,024 global gaps and the same six
historical conditional paths. Stop only at two consecutive combined passes:
gap <=0.005 bb and all six conditional checks. Save/reload exact histories and
independently audit each final saved policy. Retain all failures.

Controls must exactly reproduce the corresponding earlier normalized-pair-tail
per-hand checkpoint trajectories, discount age, stop decision and saved file
hash. Both candidates must qualify and cost at most twice their matched control
in complete example runtime before any exploratory large test is admitted.
This bounded overhead permits testing a different large-game learning target;
it is not a speedup or deployment criterion. Report actual equal-quality timing
ratios and keep all existing four-seed small-game qualification separate.

Before this screen, run normalized-regret, exploration, pair-control and native
postflop/preflop GPU equivalence tests with the new extension disabled. If a
candidate fails the registered gate, do not tune its cap, seeds or averaging
exponent in place and do not run a large candidate. Any later diagnostic needs
its own explicit purpose. Port 56708 stays untouched; no CPU speed work.
