# D17: actual learning occupancy admits a GPU prototype

All preserved D10 identities, ordered terminal witnesses and JSON match exactly
on both saved games. The optional witness only records support masks; learning
arenas and iterations remain unchanged. Build/test passed in 131.531 seconds;
small and large extraction took 1.125 and 16.297 seconds. Both independent
occupancy methods agree for every support pattern; census took 38.718 seconds.

| Learning fixture | Distinct distributions | Distinct support masks | Empty / total tile scans | Empty fraction |
|---|---:|---:|---:|---:|
| Small | 15,021 | 2,178 | 36,887,173 / 92,289,024 | 39.97% |
| Large | 862,854 | 67,346 | 1,783,515,301 / 5,301,374,976 | 33.64% |

Counts include every traverser's distinct learning distributions and all 1,024
fixed samples. The six tiles per sample form 6,047 unique support masks; host
deduplication preserves their multiplicity. NumPy three-word intersections and
Python integer intersections agree. An independent structured binary decoder
reconciles every identity, support histogram, per-seat count and final total.

The >=20% actual large-learning gate passes. This admits a separate exact-zero
GPU prototype, not a retained performance improvement. The candidate would
skip only the within-tile shuffle/add chain, keeping loads, votes, carries and
stores. Averaged accuracy checks remain on the original writer because their
large-game distributions are dense. Signed zero/subnormal behavior, compiler
branch behavior, full solver state and complete-work timing still need tests.
The 33.64% figure is not a runtime speedup, and this opportunity alone cannot
deliver the user's tenfold target. These two fixed saved states also do not
establish occupancy throughout future learning trajectories.

Evidence: `raw/d17-verified.json`, `raw/d17-occupancy.json`, compressed support
and per-pattern witnesses, manifests, guarded logs, test-only source archive
and `check_d17.py`. Frozen diagnostic executable SHA256:
`000ab91785d234d4adcc7a12106525026015ae21a5cffab7f58321ebb2235b4c`.

The optional extraction remains test-only. No production dispatch, kernel,
probability or stopping target changed; port 56708 is untouched.
