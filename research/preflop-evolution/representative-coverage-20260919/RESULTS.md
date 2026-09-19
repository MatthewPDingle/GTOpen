# Overnight reference study

Updated 2026-09-19T08:34:59.950876+00:00.

Research only. Production port 56708 has not been changed by this work.

## Numerical correctness

| Comparison | Maximum EV difference | Root policy TV | Registered checks |
|---|---:|---:|---|
| Full vs compact, 2 flops | 0.00000569 bb | 0.00000897 | Passed |
| Full vs compact, 10 flops | 0.00001293 bb | 0.00001905 | Passed |

The separate abrupt-changing-range stress test still fails its 0.002 bb independent-trajectory value threshold. Successful converged tests do not erase that failure. The paging experiment uses the original fully enumerated path.

Paging unit test: passed, including bitwise CFV and arena agreement across 160 switches.
Connected two-flop paging: passed; all checkpoint evaluations identical: True. Shared workspace 1.422 GB; 1199.1 seconds.

## Broader coverage

The unchanged 47-flop candidate improves pocket-pair opportunity coverage over the ten-flop development panel. It remains an approximation; more representative chance coverage and unseen-board tests are needed before making accuracy claims.
Feasibility trial: latest recorded iteration 20, gap 5.206158 bb, elapsed 405.4 seconds. A checkpoint alone does not prove completion.

Last recorded validation-queue stage: `complete-awaiting-trial-review`. Check the actual process before treating that stage as live.

![Recorded numerical checks and convergence](validation-progress.png)

## Independent evaluation

The reserved-board protocol freezes all preflop decisions, solves their postflop continuations, then separates postflop numerical residual from profitable full-game deviations. Deterministic controls precede reserved-board use. Ten reserved flops are a transfer stress test, not a precise full-deck exploitability estimate.

[Paging protocol](PAGING-PROTOCOL.md) · [Reserved-board protocol](HOLDOUT-PROTOCOL.md) · [Transfer controls](TRANSFER-CONTROLS.md) · [Earlier coverage findings](../integrated-coverage-20260919/RESULTS.md)
