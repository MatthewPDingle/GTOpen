# C01: exact CDF reuse retained

The large eight-player benchmark took **4.0% less complete runtime**, using the
median of three paired candidate/control ratios. Its warm iterations took
**10.2% less time** and accuracy checks **1.7% less time**. The six-player small
fixture took 0.8% more complete time, inside the 3% nonregression bound; its warm
iterations took 8.5% less time. This is useful execution-speed progress, not the
requested order-of-magnitude improvement or faster convergence per iteration.

| Large pair | Control complete | Candidate complete | Ratio |
| --- | ---: | ---: | ---: |
| 1 | 74.638 s | 71.926 s | 0.96367 |
| 2 | 74.360 s | 71.383 s | 0.95997 |
| 3 | 74.584 s | 71.177 s | 0.95431 |

The candidate adds 5,746,632 bytes of device metadata on the large fixture.
CDF allocation remains 8,444,664,320 bytes, with particle batch 32. It changes
neither particle count/order nor solver updates. A full-value comparison after
a hash match allows identical normalized hand distributions to share one CDF.
The bounded hash table falls back to independent work on probe overflow.

## Evidence

- Twelve fixed-work runs, alternating candidate/control order across three pairs
  per fixture. Each starts from the same frozen native save and runs six sweeps
  with a full check after each. The first two sweeps are warmup.
- Every paired checkpoint gap and EV agrees exactly. Final full-arena fingerprints
  agree for both fixtures. Fingerprints are checksums, not a comparison of every
  bit; the adversarial small tests perform full bitwise arena comparisons.
- Three focused GPU tests cover forced collisions/overflow, fixed policies and
  locks, graph capture, cooperative stop, zero live/folded/own reach, recovery,
  batch 5/32 and all two-to-eight opponent counts.
- Native GPU suites: 19 passed. Default solver suite: 181 passed.
- `check_c01.py` independently audits inputs, source and executable hashes,
  paired numerical outputs, timing shape and the predeclared retention rule.
  Output: `raw/c01-verified.json`.

The timing executable was frozen before appending the all-opponent-count test.
Its local archive is `target/c01-benchmark-frozen.exe` (SHA recorded in the
verification JSON). Its exact test source is tracked in
`artifacts/c01-benchmark-tests.rs`; algorithm sources did not change. The checker
allows only these explicit archive substitutions. Run it from this revision
before changing solver sources for later experiments. Earlier immutable run
scripts intentionally refuse to overwrite evidence or run against changed sources.

## Limits and next step

This is a research-only opt-in implementation. The application on port 56708
was not restarted or changed. Large-game conditional convergence remains an
open problem, as documented in pass 07. Full time-to-qualified-solution has not
been measured with C01.

Next screen: measure the support size of the unique positive distributions
remaining after exact reuse. If at least 20% contain only one or two nonzero
hand classes, consider a separately validated sparse CDF path. Otherwise reject
that direction before implementing another kernel.
