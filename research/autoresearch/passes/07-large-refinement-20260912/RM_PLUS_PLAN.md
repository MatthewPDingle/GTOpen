# Fresh GPU regret matching+ baseline

Registered before execution. Research only; port 56708 and production defaults
remain unchanged. This is a baseline for changing the regret minimizer, not an
implementation of predictive CFR+ or a claim about multiplayer convergence.

Algorithm: native alternating traverser sweeps and native counterfactual payoff
increments. After each traverser's complete observed update, clip that actor's
learning-node cumulative regrets to max(0, R). No clipping of forced/frozen
nodes, no opponent-reach division, and no regret discount. At the end of full
iteration t, multiply non-frozen average accumulators by t/(t+1). With ordinary
unit-weight accumulation this gives iteration k weight k/(T+1) at final T,
equivalent to linear averaging after normalization. No averaging delay.
Only admit iteration-zero engines whose learning-node histories are zero.
Optional pair estimator must be configured before admission. Native average
and BR evaluation bypass clipping and use all 1024 canonical particles.
Added persistent device arrays: zero. One extra clipping kernel per traverser.

Numerical prerequisites (600 seconds each, serial): compare against independent
host clipping after native sweeps and explicit host linear weighting across
four alternating iterations; cover full 1024 and pair-corrected 64 particles,
raw and calibrated HU, frozen seat and point lock. Compare every regret and
average entry, eager versus captured execution, read-only evaluation, native
GPU and CPU reference gaps/EVs (0.005 bb tolerance). Invalid/repeated/admission
after learning, nonzero learning histories and incompatible modes must reject.
Run native GPU equivalence and default release solver suites before publishing.

Learning screen will be registered separately after these prerequisites pass.
No large-game or speed acceptance follows from these arithmetic tests.
