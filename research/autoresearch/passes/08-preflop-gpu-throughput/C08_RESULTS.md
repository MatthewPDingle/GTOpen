# C08 rejected: cooperative terminal CDF staging

The first large paired run took 66.246 seconds with C07 and 81.213 seconds
with staging: **22.59% slower**. Warm iteration and check median ratios were
1.2453 and 1.3297 respectively. This failed the registered first-pair screen,
so no extended timing campaign or production-regression qualification ran.

The prototype copied each opponent's 170-value probability row into shared
memory once per particle, then performed the existing hand-specific gathers
and quadrature from those rows. All 192 threads participated in barriers;
only valid hand threads calculated values. It affected both C01 learning
terminals and C07 shared-check terminals. Constructor variants compiled the
required kernels directly, avoiding extra runtime kernel replacements.

Five cohort tests passed, including original/C01/C07/C08 comparisons of all
terminal outputs, prefix values, full learning arenas and root values, 3–9
players, all 2–8 opponent counts, batch 5/32, zero own/live/folded-opponent mass,
recovery, frozen/locked seats, repeated checks, graph replay and stop/sync.
Four existing exact-reuse tests also passed. Large paired checkpoints and final
arena fingerprints matched C07 exactly. Small and large allocation checks
matched all C07 global buffers and the unchanged grouping/cache plans. The
candidate added 5,440 bytes of shared CDF storage per block, plus its existing
shared metadata; driver/module resource overhead is not counted as zero.

The experiment does not establish whether barriers, bank conflicts, occupancy
or already-effective hardware caching caused the regression. The source-level
load change was not a measured memory-bandwidth improvement. This was a distinct
consumer-side experiment, not a rerun of the earlier rejected shared normalized
input staging in the CDF producer.

Rejected code is archived under artifacts/c08-rejected and mapped by
[c08-source-map.json](artifacts/c08-source-map.json). All prototype source edits
were removed, restoring retained C07 plus D06's test-only tracing. The live app
on port 56708 was untouched. [check_c08.py](check_c08.py) verifies sources,
inputs, frozen executable, allocation totals and numerical/timing evidence;
[raw/c08-verified.json](raw/c08-verified.json) records the rejection.

Frozen local executable target/c08-benchmark-frozen.exe, SHA-256
39904cdd592cd12b8a8cb30bc3b530847c29bd02aed02c235b817e56e42867fa.

Next: test partial unrolling of the terminal sample loop, an earlier unrun
proposal, without shared staging or another accumulator. The aim is to expose
independent loads to the compiler while retaining sequential sum order; it
still needs direct partial-count and full solver equivalence tests.
