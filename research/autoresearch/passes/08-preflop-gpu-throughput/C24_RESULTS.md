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

## Ordinary GPU integration

The research-only ordinary path now passes four numerical tests (32.687 seconds,
after a separate 159.766-second compilation). All 32 combinations of player
counts 3/4/7/9, locked or unlocked seats, and batches 1/4/5/32 match complete
regrets, strategy arrays, root values, gaps and EVs across three rounds. Both
learning and evaluation graphs are exercised. Controlled fixtures set the
same batch on both paths; this does not yet prove the real saved-game layout.

All terminal values match through zero-reach and recovery cases. Saved games
are byte-identical. An actual mid-sweep stop matches an ordinary sweep prefix,
and three continuation rounds match after reload. Actual CUDA allocation
failures at stages 1/2/3 leave no owned allocations behind; recovery and budget
refusal pass. All 36 existing PTX entries remain byte-identical. The new writer
uses 25 registers, the terminal 40 registers and 44 bytes of shared memory;
neither uses local-memory spill storage.

The preparation helper initially hit Windows' default text encoding while
reading gpu.rs, before any build. Its one partial module declaration was
verified and restored; explicit UTF-8 fixed the helper. The first build and
numerical run both passed. See `check_c24_integration.py` and
`raw/c24-integration-verified.json` for independently checked evidence.

The user's stopped iteration-53 game was saved through the normal API and
copied into an immutable research fixture (7,712,942,992 bytes). Its checksum
is `952ca57ffe9cf1b1f5b7582b1ffa4380f6ea7c2520e66d7f33902301aeb4341d`.
The original preflop root/session, postflop state and report status remained
unchanged. The private save is not checked into Git; its manifest is in
`raw/c24-user-fixture.json`. No user solve was started or restarted.

Next: native-layout timing against this exact save. No speedup is yet claimed.
