# C13 proposal: bounded 32-bit element indices in terminal evaluation

Not implemented or measured. Retained baseline remains C01+C07+C09; R01 is
selection qualification, not a new arithmetic kernel or speed baseline.

D08's linked assembly contains substantial 64-bit address arithmetic, but static
counts do not identify a runtime stall. Inspecting `pf_multiway_sum` shows that
it stores element indices in `size_t` and repeatedly adds per-sample and hand
offsets. The large retained CDF is about 14 GB, yet contains fewer than 2^32
**float elements**. Byte pointers still require 64 bits. This distinction may
permit narrower integer work without narrowing any pointer or float value.

Prototype only the terminal helper's element-index representation: use `u32`
for opponent row bases and the per-sample element offset when the entire CDF
allocation is proven to contain at most `u32::MAX` elements. Widen when forming
the actual byte address. Leave the CDF producer, tables, capacities, samples,
opponent order, Gauss points and sequential float accumulation unchanged.
Guard construction before enabling either exact-reuse or cohort kernels; refuse
unsupported capacities rather than wrap. The existing normal path stays intact.

The generated terminal copies and the helper must use consistent types. Apply
the source transformation to the complete generated source, not just the base
helper while leaving its callers with `size_t` shared arrays. Validate rewrite
counts and kernel argument compatibility. Do not change unrelated array indices.

Before timing: check the index bound independently with wide host arithmetic at
zero, final row/hand/sample, and just beyond the maximum. A GPU address-arithmetic
witness can test near-limit indices without allocating an oversized buffer.
Then run the established all-opponent, odd/partial-sample, zero/recovery, locked,
frozen, captured-execution and stop comparisons; require exact terminal and full
arena agreement. Record register/shared/local allocation and unchanged global
device bytes. Reject incorrect code before any speed screen.

Then compare the immutable large save against C09 with the established six-sweep
complete-work benchmark. First-pair screen requires at least 1% less complete
time. Retention still requires three alternating pairs, at least 3% median large
benefit, no more than 3% median small regression, exact checkpoints and arenas,
and full regressions. Compiler count changes alone do not count as a gain.
Run through the serial run07 guard; no source edits during work and no 56708
deployment. Archive any rejected code and all failed outcomes.
