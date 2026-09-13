# D06: terminal evaluation dominates after C07

Verified eager CUDA event diagnostics; not a new speed result. The retained
performance line remains C01 + C07. All traced/untraced outputs match archived
C07 checkpoints and arena fingerprints on both immutable fixtures.

| Large-game phase | Learning median | Share | Check median | Share |
| --- | ---: | ---: | ---: | ---: |
| CDF construction | 1,558.38 ms | 42.89% | 2,187.34 ms | 35.02% |
| Coupled terminals | 1,955.47 ms | 53.80% | 3,981.79 ms | 63.71% |
| Final scratch restoration | — | — | 1.72 ms | 0.027% |
| Event total | 3,636.16 ms | | 6,249.88 ms | |

Small-game terminal shares are 50.30% learning and 60.78% check. Duplicate
classification is below 0.12% on the large fixture. Optimize terminal work next;
removing the final buffer copy would have negligible impact. Phase medians need
not sum to the median total. Eager events bypass graphs and add overhead, so
these observations do not replace paired end-to-end timing or establish actual
memory transaction counts.

Five C07 tests and four C01 tests passed. New trace coverage checks full arenas,
roots and gap/EV bits across repeated iterations, 4/7/9 players, frozen/locked
seats and batch 5/32. Expected interval counts include per-group CDF work,
per-player terminals and root copies. Event interval sums match totals. All
new runtime hooks are cfg(test); production kernels/allocations are unchanged.

Source/input/executable hashes and all output invariants are independently
audited by [check_d06.py](check_d06.py). Results are in
[raw/d06-verified.json](raw/d06-verified.json); source archive map is
[artifacts/d06-source-map.json](artifacts/d06-source-map.json). Frozen local
executable target/d06-profile-frozen.exe has SHA-256
1cb4e427d48daf5e5b31820385646346b2b8ce114341b952d0768cc1c1b47d61.

Next: C08 tests cooperative shared-memory staging of the CDF rows consumed
inside terminal evaluation. This differs from the earlier rejected shared
normalized-input staging in the CDF producer. It may reduce redundant gathers,
but barriers/bank conflicts/occupancy can erase the benefit. Require unchanged
terminal arithmetic and exact outputs before a paired timing screen.
