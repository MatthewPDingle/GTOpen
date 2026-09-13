# GPU research dashboard

Run `python dashboard.py --port 56709` from this directory, then open
http://127.0.0.1:56709. The server binds to localhost and only reads research
artifacts. It never controls the solver on port 56708.

The page refreshes evidence every five seconds. Reload the browser after an
HTML update. No JavaScript packages or external chart libraries are required.

## Progress graph

Inspired by the scatter points and running-best step line in
[Karpathy's analysis notebook](https://github.com/karpathy/autoresearch/blob/master/analysis.ipynb).
This is a solver-throughput adaptation, not training-loss data.

- The current C01 candidate is compared with its unchanged control using the
  median of three paired runtime ratios. Baseline is 100%; lower is faster.
- Whiskers show the minimum and maximum paired ratios, not confidence intervals.
- Select large/small game and complete runtime/warm iteration/accuracy check.
- Green means retained, amber means provisional, gray means rejected. Only a
  verified retained candidate can lower the running-best line.
- Hover or focus a point for values and status. Failed builds and tests have no
  valid speed measurement and stay in the activity log.
- Complete runtime includes initialization, warmup and synchronization. Neither
  it nor warm-iteration speed is a measurement of time to full convergence.

The current pass has one measured candidate; repeated runs are not presented as
separate optimization discoveries. C01 results are read from `raw/c01-*-bench.json`
and the decision from `raw/c01-verified.json`. Extend this series with each new
candidate and its verified control relationship as the research proceeds; do not
combine timings from unrelated fixtures or earlier accuracy-changing passes.

Validation: visually checked in Chrome; metric/fixture controls showed 96.00%
large complete runtime, 89.78% large warm-iteration time and 100.81% small complete
runtime. C01 subsequently passed independent evidence verification and is retained in the research branch.
