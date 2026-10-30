# Context fitter implementation qualification

This bounded control uses retained native observations with synthetic targets
from the fit-row fixture. It is not a scientific poker-learning comparison and
does not generate new poker labels. Both actors and both 362/387-input formats
include all five fitting stack depths and all four streets.

Before launch, record exact source/input identities. Refuse an existing
registration, attempt, result, failure, store or research lock. Respect active
production solves and existing light-desktop sharing rules. Never retry a
started control under the same identity; preserve any failure.

For each of four actor/representation cases:

1. Compare CPU and CUDA float64 raw outputs, complete weighted loss and
   gradients at the neutral seeded initialization. Absolute tolerance 1e-10.
2. Fit 256 full-gradient Adam steps with seed 9300201+actor, learning rate
   0.003 and ordered chunks of 128, once directly and once with CUDA gradient
   graph replay. Require identical exported networks and equal recorded losses.
3. Read each fitted network through widened-float64 CPU and CUDA operations.
   Require raw-score difference at most 1e-10. Save the compared raw arrays
   and both exported networks for independent readback.

Repeat three short captured fits only to verify deterministic replay and
released tensor allocations. Check that initialization/fitting do not consume
the caller's CPU or CUDA random streams, and that the prepared objective
identities are unchanged between the two execution paths.

Resource caps: 600 seconds, 1 GB reserved CUDA, 64 MB new logical evidence,
16 MB storage reserve, 800 GB global allocated research budget, at least40 GB
free S: space and24 GB available RAM. No production changes or deployment.

Passing qualifies only this fitter's implementation. Native target collection,
complete joint-cycle publication/restart, end-to-end upstream influence, and
actual strategy quality remain separate required work.
