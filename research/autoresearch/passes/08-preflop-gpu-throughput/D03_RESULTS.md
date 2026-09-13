# D03: retained-C01 phase diagnosis

Verified diagnostic results; this is not a performance candidate. Port56708
was untouched. The graph's retained line remains the C01 result.

## Where the large game's GPU time goes

Median of four measured rounds after two warmups, eager CUDA events:

| Phase | Learning iteration | Share | Accuracy check | Share |
|---|---:|---:|---:|---:|
| CDF construction | 1,572.94 ms | 42.86% | 3,214.67 ms | 43.89% |
| Coupled terminal evaluation | 1,974.86 ms | 53.80% | 4,031.41 ms | 54.96% |
| Everything else | about 125 ms | about 3.3% | about 83 ms | about 1.2% |
| Event total | 3,672.34 ms | | 7,329.42 ms | |

Duplicate classification is only4.67ms per learning iteration and7.18ms per
check. On the small fixture, CDF/terminal shares are42.70%/50.36% for learning
and44.60%/51.47% for checks. Ordinary strategy-update kernels are not a promising
source of a large overall gain on these fixtures.

These eager timings bypass graph replay and include event overhead. Medians of
phase totals need not add exactly to the median overall total. They identify
work concentration; they are not measured hardware memory transactions, a
candidate speedup, or a full-convergence timing.

## Validation

- Four C01 tests passed, including full arena and checkpoint equality with
  tracing off/on, batch5/32 and forced/frozen policies.
- The original non-C01 tracer test also passed after the test-only helper refactor.
- Six checkpoints and final full-arena fingerprints matched for each immutable
  small and large control/profiled pair. Phase counts and event totals verified.
- A v1 assertion incorrectly expected a frozen seat to perform a learning
  traversal. The test expectation was corrected; v2 passed. The failed log is kept.
- All new timer hooks/helper code are cfg(test); the CUDA kernels are unchanged.
  This diagnostic did not justify rerunning unrelated production suites.

`check_d03.py` audits source/input/executable hashes, output equality, interval
counts and finite timings. Archived changed source is in `artifacts/d03-profile`;
its path map is `artifacts/d03-source-map.json`. Local executable:
`target/d03-profile-frozen.exe` (SHA256
`1794a38af62c54a04cd40ce24d1d919db99bc9b09cdc788cdbba04114d6c0f03`).

## Next

Test aligned first-prefix stores with a padded stride and fixed leading bias.
This follows the earlier padding assessment's untested alternative, rather
than repeating plain padding or compression. See `C05_PROPOSAL.md`. Full direct
reads and arithmetic remain unchanged; extra memory and initialization costs
must count. A benefit is plausible, not established.
