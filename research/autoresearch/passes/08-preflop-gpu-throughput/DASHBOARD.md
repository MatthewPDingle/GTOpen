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

- Each candidate is compared with its unchanged control using the
  median of its completed paired runtime ratios. C01 has three pairs; C02 was
  rejected after its first pair. Baseline is 100%; lower is faster.
- Whiskers show the minimum and maximum paired ratios, not confidence intervals.
- Select large/small game and complete runtime/warm iteration/accuracy check.
- Green means retained, amber means provisional, gray means rejected. Only a
  verified retained candidate can lower the running-best line.
- Hover or focus a point for values and status. Failed builds and tests have no
  valid speed measurement and stay in the activity log.
- Complete runtime includes initialization, warmup and synchronization. Neither
  it nor warm-iteration speed is a measurement of time to full convergence.

Candidates are listed in `experiments.json`, including the retained control each
builds upon. The graph chains paired ratios back to the original baseline; its
whiskers describe each individual experiment's variation, not cumulative
uncertainty. Repeated runs are not separate optimization discoveries. A rejected
candidate cannot lower the retained-best line. Reads `raw/c*-*-bench.json` and
per-candidate `raw/cNN-verified.json`. Add each future candidate and its correct
control relationship to the manifest; unrelated accuracy-changing passes are
not comparable and must not be inserted into this series.

Validation: visually checked in Chrome; metric/fixture controls showed 96.00%
large complete runtime, 89.78% large warm-iteration time and 100.81% small complete
runtime. C01 subsequently passed independent evidence verification and is retained in the research branch.
