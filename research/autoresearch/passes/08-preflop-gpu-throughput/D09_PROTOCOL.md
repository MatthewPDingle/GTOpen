# D09: bounded indices in the CDF writer

Previous goal turn made progress: R03 normal-server integration was qualified
and pushed. Port 56708 stays read-only. Continue GPU performance research from
53288a0; do not repeat C05 layout changes or C12 scan arithmetic experiments.

Hypothesis: C14 narrowed terminal reads, but the exact-reuse CDF writer still
carries a 64-bit element base through its stores. Narrow only that writer base
and additions when the entire CDF fits u32 elements. Convert the final element
index to size_t before addressing; byte pointers remain 64 bit. Do not change
normalized loads, rank order, scan additions, samples, tile layout or dispatch.

First run a test-only compiler/device screen with no runtime dispatch changes.
Compare exact CDF contents, untouched inactive/aliased/padding outputs and guard
values across compact/noncompact indexing, gate on/off, zero/recovery inputs,
batches 1/5/32, partial counts and late sample offsets. Reuse bounded-address
arithmetic proof with witnesses above 4 GiB in byte offsets. Record direct-loaded
register/local/shared attributes and archived control/candidate PTX and source.
Control PTX must match retained C14. All other PTX entries must stay unchanged.

Admit a separate C15 full-work prototype only if exact tests pass and the writer
uses fewer registers or fewer integer-address PTX instructions, with no local
spill increase. This is compiler evidence, not a measured speedup. If admitted,
C15 must include startup, first large pair <0.99, then three alternating pairs
with >=3% median large benefit and <=3% small regression. No retries to seek a
pass. Register C15 before its actual timing. Keep all failed results.

Use serial run07 live guards and bounded caps. This test-only diagnostic does
not require repeating unrelated full regressions. Keep the qualified production
binary immutable. Update the dashboard and push the evidence to GitHub.
