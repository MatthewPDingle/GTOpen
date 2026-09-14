# C24: four-sample static tables

The standalone GPU layout screen passes. This is not integrated into complete
ordinary solves yet and is not a measured speed improvement.

The test compares packed and original tables across five rank distributions,
all partial four-sample counts, early and late sample offsets, compact/union
indexing, active gating, duplicate aliases, empty and sparse inputs, signed
zero and subnormal values. Terminal tests cover two through eight opponents
and zero/nonzero incoming accumulators.

- 3,840 prefix cases; 1,185,984 required prefixes compared bit-for-bit.
- 53,760 terminal vectors; 9,085,440 hand values compared bit-for-bit.
- 4,346,688 sentinel storage positions verified unchanged.
- The real four-sample row stride is 333 floats rather than 680.
- CUDA source, compiled PTX and kernel resources are identical to the qualified
  C23 standalone kernels. Only the host map's row capacity differs.

The guarded build plus test took 151.5 seconds; GPU qualification itself took
9.24 seconds. These are development costs, not benchmark timings. A completed
run and independent checker verify the evidence and exact case matrix.

The production map constructor still selects 32 samples. The new four-sample
test is opt-in under the research feature. The qualified R04 executable is
unchanged; live port 56708 remains R03 with the stopped user game intact.

Next is a research-only ordinary-path constructor and writer/reader dispatch
without the cohort and duplicate-hash dependencies. Full checkpoint equality,
stop/reload replay, memory failure recovery and same-problem runtime comparisons
must pass before retention or deployment. See `C24_PROTOCOL.md`,
`check_c24_screen.py`, and `raw/c24-screen-verified.json`.
