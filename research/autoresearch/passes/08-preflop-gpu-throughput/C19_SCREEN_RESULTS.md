# C19: scan interleaving passes standalone admission

The candidate preserves every output bit in 672 paired device cases. Loaded
registers remain 26; local and shared storage remain zero. Only the preferred
exact-reuse CDF writer's PTX changes, from 324 to 320 static instructions by the
registered audit's parser. The other 19 entries are identical, and control PTX
matches qualified R03. C19 passes its compiler admission gate.

**No speed improvement is established.** This is a test-only source generator;
normal solver selection, both saved sessions and port 56708 are unchanged.
Full-solver qualification and complete-work timing are the next stage.

The source loads all six independent 32-class tiles first, then interleaves
their five within-tile shuffle/add stages. It retains each tile's original
addition dependencies and combines carries in increasing tile order. This
exposes independent work to the compiler without shared staging, changed
precision, different samples or different CDF layout. The static instruction
count is not native scheduling, execution latency or hardware-counter evidence.

Coverage is seven input patterns plus a repeated dense recovery case, two
compact modes, two gate modes, seven batch/count pairs, and three offsets.
Patterns include all zero, dense, sparse, subnormal, last-hand-only, near-one
with tiny values, and tiny positive values. Every output and untouched guard
matches the retained implementation. Aliased, inactive and nonpositive-mass
rows remain untouched. Source archives preserve the tested implementation.

The guarded build/test finished in 133.469 seconds, including 2.40 seconds of
test execution. One pre-existing unused-import warning remains unrelated.
Frozen test executable: `target/c19-prefix-frozen.exe`, SHA256
`2709683b9e7b2a8a939719dba4dc1a134e0904a0cfc281a5b6d625a4754738d3`.

Next, integrate only a fresh-constructor research switch for the shared CDF
writer used by learning and cohort checks. Preserve all allocations and verify
complete arenas, roots, prefixes, recovery, fixed seats, stopping and captured
graphs before running the large control/candidate pair. Do not treat this
admission as retention or launch the extended campaign without its timing gate.

[Protocol](C19_PROTOCOL.md), [independent audit](check_c19_screen.py),
[immutable screen result](raw/c19-screen-verified.json),
[guarded runner](run_c19_screen.py).
