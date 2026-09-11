# Phase C, registered before execution

Run the six-path local audit for every Phase A candidate against the same
reference used in pass 05. Retain failures; global stopping is not local
qualification. Then test and run the synthetic variance screen.

The six-player gamma=15 averaging screen improved time to the same two full
checks. Test this combination on the eight-player and modeled fixtures,
64 rotating particles, seeds 42 and 314159, check cadence 50, target 0.005 bb.
Limits: 2,000 / 1,500 iterations and 3,600 / 1,800 seconds respectively.
Use the frozen pass-05 binary, identical inputs and memory budget. Count startup
and full checks; compare against original full-sample baselines. Do not multiply
separate speedup ratios. These new trials also require subsequent local audits.

All hardware work is serial and guarded by the live app's read-only status.
The app on port 56708 is unchanged.
