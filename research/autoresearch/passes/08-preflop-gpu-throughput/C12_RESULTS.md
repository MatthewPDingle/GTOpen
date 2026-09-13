# C12 rejected: predicated scan is effectively tied

The candidate preserves results but fails the first-pair speed screen. It is
archived and removed; C09 remains retained and port 56708 is unchanged.

| Large frozen fixture | C09 | C12 | Candidate / control |
|---|---:|---:|---:|
| Complete run | 64.5204 s | 64.4201 s | 0.99844 |
| Warm iteration median | — | — | 0.99950 |
| Accuracy check median | — | — | 1.00385 |

The complete gain is only 0.16%, below the registered first-pair 1% screen.
No extended campaign or full default/native regression campaign was run for
this rejected change. This is not evidence of a repeatable gain.

The compiled CDF has the same 30 up-shuffles. The reference has 30 explicit
float selections; the candidate has none and uses 30 predicate-guarded
round-to-nearest additions. Both loaded functions use 26 registers, zero local
memory and zero shared memory. PTX differences are verified; no claim is made
about the final native instruction count or the cause of the timing tie.

The prefix comparison passes all 288 combinations of input patterns, indexing,
gates, sample offsets and counts, comparing all output bits including untouched
sentinels. Five expanded cohort tests pass across original/C01/C07/C09/C12,
covering 3-9 seats, batch5/32, every terminal, prefixes, zero reach and recovery,
frozen seats/locks, graph capture/replay and stop. Four exact-reuse tests also
pass. The fresh-only switch rejects changes after capture. Small and large
allocation inventories match C09 exactly. Both large timed runs match each
other and earlier C09 in all six checkpoints and complete arena fingerprint.

`check_c12.py` audits these claims against logs, compiler artifacts, archived
source, immutable input/executable hashes and layouts. `run_c12.py` records the
qualification/screen procedure; run IDs cannot be overwritten. Exact tested
source is in `artifacts/c12-rejected`, with `artifacts/c12-source-map.json`.
The frozen executable SHA256 is
`aca215f3a4d2ffc426d214120577d373cc3191829c0b0e842b0d704f85a3bca2`.

The graph now contains 12 measured GPU candidates and three retained gains;
the chained complete-work baseline remains 84.9%. Full large-game conditional
convergence and the user's order-of-magnitude goal remain unresolved.

Next: obtain instruction/memory-stall profiling of retained C09 before another
small kernel rewrite. `ncu`, `nvdisasm` and `cuobjdump` are absent from PATH;
standard NVIDIA install locations also have no Nsight Compute/CUDA toolkit.
Investigate a local official NVIDIA tool archive first. Do not change driver
permissions, restart the app, or equate profiler replay duration with production
runtime. NVIDIA's profiling guide documents replay/cache effects and potential
counter-access limitations: https://docs.nvidia.com/nsight-compute/ProfilingGuide/.
