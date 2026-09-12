# Full-particle normalization passes the small combined-quality screen

Registered plan: [NORMALIZED_PARTICLE_QUALITY_PLAN.md](NORMALIZED_PARTICLE_QUALITY_PLAN.md).
Verifier: `python check_particle_quality.py`; machine-readable output:
`raw/particle-quality-verified.json`.

All runs used the same 23,038-node, six-seat fixture, fresh histories, gamma15,
and the canonical 1,024-particle evaluation model. GPU learning only; CPU
conditioned audits are correctness checks. Every 25 iterations, both global
gap and all six historical conditional paths were evaluated. Two consecutive
combined passes were required, with a fixed 1,000-iteration ceiling.

| Learning particles | Seed | Normalize regrets | Stop iteration | End-to-end seconds | Final gap (bb) | Conditional passes | Qualified |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 64 | 42 | No | 1,000 | 13.104 | 0.001771 | 2/6 | No |
| 64 | 42 | Yes | 1,000 | 12.736 | 0.009826 | 4/6 | No |
| 64 | 314159 | No | 1,000 | 12.977 | 0.001654 | 2/6 | No |
| 64 | 314159 | Yes | 1,000 | 13.044 | 0.016286 | 5/6 | No |
| 1,024 | 42 | No | 1,000 | 65.115 | 0.000940 | 2/6 | No |
| 1,024 | 42 | Yes | 950 | 55.180 | 0.002839 | 6/6 | **Yes** |

The full-particle normalized run passed all six conditional paths before its
global gap qualified. Combined passes occurred at iterations 925 and 950,
with gaps 0.00384472 and 0.00283911 bb. All 238 check records were independently
recomputed from their per-hand action values and probabilities. The six
separately loaded saved-game audits exactly matched final per-hand records.
Both sampled normalized final save hashes also exactly match the earlier
normalized runs, verifying that the additional audit cadence did not change
their learning trajectories.

This supplies a small-game quality candidate, **not a measured speedup over a
qualified control**: none of the controls met the combined gate. Sampling
removal is sufficient for this fixture and schedule; it does not establish
the specific variance mechanism, performance on other trees, or physical
multiway equity accuracy. Full-particle learning uses the fixed canonical
deck, so another RNG seed is not an independent full-particle trial.

Raw result JSON is archived as deterministic gzip, with original-byte and
compressed-byte SHA-256 envelopes. Guard records preserve source, executable
and input hashes. No server or live session on port 56708 was changed.

Next: register and test full-particle normalization on the 1,567,754-node
fixture with the original 27-path conditional audit and global gap gate.
Large-game qualification and practical speed remain unproven. Do not deploy.
