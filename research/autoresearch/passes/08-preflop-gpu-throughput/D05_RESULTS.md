# D05: wider cohorts admitted for a prototype

The statically selected large grouping saves **47.35% of average-check CDF
rows** and fits the registered23GB preplanned allocation budget. This is an
inventory result; no speedup has been measured or retained.

| Fixture | Group sizes | Separate C01 rows | Cohort rows | Fewer rows | Peak including reserve |
|---|---:|---:|---:|---:|---:|
| Small | 2 + 4 | 29,009 | 16,763 | 42.21% | 0.605 GB |
| Large | 4 + 4 | 2,419,357 | 1,273,730 | 47.35% | 22.924 GB |

Exhaustively checked196 small and3,795 large partitions, allowing groups of
one through four. Selection uses only static tree topology: minimum summed
static union rows among fitting plans, then memory and lexical masks. Large
groups are seats0-3 and4-7; small groups0-1 and2-5. No current learned strategy
is needed to choose or retain this grouping during later iterations.

The large plan has722,172 static CDF slots and a15.714 GB CDF allocation at
batch32. Three full extra d_val arenas cost2.087 GB. Total logical device
allocations are22.655 GB; a256MiB reserve gives22.924 GB. Only76.2 MB remains
inside the registered23GB budget after that reserve. The physical RTX3090 has
additional capacity beyond this budget, but the prototype may not spend it
to qualify. Keep checking exact allocation totals as implementation evolves.

Constructor preplanning is necessary: allocate-before-release would require
31.637 GB. Do not enable this by allocating replacements beside the old CDFs.
No sampling reduction, smaller particle batch or removed HU cache is allowed.

All distribution identities and every previous D04 singleton/pair result match.
The histogram-derived subset counts agree with explicit sets; a separate
Python partition enumerator verifies all costs, selection and the Pareto
frontier. Learning arenas, average reaches/masses and iteration remain
unchanged. Tests cover collisions, signed zero, overlap and partitions for1-9
seats. One initial compile failure was a missing integer type annotation;
the failed source/log is preserved and corrected build tests pass.

Evidence: `raw/d05-*-v1.json`, run metadata/logs, `raw/d05-verified.json`,
`check_d05.py`, and `artifacts/d05-inventory`. The local frozen executable is
`target/d05-inventory-frozen.exe`. Large diagnostic runtime46.94s includes
host inventory and enumeration, not solver throughput.

Next: C06 shared cohort CDFs during accuracy checks. Per-player terminal values
must survive every particle batch in separate buffers before the usual up
sweeps. All1,024 samples, addition order, learning updates and locked/frozen
behavior remain unchanged. Numerical tests and complete paired timings are
still required. Port56708 and its sessions are unchanged.
