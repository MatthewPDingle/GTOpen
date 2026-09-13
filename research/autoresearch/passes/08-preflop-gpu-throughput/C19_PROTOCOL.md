# C19: interleaved independent CDF scan tiles

Registered before compilation. GPU preflop only; retained C14/R03 baseline,
port 56708 read-only. Distinct from rejected shared normalized staging, padded
CDF writes, predicated additions and narrower writer indices.

Each particle's 169-class scan has six independent within-tile prefix scans.
The original carries combine those scans in increasing tile order. Load the
six lane values first, interleave each shuffle/add step across all six values,
then perform the original carry/store sequence in increasing tile order.
Preserve every arithmetic dependency, rounding mode, padding zero, index,
alias, probability, allocation, sample and policy. Only rewrite the preferred
exact-reuse CDF writer. No shared memory or barriers; no fallback changes.

Hypothesis: independent scan chains expose latency overlap. The compiler may
already do this, or extra live values may reduce occupancy. Not a work-volume
reduction or a claim of order-of-magnitude speedup; CDF construction is roughly
half of retained learning time, so any complete gain is inherently bounded.

Stage 1, cap300 seconds: test-only source rewrite and device/compiler screen.
Compare every CDF output bit and guards against retained compiled source on
compact/noncompact layouts, aliases, gates, zero/recovery, dense/sparse/small
positive/subnormal/extreme normalized inputs, sample offsets0/17/992 and
batch/count pairs1/1,5/1,5/5,32/1,32/7,32/31,32/32. No output overwrites.
Archive sources/PTX/resource records. Control PTX must match R03; only the
writer entry may differ. Require exact outputs, zero local spills, at most
48 registers and no more than20% extra static PTX instructions in that writer.
Unchanged PTX is a no-op rejection. These are admission gates, not speed tests.

If admitted, separately integrate the switch fresh before capture, repeating
whole-arena/roots/prefix/zero-recovery/frozen/stop/graph tests and both immutable
saved allocations. Then the registered complete-work large first pair rejects
at ratio>=0.99; a survivor needs three alternating pairs per fixture, median
large gain>=3%, small regression<=3%, exact checkpoints/fingerprints and full
default/native regressions. Include construction/allocation/compilation cost.
No stage2 runs until stage1 is audited. Reject and archive only candidate code.

One guarded workload at a time via run07; no source edits during execution.
No driver changes, sample reductions, precision changes or live deployment.
