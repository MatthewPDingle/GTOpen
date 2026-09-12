# Fixed-current-policy sampling diagnostic

All three registered diagnostics completed and passed independent verification.
The existing 64-particle cyclic estimator is unbiased within the measured
floating-point error, but its action-ordering noise is substantial at the
selected multiway blind responses. This is diagnostic evidence, not a faster
qualified solver.

The saved current policies were frozen while all 1,024 sampler offsets were
enumerated. Full-particle action values agreed with the independent CPU
fixed-policy reference. Source and device histories stayed exact, and restoring
full-particle tables reproduced the original full result exactly. The maximum
absolute normalized regret-difference bias over all hands/actions was below
0.000003 bb in each case. All six paths had positive current opponent reach.

Worst relevant-hand probability that an action more than 0.1 bb inferior under
the full reference strictly outranks every acceptable action in one draw:

| Source saved policy | SB after open + call | BB after open + two calls |
| --- | --- | --- |
| 64 samples, seed 42, age 1,000 | 44.63% (AQo) | 46.39% (KQs) |
| 64 samples, seed 314159, age 1,000 | 53.81% (AQs) | 41.11% (98o) |
| 1,024 samples, seed 42, age 950 | 49.61% (JTs) | 41.41% (99) |

These are worst hands with current conditional mass at least 0.0025, not
range-wide error rates or probabilities that learning ultimately fails.
The full-particle source policy is also evaluated with 64-particle draws in
this diagnostic. Different saved stop ages are not a controlled comparison
of learning trajectories. Heads-up paths `[2,0,0,0,0]` and `[1,0,0,0,0]`
showed no inferior-action promotion; their payoff evaluation is not sampled
by this multiway estimator.

Complete per-hand means, bias, variance, MSE, covariance, raw units and
ordering probabilities are in each `*-verified.json`. All raw offset action
values are retained in the corresponding gzip archive and SHA-256 envelope.
The independent Python verifier includes an analytic covariance fixture and
malformed-evidence rejection tests. Rust tests cover actual sampled multiway
variation, exact source constraints, frozen seats, zero-reach subtrees and
subfloor history behavior. The first build attempt failed on a budget type
mismatch; it was corrected before any diagnostic run.

Regression validation: 181 default solver tests and 19 GPU equivalence tests
passed, in addition to the two new Rust tests and two analytic Python tests.
All workloads ran serially with the live-session busy guard.

## Large-game reach inspection

The separate final large-game diagnostic found zero current opponent-prefix
mass at 9 of the 16 failing average-policy paths. All nine still have positive
average-policy prefix mass. Their failure is retained in the acceptance gate;
zero current reach does not excuse an inaccurate response when a user selects
that branch. The other seven failing paths retain positive current reach,
so lack of reach is only part of the problem. The worst audited hand at each
of the 27 paths does not use the current uniform fallback.

Reproduce that summary with `check_large_current.py`; source input and output
records are `large-normalized-current-v1*`. Full-particle large learning also
missed the global gap target, so simply reducing sampling variance is not a
complete large-game fix.

## Next decision

Use decision-regret covariance and ordering errors to screen variance-reduction
candidates before another timed learning run. The prior terminal-payoff
variance screen cannot establish improvement at these decisions. Separately,
large-game work must preserve learning on branches that lose current reach
and address global instability; repeating more full-particle iterations is
not supported by this result. Keep the combined quality gates unchanged and
register any changed learning rule before evaluating it.
