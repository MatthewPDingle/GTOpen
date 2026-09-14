# C24 ordinary-path comparison fixtures

Registered before comparison runs, after two complete native four-sample pairs
confirmed approximately 25% less time. Use the same frozen C24 executable as
the current-game trials, without compilation or source changes.

Use the existing immutable witnesses from C23:

- Small: `target/convergence/behavioral-fixed-e0-v1/final.gtop`.
- Large: `target/convergence/eight-native-a/final.gtop`.

For each, use `PreflopGpu::new` with the same 23911 MB budget on both roles,
and require its native batch to be 32 with HU cache enabled. Candidate promotes
that fresh ordinary engine to C24 static tables. Neither role uses cohorts or
the duplicate hash. This compares C24 against the ordinary path on these
fixtures; it is not the old C23-versus-retained-cohort comparison, and must not
be chained into that historical graph.

Run six iterations per process, including a complete gap/EV check after every
iteration; first two rows are warmup. Complete time includes construction,
input loading, synchronization and full-arena fingerprinting. Each process has
a fixed 300-second cap. This is a predeclared comparison bound, not permission
to extend a failed run. Run three alternating pairs for each fixture:
control/candidate, candidate/control, control/candidate. Small precedes large.

Require exact checkpoint values and full-arena fingerprints throughout, the
same initial allocation map and native planner, and matching qualified kernel
source/PTX. C24 may change only CDF allocation and add immutable index metadata.
No greater than 3% median complete-time regression on either comparison is
allowed. Retention also requires all three current-game pairs and their >=3%
median gain. The live-idle guard and single-workload rule remain in effect.

Names use `c24-witnesssmall-*` and `c24-witnesslarge-*` to keep these independent
controls out of the historical small/large chained dashboard plots. Their
results belong in C24's qualification details.
