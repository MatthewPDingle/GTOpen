# N17: parallel pair normalization and centering

An implementation-only follow-up for the frozen N15 predictor. No model fitting,
changed features, reduced precision or production changes are introduced by N17.
It can be composed with the separately documented N16 float32 neural arithmetic.

Replace serial rank-incidence accumulation with 13 independent rank sums per
range. Each rank sums its pair and the 24 suited/offsuit classes containing that
rank; incidence weights are exactly 1/2 for pairs and 1/4 otherwise. Replace the
serial legal-pair normalization and the 338-entry correction centering sum with
256-thread block reductions. Keep double precision. Use the already prepared
parallel range descriptors. The host launch remains exactly 256 threads.

Freeze and compile two sources: N15 double arithmetic and N16 mixed arithmetic,
each with these new reductions. Execute only after N15's registered fresh-data
accuracy passes and both original N15 GPU oracles pass. Require the independent
12-case physical-hand action oracle for each source, plus <=0.0002 bb direct
action-value differences versus the matching N15 double-summary oracle. For the
double variant alone, require <=0.000002 bb direct action-value difference.

Benchmark three interleaved original/double/mixed repeats, 50 warm-up and 100
timed iterations on the unchanged tree. Compare every ordinary saved arena to
the previously verified ordinary baseline, and require repeated experimental
saves to be byte-identical in their numeric arenas. Compare mixed versus double
complete arenas diagnostically; inspected strategy difference must be <=0.001
absolute probability and player EV difference <=0.001 bb. Report this limited
scope rather than claiming all strategies identical.

The fixed-work runtime target is <=10% overhead versus ordinary Balanced. Any
passing variant still requires changed-policy validation. Neither arithmetic
equivalence nor lower iteration cost establishes convergence or full-game
accuracy. One GPU controller, live-app idleness, no concurrent CPU numerical
work during timings, and the fixed 20:49:02 UTC deadline all apply.
