# N09 cached-prior GPU experiment

Prepared after the fixed training screen passed, before prospective evaluation.
No GPU work is launched until N09 passes that accuracy screen and the reference
controller has stopped. No application restart, deployment or cache replacement.

Use the already isolated filtered-interface executable, unchanged. Generate a
new CUDA module with two opponent-major 169x169 float32 relative-equity matrices
from the frozen priors (228,488 bytes). Compute these once during export; do not
recalculate class adjustments or conditional features at each terminal. The
new source retains anchored compatible-pair weighting and folded-player sunk
cost handling, and blends by min(SPR/8,1). Candidate inference is active at
SPR 1 through 20, with the existing Balanced fallback outside that domain.
Every reserved N09 evaluation context lies within it.

This is a paired-interface experiment, not a drop-in production-cache replacement.
Two-player chance is physical class-compatible chance using approximate cached
equities. Larger games still reset that prior when two players remain and ignore
folded-card bunching. Do not load its experimental saved games into the app.

First require the existing independent 12-case action-value/accounting oracle,
redirected to the new model through an isolated Python namespace. Compare against
float64 physical-combination calculations, not the exported float32 matrices.
The ordinary solver executable and CPU/GPU implementation remain frozen.

If accurate, run three interleaved repeats of original Balanced and this candidate,
each with 50 warm-up plus 100 timed synchronized iterations from the same game.
Report setup, warm-up and total time separately. Require complete saved-state
equality for original Balanced versus its N04 counterpart and across candidate
repeats. Candidate strategies are expected to differ from the baseline.

The runtime target is no more than 10% median overhead versus original Balanced.
This is fixed-work speed, not full-game convergence speed. Fresh changed-policy
references and strategy checks remain necessary before recommending integration.
Observe the one-GPU-workload rule, live-app guard and 20:49:02 UTC deadline.
