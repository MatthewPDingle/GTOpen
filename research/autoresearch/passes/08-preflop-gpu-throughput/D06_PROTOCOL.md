# D06: profile the retained bounded-cohort implementation

Registered before implementation and runs. C07 is retained after exact tests
and three paired comparisons per fixture. Measure the remaining work before
choosing another mechanism; do not interpret diagnostic timing as a speed win.

Add cfg(test)-only CUDA event markers to C07's shared check path: each player's
prepare/terminal/up/root-copy work, each group's normalize/classify/CDF work,
and final scratch restoration. Reuse the eager tracer and its preallocated
events. Kernels, allocations and numerical execution stay unchanged when the
tracer is disabled; production compiles these hooks out entirely.

Prove tracing preserves full regret/strategy arenas, root values, gap/EV bits
and continuation across multiple sweeps, frozen/locked seats, odd player counts
and batch 5/32. Assert group/player phase interval counts and event sum/total
consistency. Run existing C07 and exact-reuse tests. Build/test cap 240 seconds.

From the immutable small and large saves run one unprofiled and one profiled
six-sweep/check sequence, two warmups, unchanged C07 allocation and 1,024
particles. All paired checkpoints and final arena fingerprints must agree.
Also compare unprofiled outputs with archived C07 outputs. Each invocation cap
180 seconds, guarded by run07 and with source/input/executable hashes.

Report last-four medians and phase shares. Eager tracing bypasses graphs and
adds overhead, so it cannot establish a new performance improvement. Add D06
as a diagnostic only, excluded from graph points. No parallel GPU work, no
source edits during runs, no CPU performance work, no deployment or writes to
port 56708. Choose a bounded next experiment from these measurements.
