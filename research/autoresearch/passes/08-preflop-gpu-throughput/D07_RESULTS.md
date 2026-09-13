# D07: terminal ordering fails the locality screen

The registered ordering made the scheduling proxy worse on both saved games.
Reject it before implementing a GPU prototype. Retain C09 unchanged.

| Fixture | Terminals | Miss ratio, 64 rows | Miss ratio, 256 rows |
|---|---:|---:|---:|
| Small | 7,098 | 2.141 | 2.120 |
| Large | 602,914 | 2.803 | 2.819 |

Ratios compare candidate to original ordering; lower is better. The admission
gate required large <=0.90 at both capacities and small <=1.03. Neither passed.
The existing order therefore has better locality under this specific proxy.
These are simulated whole-row misses, **not measured GPU cache misses or speed**.
Concurrency, cache-line accesses and exact probability aliases are not modeled.
No alternative ordering was searched after seeing these results.

The invariant test passed against a simple queue oracle. Both immutable saved
fixtures passed topology validation, exact coverage and unique terminal-value
checks. An independent Python OrderedDict implementation reproduced every
per-seat metric from compressed binary witnesses, including the permutation.
The small/large inventories changed 7,096 / 602,913 terminal positions.

Reproduce the independent verification with `python check_d07.py` from this
directory. `run_d07.py` records guarded extraction commands and immutable input,
source and executable hashes; its run IDs intentionally cannot be overwritten.
`raw/d07-source-map.json` identifies the exact tested source archive. The
working gpu.rs line endings were normalized after archiving; its only logical
change is a test-only module declaration. No runtime solver change, CUDA
workload, native/default regression campaign or deployment was needed.

The live dashboard still has 11 measured GPU candidates and three retained
improvements. D07 is a diagnostic, so it does not add a performance graph point.
The chained retained complete-work ratio remains about 84.9% of the initial
baseline, not a full-convergence or tenfold speed result. Port 56708 is untouched.

Next, revisit the remaining probability-construction work with a source-level
cost inventory before another kernel prototype. Avoid more unmeasured cache
preferences, terminal order variants or changes to sample count/precision.
