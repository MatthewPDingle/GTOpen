# C02: compact active terminal queue

Baseline: retained exact CDF reuse (C01). Hypothesis: launching one block for
every multiway terminal on every particle batch wastes scheduler work on zero
probability and non-live terminals. Compact positive prepared terminal indices
on the GPU once per traverser, then reuse that list for subsequent batches.

Preserve C01's first-batch full terminal launch so zero values and non-live
semantics remain unchanged. For later batches use a fixed 4096-block grid with
block-stride iteration over the active list. Each terminal's sample and arithmetic
order stays identical. A barrier between loop iterations protects shared values.
The queue is refreshed each traverser, including graph replay, from the existing
prepared probability (which excludes own reach and includes folded opponents).
No host count readback; extra device storage is at most four bytes per terminal
plus one count. No CDF, batch, precision or particle changes.

First run adversarial exact comparisons against both the original and C01 on
fixed/locked, zero/recovery, graph replay and 2..8 opponent fixtures. Reject any
numerical or state discrepancy before timing. If those pass, use the existing
six-sweep/two-warmup paired benchmark with C01 control and C02 candidate.
A first large pair must improve complete runtime by at least 1% to admit the
remaining pairs. Retention requires the pass's three-pair 3% large gain and
small nonregression rule plus regression tests. No production deployment.

Build/test cap 240 seconds, each benchmark 180 seconds. One owned workload;
run07 live guard and frozen input/source hashes apply. Do not tune grid size
against the same measurement after seeing a failed screen without a new protocol.
