# D02: sparse CDF direction rejected

Only **5.63%** of remaining unique current-play distributions in the large
fixture have one or two nonzero hand classes. This is below the predeclared
20% admission gate. Average-play distributions have none. No sparse kernel was
implemented and no speedup is claimed.

| Fixture / policy | Unique distributions | One hand | Two hands | Eligible |
| --- | ---: | ---: | ---: | ---: |
| Small current | 15,021 | 80 | 1,134 | 8.08% |
| Small average | 29,004 | 0 | 0 | 0% |
| Large current | 862,854 | 359 | 48,237 | 5.63% |
| Large average | 2,419,347 | 0 | 0 | 0% |

The read-only GPU inventory reproduced every D01 count, with unchanged learning
arenas and iteration. Histogram totals match active and unique distribution
counts. The guarded small and large runs completed in 1.05 s and 15.14 s;
build/classifier took 131.28 s. These are inventory times, not solver benchmarks.
Source hashes, commands and exit records are in `raw/d02-*`.

This eliminates one narrow mechanism. Distributions with up to eight hands are
more common (42.8% of large current unique distributions), but a different sparse
scan could change floating-point addition order. Do not quietly extend the
one/two-hand proposal to those cases or claim exactness without new evidence.

C01 remains retained; port 56708 remains unchanged.
