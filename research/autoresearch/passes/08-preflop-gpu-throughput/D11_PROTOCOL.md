# D11: retained-kernel phase refresh and work-volume census

Registered before new profiling/count extraction. Retained baseline C14/R03 at
7e1fe7f. GPU performance only; 56708 read-only; serial run07 guard and caps.

Refresh eager CUDA event phase timings for the retained narrowed/unrolled cohort
path. D06 predates C09/C14 and cannot establish the current phase balance.
Add a test-only copy of the existing tracer qualification using the retained
constructor; keep original tracing tests. Permit profiling in the benchmark's
retained constructor (a test assertion previously prohibited that combination).
No production source, CUDA kernels, policies, precision or samples change.
Require exact traced/untraced full arenas, root values and gap/EV results,
4/7/9 players, fixed/learning seats, batches 5/32, and expected event counts.

Then run matched six-sweep unprofiled/profiled saved benchmarks for small and
large fixtures, all outputs matching archived C14. Count initialization and
synchronization, but report phase timings as eager diagnostics, not speedups.
Build/tracer-test cap300s, each saved run180s. Record frozen source, executable,
input hashes and GPU snapshots. Do not rerun denied hardware counters.

Independently decode the existing verified D10 binary witnesses to count positive
terminal work by opponent count. Reconcile with D10 per-seat terminal totals and
weighted references. From original code, count per hand/sample arithmetic:
O subtractions, Q*O multiplies, Q*O multiply-add pairs, and Q weighted additions;
Q=(O+2)//2. Express this as O+3*Q*O+2*Q floating-point operations, with FMA=2.
Keep O fmax operations separate; omit indexing, control, division, normalization,
metadata and final pot/investment updates. Logical CDF gathers are 2*O floats
per hand/sample. These are source work counts, not executed-instruction or
DRAM-transaction measurements.

Deduplicated CDF output volume is distinct distribution rows *1024*170*4 bytes.
This is a minimum logical volume for the current eager materialization design:
the device classifier can fall back after its bounded probe count. Do not assume
all logical gathers miss cache, or present logical bytes as measured traffic.
Learning counts describe an immutable starting snapshot, not evolving sweeps.

Use NVIDIA's GA102 whitepaper Table9 (RTX3090 reference design) for an explicitly
illustrative 35.6 TFLOP/s and 936 GB/s comparison. Record local nvidia-smi model,
max clocks and power limit; do not change settings. Reference peak is not a
measured machine ceiling, especially with a non-reference board. No definitive
impossibility claim follows from this calculation.

For each measured phase fraction f, show Amdahl's ideal total speed multiplier
1/(1-f) if that entire phase became free. Also show the required combined
CDF+terminal reduction for 10x, under the deliberately optimistic assumption
that all other phases remain fixed. Derive next priorities from the measured
balance. This diagnostic does not admit a changed solver or add a performance
graph point. Preserve all unsuccessful runs and independently verify outputs.
