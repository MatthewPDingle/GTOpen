# Reusable exact all-in arithmetic

23 September 2026. This is an implementation improvement for research, not a
new candidate, a change to the running experiment or a full-solver speed claim.

The complete 47,478-row physical-pair equity population can be grouped into
three 169-by-169 tables: joint hand-class probability and each player's
probability-weighted showdown return. Opponent-dependent values then require
small matrix-vector operations instead of traversing every physical-pair row.
Both card removal and exact board-enumerated equity remain in the tables.

All 16 combinations of two old saved policies and two synthetic extreme policies
matched the existing complete integrations, including every class value, within
7.11e-15 bb. A separate scalar review reconstructed all 85,683 matrix cells from
outcome-wise chip payouts and independently rebuilt all 16 response gains;
maximum discrepancy was 3.56e-15 bb.

The stored JSON table is 1,228,817 bytes. Construction took 1.59 seconds after
loading the existing exact cache. In these control calls, endpoint arithmetic
took 0.22–0.39 milliseconds per policy pairing, versus 3.37–5.56 seconds through
the current validating physical-pair helpers. These timings exclude building
the equity cache, policy inference, neural fitting and solver work. They are
individual control observations, not a full performance benchmark. Most of the
overall research cost remains elsewhere.

The table is specific to the incoming ranges, card-removal distribution, stack,
rake and terminal economics bound into its context hash. It is not a general
preflop strategy table. Policies must be constant across the suit-equivalent
members of each class at these first-own-action decisions, as separately
qualified by the catalog checks. Ordinary call/raise continuations are absent.

## Uses and limits

This gives future exact endpoint checks a cheap reusable calculation. It also
makes it practical to investigate integrating opponent-private-card and response
noise out of the two initial all-in decisions during training. That requires a
separate estimator integration and unbiasedness check; this module alone does
not modify training or establish that such a change improves ranges.

The active averaging experiment retains its original frozen evaluator. Do not
replace it mid-run. First analyze that experiment; a passing narrow screen still
leads to the broader call/raise test, not automatic deployment or an unrelated
new architecture search.

Evidence: `preflop-allin-matrix-control-v1-{registration,result,independent-review,matrix}.json`.
Implementation: `tools/research/preflop_allin_matrix_v1.py`.
