# Guarded future-card symmetry bridge

Registered before implementation tests on 19 September 2026. Research only.

Hypothesis: changing external preflop reaches preserve the existing flop's
suit group when preflop policies are class symmetric. Future-card orbit
folding can then reduce GPU storage without changing the modeled game.

Implement a restricted GPU wrapper, separate from the arbitrary-reach bridge.
Start from zero F32 CFR+ arenas, iteration zero, no locks, and enabled suit
isomorphism. Keep the GPU private so callers cannot install asymmetric locks
or policies. Every sweep must validate lengths, finite nonnegative entries,
and exact equality under every configured hand permutation for BOTH players.
Reject invalid input before any update. No tolerance or approximate merging.
Synchronizing results must target the original Spot. No public fixed-range
GPU exploitability method is exposed by this wrapper.

## Tests and acceptance

- Compare two-tone, monotone and rainbow flop fixtures under changing
  class-dependent external reaches, including zero own reach. Use identical
  starting states for one-sweep comparisons against uncompressed CPU/GPU.
- Maximum counterfactual-value discrepancy per unit opposing mass <0.002 bb;
  immediate root-average discrepancy <0.002. Report actual maxima.
- Independently run compressed and uncompressed GPU trajectories for 100
  iterations; report root policy drift and normalized average/BR value errors.
  Require root strategy difference <0.01 and value difference <0.002 bb for
  this fixture. A failure is investigated and retained, not silently loosened.
- Force compact F32 allocation with the existing planner's compact budget;
  report actual device arena lengths and require reduction where orbits exist.
- Reject asymmetric own and opposing reaches separately; zero/tiny reaches
  must not bypass symmetry checks. Reject locks, warm or nonzero arenas, NaN,
  negative inputs, invalid player/iteration, and mismatched sync targets.
- Run existing continuation-bridge and postflop GPU equivalence tests.

After these tests, preregister a connected-game comparison with the frozen
uncompressed reference. Do not use any reserved strategic validation case.
Check production 56708 is idle before GPU work and monitor it during tests.
This wrapper alone is not evidence of improved preflop accuracy.
