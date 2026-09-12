# Isolate averaging from learned-regret instability

Registered while the large normalized-pair seed-42 run is still running;
do not interrupt or alter that run. Execute this diagnostic only after its
terminal saved audit, and only if it fails combined quality. A passing run
instead advances to its already registered second seed.

For all-learning seats, the implemented `gamma15` and `dcfr` schedules have
the same positive/negative regret factors and sampler sequence. Their
average-strategy discount exponents differ (15 versus 2). Therefore a fresh
replay can test whether aggressive recent-iteration averaging causes the
observed global instability without changing the learned current regrets.
This expectation must be tested and verified, not assumed.

Replay the same 1,567,754-node, eight-seat fixture with normalized pair
correction, 64 samples, seed 42, horizon 1,000, and `dcfr` instead of
`gamma15`. Run exactly to the original terminal age (at most 3,000), without
early stopping, so the final regret arenas can be compared bit-for-bit.
Require no frozen/profiled/locked seats and identical configuration/model.
The diagnostic is invalid if the final regret arrays differ.

Every 50 steps retain native full-reference global gaps and all 27
conditional per-hand checks. Keep their thresholds unchanged. Evaluate both
complete saved states independently, preserving the original as an immutable
input. Report the comparison and whether averaging alone changes any
combined-quality result; do not infer a timed speedup from this forced-age
diagnostic or relabel an accuracy failure.

Before running, tests must show equal regret factors and sampler sequences,
and equal GPU regret histories despite different average histories in an
all-learning fixture. Use run07's one-workload busy guard, 10,800-second cap,
20,000 MiB base GPU budget and 1,024 MiB pair extra cap. Pin/hash calibration,
equity, original save, configuration, plan and executable. Port 56708 remains
unchanged. No further averaging exponents or learning changes in this test.
