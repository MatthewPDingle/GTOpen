# Fixed 64-hand posterior river control

Prepared before execution, 2026-09-28. Use all eight completed actual-policy
TRAIN cases (67 river targets) from river-learned-batch-cost-v1, with their
registered generation-77 policies. No new training, eval deals or production
change. Preserve all previous sources and evidence. GPU stays unused.

K=64 is fixed before observing this control. Construct the complete normalized
opponent posterior using entry mass and all actual opponent action-history
probabilities. All 990 compatible pairs remain in this normalization; zero
support rejects. Own reach must be independent of opponent cards and must not
multiply the posterior. Current-policy preflop/board-root overrides remain.

Use the retained complete native shared batch as an independent reference.
Stage one prepares only all target/history queries and their own-history
closure, runs the bound CPU policy and reconstructs posteriors. Stage two draws
64 pairs with replacement from each posterior, using PCG64 with a SHA256-derived
seed bound to case, policy and target. It prepares only complete future-action
trees of selected pairs plus their history closure. Every inferred probability
must match the retained full-query inference within 1e-10 with identical support.
Trees/action menus/payoffs are unchanged; no opponent card becomes a visible
feature. Repeated draws retain multiplicity. Use common draws for every hero
action, and subtract the same sigma-weighted value for the regret target.

Compare the resulting vector to independent selection of exact per-pair action
vectors. Require agreement within 1e-8 bb. Require full-posterior weighted means
to match exhaustive targets and verify variance of the sample mean is the
single-draw covariance divided by 64. Also retain 2,048 independent sampled
means per target under a distinct deterministic stream; compare action-wise
mean against exact mean with 8 standard errors plus 1e-9 bb tolerance. This
checks the implementation, not a new policy-quality claim. Zero-variance rows
are included, not filtered to favorable cases.

Negative controls cover zero support, missing compatible pairs, nonfinite or
unnormalized posterior, wrong draw count, out-of-domain draw, missing future
probability and lost multiplicity. Retain all cases and errors. Record stage-one
and stage-two query counts, including duplicated history work. The predeclared
engineering gate for implementing new native transport is at least 25% fewer
total prepared rows than full expansion across these cases, with all correctness
checks passing. Counts do not establish native elapsed speed: this control
subsets existing exports. If the gate passes, measure a real native two-stage
implementation before training admission.

CPU only, one BLAS thread, sequential cases, maximum 300 seconds and 8 MB new
evidence under the existing 800 GB global cap. Require 24 GB free RAM and idle
production; do not contend with the heavy external GPU workload. Seal inputs
before execution and recheck them before publishing a terminal result. Preserve
failure and version any correction; never edit executed source for a rerun.
