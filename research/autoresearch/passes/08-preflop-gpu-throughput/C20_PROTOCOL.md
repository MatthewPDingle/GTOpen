# C20: learning-only exact-zero scan bypass

Registered before build. D17 measured 33.64% empty large-learning tiles and
39.97% small-learning tiles. This candidate bypasses the five shuffle/add
steps only when a warp-wide vote finds every lane value numerically zero.
It preserves the original loads, carry additions, stores, sample order,
precision and every nonempty scan operation. No positive-value cutoff.

Append a separate sparse CDF kernel; retain all original kernel entries
unchanged. Subsequent integration selects the sparse entry only in learning
evaluations. Accuracy-check cohorts retain the original function, with no
per-tile sparsity test. Add no device arrays or shared-memory staging.

Stage1 cap300 seconds: standalone GPU comparison of every prefix output bit
and untouched guards for 12 ordered input cases (dense, zero, dense recovery,
sparse, positive subnormal, final-hand-only, near-one plus tiny values, small
positive dense, negative zero, alternating signed zero, single subnormal with
negative zeros, sparse tiny positives with negative zeros), compact/noncompact,
aliases, gate0/1, zero-mass slots, sample starts0/17/992 and batch/count pairs
1/1,5/1,5/5,32/1,32/7,32/31,32/32: 1008 cases per variant.

Require exact outputs, zero spills, <=48 registers, no shared memory, sparse
entry static PTX instruction count <=120% of original writer. Require a
warp vote and conditional branch that bypasses the shuffle/add chain; all
20 original entries, including the check writer, must remain byte-identical
to the retained compiled entries. This is admission, not a speed claim.

Only after stage1 passes: integrate selection before graph capture, audit both
writers' dispatch, repeat full arenas/roots/terminal counts/zero recovery/
fixed players/stop/graph tests and both saved memory layouts. Include cold
construction/compilation/module costs. First complete large pair rejects at
candidate/control >=0.99; survivors need three alternating pairs per fixture,
median large gain>=3%, small regression<=3%, exact full checkpoints and full
default/native regressions. No promotion without full qualification.

One run07-guarded workload at a time. 56708 read-only; no source edits during
workloads. No sample reduction, policy or convergence target change. The
tenfold complete-solve target remains unachieved even if this candidate passes.
