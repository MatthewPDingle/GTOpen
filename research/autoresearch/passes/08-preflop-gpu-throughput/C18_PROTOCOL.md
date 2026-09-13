# C18: compact equal sampled-rank products

Registered after D13 admission and before candidate implementation. Start from
retained C14/R03; only terminal product evaluation changes. Port 56708 stays
read-only. One guarded build/test/GPU workload at a time; no source edits during
workloads. Preserve failures. Do not alter samples, precision, mathematical
model, policies, action menus, learning rules or stopping targets.

## Mechanism

Precompute immutable sample-specific mappings: compact group lower/upper bounds,
number of groups, and each hand's group index. Products depend on sample rank,
opponents and quadrature point, so each terminal block computes them once per
compact rank group. Store Q products per group in block shared memory, then
all 169 hands perform their original ordered weighted additions. Synchronize
before reads and before the next sample overwrites scratch. Use one terminal
per 192-thread block; all threads participate in barriers, even h>=169.
Keep original unroll-two sample hint and bounded CDF addressing. Each helper's
Q and opponent count remain compile-time constants. Keep the original CDF
construction, cohort layout and global allocation plan.

Mappings add (3*1024*169+1024)*4 bytes if all three arrays are rectangular;
shared product storage is at most169*5*4 bytes per block. Account actual buffers
and startup construction. Allocate no terminal-by-sample product cache. Fallback
and baseline remain separately selectable; do not replace a kernel after graph
capture. Changing runtime signatures requires all launch paths updated together.

## Qualification before full integration

First isolated kernels: retained versus compact helper for O=2..8, Q=2..5,
all-equal/all-distinct/warp-boundary/mixed rank groups and the real static table,
zero/dense/sparse CDFs, sample offsets 0/1/37/992 and counts1/5/7/23/31/32
that remain in bounds. Keep different nonzero per-hand initial accumulators so
sharing a final sum fails. Compare every f32 output bit, including guard entries.
Use all192 threads in candidate wrappers; no partial block may skip a barrier.
Record PTX and loaded register/local/shared-memory attributes. Build/test cap300s.
Reject numerical failure; archive and correct only a diagnosed implementation
mistake, not a changed tolerance. Qualify source transformations explicitly.

Then integrate opt-in research constructor and new immutable mappings into
retained cohort evaluation. Cover graph/eager, fixed seats, zero-mass recovery,
partial batch5/32, stop/capture/replay and complete regret/average arenas. Verify
small/large allocations differ only by declared mapping buffers. Freeze source
and executable before benchmark. Normal production constructor remains unchanged.

## Timing and retention

First matched large six-sweep control/candidate pair, cap180s each via run07.
Reject complete ratio>=0.99. Only a passing first screen proceeds to three
alternating pairs for both fixtures. Retain only>=3% median large complete gain
with<=3% small regression, exact checkpoints/arenas and complete required native
GPU/default regressions. Count cold setup, checks, synchronization and mapping
construction. No microbenchmark-only retention, convergence or10x claims.
Do not automatically combine warp-local sharing with a rejected compact kernel;
it requires separate protocol and evidence review.
