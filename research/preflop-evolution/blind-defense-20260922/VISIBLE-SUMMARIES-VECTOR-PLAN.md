# Vectorize unchanged visible-card preparation

Prepared 2026-09-28 after the fixed-current-policy pilot and CPU profile.
GPU inference took a median 7.1 ms, while preparation took 306.6 ms. The CPU
profile attributes 44%-51% of profiled preparation time to scalar visible-card
summaries. Optimize that measured operation in NEW modules; retain every
registered implementation and do not change the representation or policies.

Candidate: compute the same 33 visible-card summaries in batched NumPy using
rank/suit counts and straight patterns. Preserve the original 269 one-hot
features, exact made-hand category and tie breaks, board multiplicities,
suit-group ordering and other summaries. Future/opponent cards remain absent.
Preflop additions remain zero. Keep float64 arithmetic before float32 output.

Before first execution, register sources, seed, immutable pilot inputs and
these controls. Compare every float32 feature byte on 40,000 deterministic
random inputs (10,000 each preflop/flop/turn/river), plus explicit all-category,
wheel, two-trips, three-pair and board-only examples under all 24 suit maps
and reversed within-group ordering. Require all nine categories to be covered.

On all 12 frozen pilot query batches, require byte-identical complete features
and prepared float64/integer/bool arrays, including table overrides and own
histories. Use the first declared model pair's table state. Nothing changes
in inference: identical prepared inputs imply the existing qualified model
receives the same bytes. No GPU rerun is needed to time a CPU-only operation.

Both implementations must reject the same nine explicit malformed one-hot
inputs, including future-card leakage, duplicate cards, history gaps and bad
integer semantics. Check empty arrays too. Time complete preparation in fixed
reference/vector/vector/reference order for every batch, preserving all cases.
Report whether it is faster; do not change failed controls or select cases.

CPU only, one BLAS thread, 180-second limit, at most 2 MB new evidence from the
preceding study's unused allocation allowance. No training, native changes,
production modification, archive deletion, altered validation semantics or
GitHub push. Register failures and version corrections. A speed gain here is
for query preparation, not proven overall solving or convergence performance.
