# D050 independent terminal review

**Scoped compiler capacity and PTX prerequisites pass.** Ten raw markers contain the fixed eight resource rows, from one successful Rust compile and one successful query. The frozen source/runner/dependency/compiler/DLL/binary/output provenance and all162 unchanged accepted E020 source hashes were verified. No kernels or solves ran.

Both kernels use38 registers,0 local bytes and1040 static shared bytes. For rainbowP0/P1, theoretical blocks change12→6 while warps remain48; the wide-turn case remains4blocks with warps16→32; the1326 upper-bound case remains3blocks with warps12→24. All requested thread/shared sizes fit and residency is positive. These are resource tradeoffs, not speed measurements.

Concrete dependency inspection confirms candidate physical256 retains128 logical chunks, +0 accumulators,128 writes, the full128 serial recurrence and original base-add order. Upper lanes skip scan state work and join every barrier. The629-line post-scan hand calculation matches under consistent register/label renaming, with unchanged floating dependencies and no FTZ change. Eight other PTX entries and the up_show ABI are byte-identical. See ptx-review.md and ptx-alpha-evidence.json for exact before/after references and scope.

This is neither numerical equivalence nor performance proof. Any direct old128/new256 kernel test, production activation and complete-cycle qualification require separate authorization and evidence.
