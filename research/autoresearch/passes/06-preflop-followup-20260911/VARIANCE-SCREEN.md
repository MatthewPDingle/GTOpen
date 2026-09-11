# Registered offline variance screen

This is a synthetic mathematical screen before any GPU control-variate work.
It is not hand-history fitting or a solver speed benchmark. Build/test/run the
research-only `convergence_variance` example after timed hardware work finishes.

Use the existing 1,024 coupled particles and 169 hand classes. Generate fixed
normalized opponent ranges with a smooth strength weighting, then mix each with
a broader range by 0, 1, 5, 20, 50 or 100 percent. Test 2, 3, 5 and 7 opponents.
For 16, 32, 64 and 128 samples, enumerate all 1,024 cyclic offsets rather than
estimating the noise from a few random draws.

Compare ordinary sample means with
`full_reference_mean + mean(current_particle_value - reference_particle_value)`.
Evaluate the two nonlinear payoff functions separately on the same particles.
Record combo-weighted mean-squared error, all-offset mean bias, and unclamped
estimate extrema. Verify per-particle full means against the existing production
terminal evaluator within 1e-12. Unit checks require zero residual variance for
an identical reference and unbiased all-offset means for different references.

Interpret the result only as sensitivity to controlled range drift. Actual
training trajectories, GPU cost, refresh frequency and memory behavior remain
unmeasured. A two-pass sampled implementation has a first-order work count of
`2*K + 1024/refresh_interval` particles per update, before cache/launch overhead;
this arithmetic is not a performance projection. Consider a GPU prototype only
if the measured variance reduction could justify those costs.
