# C07: bounded three-player check cohorts

Registered before implementation or new GPU measurements. Baseline is retained
C01 plus optional, disabled D03 tracing. Reuse the archived C06 mechanism with
at most three players per cohort and a 20,500 MB cohort budget, including the
256 MiB reserve. The ordinary layout still receives 23,000 MB: batch 32, all
1,024 particles and the HU cache must match the control. No reduced precision,
sampling, learning updates or accuracy work.

Choose minimum static union rows among fitting partitions, then allocated bytes
and lexical masks. The independent D05-based preflight predicts large masks
[161,70,24], 1,810,900 static rows, 1,655,762 exact unique rows and peak
20,446,750,580 bytes. This is 31.56% fewer check CDF rows, above the 25% admission
gate. Verify real constructor allocations against the preflight before timing.

Retain C06's exact prefix, all-terminal, full arena, root, capture/replay,
frozen/locked-seat, zero/recovery and stop/sync tests at batch 5 and 32. Add
seven-player coverage, rejection of a tree without multiway leaves, and
restoration of owned buffers/state after explicit Result errors. No runtime
test downloads or timers in the production candidate path.

Use the existing frozen benchmark: six iterations, first two warmups, accuracy
check each iteration, complete initialization and synchronization included.
Every checkpoint and final full arena fingerprint must match. First large
control/candidate screen rejects at complete-time ratio >=0.99. If it passes,
complete three alternating-order pairs on each large and small fixture. Retain
only >=3% median large complete-time gain, consistent direction and <=3% small
regression, followed by native GPU and default solver regressions.

Record read-only GPU memory and clock snapshots outside each timed invocation;
these cannot establish residency during execution. Run one guarded workload
at a time using run07. Build/test cap 240 seconds; benchmark cap 180 seconds.
No source edits, builds or other GPU work during timing. Hash sources, inputs
and executable; preserve rejected code and raw outputs. Never restart or write
to port 56708. A throughput win alone does not complete the convergence goal.
