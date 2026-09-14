# C24 native saved-game timing screen

Registered before timing against integration commit a021f44. Input is the
immutable iteration-53 seven-seat game in `raw/c24-user-fixture.json`, SHA256
952ca57ffe9cf1b1f5b7582b1ffa4380f6ea7c2520e66d7f33902301aeb4341d.

Use one frozen executable for both roles, budget 23911 MB and the unmodified
native planner. Require its batch to equal four and its HU cache to remain
enabled. Candidate promotes that same private ordinary engine; control keeps
it. No batch, range, model, sample count or checkpoint changes are permitted.

The initial baseline is three complete iterations, each followed by the full
gap/EV check: two warmup rows and one steady row. Include input loading,
construction, all three rows, CPU synchronization and full-arena fingerprinting
in complete time. Cap the owned process at 300 seconds, with the live-idle
guard. Record each row immediately. Do not run the candidate if the baseline
does not complete. Before the candidate, record baseline duration and freeze
the identical three-row screen/cap decision in a receipt. Require exact row
metrics and final full-arena fingerprint, and at least 1% complete-time benefit
to proceed beyond this screen. This short run cannot retain the optimization.

If admitted, use six rows (two warmup, four steady) for three alternating full
pairs, with a cap registered from the baseline before those runs. Retention
still requires the C24 protocol's median benefit and comparison-fixture gates.
Report this current-game result separately from the historical small/large
benchmark graph; they are different problems. Compilation is not part of the
solver speed comparison. No production restart or solve is authorized by this
benchmark script.
