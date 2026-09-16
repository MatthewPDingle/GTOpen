# N14: parallel range summaries, unchanged predictor

Specified before execution. The conditional GPU kernel currently computes
each player's range descriptors in a serial 169-hand loop on one thread.
Use one 32-thread warp per player and combine the same sums and top-three
hand masses. Retain double precision, all 104 coefficients, legal-pair
accounting, the shared-memory layout and the existing barriers. No fitting,
feature changes, new reference labels or production deployment.

Floating-point summation order changes. Require the independent 12-case
physical-hand oracle to remain within 2e-6 bb per action, and pot accounting
within the original oracle tolerance. Then use three interleaved repeats
of ordinary Balanced, the N04 filtered control and the warp version. Each
has 50 warm-up and 100 timed iterations on the existing 410270-node save.

Compare every saved regret and strategy accumulator against the filtered
control: absolute difference <= 1e-6 + 1e-5 * maximum absolute magnitude.
Also require inspected strategy probabilities within 1e-4 and seat EVs
within 2e-5 bb. Record exact equality separately; do not call toleranced
agreement bit-identical. Candidate repeats must agree exactly. These are
arithmetic and fixed-work checks, not full-game convergence guarantees.

The speed objective remains <=10% overhead versus ordinary Balanced. The
old predictor failed prospective accuracy, so even a speed success cannot
promote it. A newly qualified model requires its own combined validation.

Do not overlap other GPU work or CPU model fitting with these timings.
Source preparation is allowed during N04; compile and numerical checks
wait until N04 timing finishes. The original ten-hour deadline applies.
