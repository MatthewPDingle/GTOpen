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

## First native-layout timing pair (provisional)

The registered three-row screen completed with the native planner's four-sample
batch and HU cache enabled on both paths. Control complete time was 233.456371s;
C24 was 174.5494531s: **25.23% less complete time**. Complete time includes loading,
construction, three iterations with gap/EV checks, synchronization and the full
arena fingerprint. Compilation took 159.015s and is excluded from that comparison.
The process guard measured 245.281s and 184.531s respectively, both under 300s.

All three checkpoints have identical gap/EV values; the 1,928,235,582-entry
regret/strategy fingerprint matches (`e21ec20d684faafa`). Both finish at iteration
56 from the same iteration-53 input, using 1,024 samples. Native candidate source,
PTX and kernel resources match the qualified integration artifacts. Device
allocations fall by exactly 1,792,219,820 bytes, with only the CDF buffer replaced
and its immutable metadata added. No solve on port 56708 was started or restarted.

This is one short screening pair, with two warmup rows and one steady row. It
passes the 1% screening threshold, but is **not retained or deployed**. Six-row
alternating pairs and the comparison-fixture gates remain. The dashboard shows
the first point in a separate **Memory-limited (C24)** view at 74.77% of this
fixture's ordinary-path control. It must not be chained onto the old large
benchmark's 68.35% result: these measure different games and GPU schedules.

Evidence: `check_c24_native_screen.py`, `raw/c24-native-screen-verified.json`,
`check_c24_dashboard.cjs`, and the paired `c24-current-*-screen1` raw records.

## Full confirmation, first pair

The registered six-row workload confirms the short screen: 438.2881368s control
versus 328.7690152s C24, or **24.99% less complete time**. All six checkpoint
gap/EV values and the final full-arena fingerprint (`40005fb7a8048755`) match.
The first three checkpoints also reproduce the short screen. Both roles use
the same frozen executable, input, native four-sample plan, HU cache and 1024
samples, and finish at iteration 59. Source/PTX and device-allocation checks
pass. The guard measured 449.265s control and 338.859s candidate, below the
predeclared 600s cap.

The dashboard now uses this full-work pair instead of combining it with the
three-row screen. C24 remains provisional. Two more alternating pairs and the
supported comparison-fixture checks remain. See `C24_FULL_TIMING.md`,
`run_c24_full.py`, `check_c24_full.py`, and `raw/c24-full-verified.json`.

## All three native pairs

The two additional pairs pass all checkpoint, full-arena fingerprint, immutable
source/PTX and allocation checks. Across three alternating pairs, median complete
runtime reduction is **24.94%**, with paired reductions from **24.44% to 24.99%**.

| Pair | Order | Control seconds | C24 seconds | C24 / control |
| --- | --- | ---: | ---: | ---: |
| 1 | Control, candidate | 438.2881368 | 328.7690152 | 0.750120726 |
| 2 | Candidate, control | 438.3862128 | 329.0705428 | 0.750640721 |
| 3 | Control, candidate | 448.2777430 | 338.7253963 | 0.755615021 |

All six processes finish at iteration 59 with fingerprint `40005fb7a8048755`.
The third pair ran somewhat slower in both roles; it is included in the result.
The dashboard shows the three-pair median and range. C24 remains provisional
until the supported comparison-fixture gates pass. Their ordinary-path controls
are registered separately in `C24_COMPARISON_TIMING.md`; these independent
comparisons must not be chained into the historical C23 benchmark percentages.
