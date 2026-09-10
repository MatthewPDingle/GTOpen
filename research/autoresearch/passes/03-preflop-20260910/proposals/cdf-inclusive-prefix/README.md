# Inclusive CDF prefix layout proposal

Source-only, not compiled or measured. Apply either `inclusive-prefix.patch` to the current source or `inclusive-prefix-after-minimal.patch` after the pending compatibility-minimal proposal. They are alternatives, not cumulative. Both change the same shared `pf_multiway_sum` reader, covering preferred and minimal terminal entries. Do not combine shared-normalized staging or padding into this experiment.

The two CUDA writers now store inclusive prefix k at physical k-1. Logical CDF(0) is literal positive zero. Physical stride remains 170 floats and all GPU allocation/batch planning stays unchanged. Physical element169 is unused. CPU CDF storage is unaffected. All scan operations, their order, carry, divisions, samples, quadrature, and terminal accumulation remain unchanged.

`CoupledDeck::build` starts hi at lo+1 and caps it at169 before assigning each nonempty tie group. Thus 0 <= lo < hi <=169; upper-minus-one cannot underflow and both physical indices stay in0..168. Lower zero uses a conditional literal, preventing subtraction or a load before the row. Existing host-generated tables meet this invariant, including all-tied groups lo0/hi169. No synchronization changes or new divergent barrier exists.

## Expected benefit and limit

For consecutive stride170 rows, base modulo8 floats cycles0/2/4/6. Previously +1 displaced every full warp store from a32-byte sector boundary. Five full32-float tiles plus9 tail floats cover27 sectors per row at instruction granularity. Inclusive stores yield22 sectors in the aligned quarter and27 in other rows:25.75 average,4.63% fewer sector coverages. The separate zero store also disappears. This is not a DRAM traffic prediction: adjacent tiles share boundary sectors, cache/store combining can erase much of the difference, and the total unique row footprint is essentially unchanged. Reader conditional-zero selection can add instructions or alter scheduling, so a regression is plausible. No memory-capacity or CDF-batch improvement is claimed.

## Gates

`cuda_tests.rs` is a proposed test appended inside gpu.rs's existing tests module, with `reference-writers.cu` copied alongside kernels.cu for test inclusion only. It compiles frozen original writers and candidate in one module using production NVRTC options. Every one of169 logical prefix results must match bitwise for direct/normalized, compact/union, gate off/on, nontrivial permutation, zero mass, inactive slot, sample offset3, and counts1/7/23/31/32. NaN poison checks unused element169 and one extra capacity row. Reference kernels are test-only; do not load them in production.

Retain current all-opponent terminal exact-bit exports at equal batch size, CPU error gates, active/zero-reach poison tests, graph/non-graph equivalence, and preferred/minimal equality. Those test the shifted reader as well as writers; the new prefix test alone cannot prove the consumer correct. Keep32/7/1 and add23/31 to terminal controls where affordable. Whole-arena hashes and same-budget batch metadata remain exact comparison gates because allocation and batch choices do not change.

Compare independently rebuilt control/candidate with alternating paired runs on existing modeled and all-solver cases, record phase CDF/terminal and end-to-end time, and reject a material terminal or total regression despite isolated CDF improvement. No performance conclusion until measured.
