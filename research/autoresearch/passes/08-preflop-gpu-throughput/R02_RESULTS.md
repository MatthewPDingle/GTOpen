# R02: partial GPU allocation recovery qualified

Both the R01 wide path and the C14 narrow path recover after a real CUDA
out-of-memory error during optimized construction. The error occurs after
work/maps, exact-reuse storage and the first extra values buffer exist. The
same selection function constructs the ordinary GPU engine and preserves the
configured budget, batch, HU cache, solver age and initial arenas.

| Synchronized device-pool used bytes | Both paths |
| --- | ---: |
| Before construction | 0 |
| At injected allocation failure | 3,933,780 |
| After ordinary fallback construction | 3,409,848 |
| After fallback shutdown | 0 |
| After successful optimized retry and shutdown | 0 |

The fallback uses exactly the independently measured ordinary-engine allocation,
not that allocation plus leaked optimized buffers. The driver temporarily reserves
32 MiB in its pool; reserved capacity is recorded separately from bytes in use.
No pool-trimming or driver changes were used to obtain the result.

Three iterations and accuracy checks compare full strategy/regret/root arrays,
gaps and EVs bit for bit against ordinary construction. The fixture contains a
frozen player and a point lock. Captured execution, stop and CPU synchronization
match. An optimized construction and the same numerical checks also succeed
after cleanup. The existing selection suite passes: 3 tests, 1 intentionally
ignored saved-game harness. This addition is entirely test-gated, so it does not
change the runtime qualified by C14's 19 GPU and 181 default regressions.

Version 1 is retained as a failed test. Its wide case passed, but Windows accepted
more than reported physical VRAM on the narrowed case. Version 2 requests 1 PiB
through the allocator without initializing/accessing it; the driver rejects it
with CUDA_ERROR_OUT_OF_MEMORY. This corrects the failure witness, not the solver
or the recovery criteria. Both stages and source versions are archived.

`check_r02.py` independently verifies source/input hashes, the initial failure,
actual driver error, allocation stage, memory accounting, numerical test evidence,
selection suite and successful retry. See `raw/r02-verified.json` and
`artifacts/r02-{v1,v2}`. No speed improvement is claimed for this diagnostic.

Remaining: separate retained GPU modules from unrelated research features,
integrate selection/reporting in the server, and qualify an isolated server with
saved-session loading/continuation. Port 56708 remains untouched.
