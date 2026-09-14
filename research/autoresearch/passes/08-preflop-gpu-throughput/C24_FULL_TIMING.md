# C24 full native-layout confirmation

Registered after the first short pair at commit 4f97039, before any six-row
timing. Use the same frozen executable and immutable input as the screen.
Six complete iterations, each followed by the full gap/EV check; two warmup
and four steady rows. Do not change the native planner, budget (23911 MB),
four-sample batch, HU cache, 1024 samples, model, ranges, precision or ordering.

The screen's guarded control took 245.281 seconds for three rows. Set the
full-run cap to ceil(245.281 * 2 * 1.2 / 60) * 60 = 600 seconds. This doubles
the entire measured process duration, then allows 20% margin rounded up to a
minute; it conservatively doubles fixed loading/fingerprint costs as well.
Apply exactly the same cap to both roles. No extending failed runs.

Run three pairs serially in this predeclared order:

1. Control, candidate.
2. Candidate, control.
3. Control, candidate.

Use separate full1/full2/full3 records. After every pair, require identical
six-row gap/EV checkpoints, full-arena fingerprint, initial buffer layout,
native batch, sample count and final iteration. Require the same qualified
kernel source/PTX and the expected 1,792,219,820-byte allocation saving.
Any correctness failure stops this series. Do not omit slow completed pairs.

The dashboard will replace the short screen with full-work ratios as they
arrive. They remain provisional: C24 retention still needs >=3% median benefit
and the supported comparison-fixture gates in C24_PROTOCOL.md. The separate
current-game graph must not be chained to historical small/large percentages.

The existing live-idle guard checks port 56708 every second and terminates only
the owned research workload if user work starts. No production restart.
