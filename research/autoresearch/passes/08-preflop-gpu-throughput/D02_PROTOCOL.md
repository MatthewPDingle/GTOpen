# D02: remaining sparse distribution screen

Starting from retained C01 (edb415e), count exactly nonzero classes in each
normalized GPU distribution from the same frozen native saves. Use both current
and average play and all traversers, preserving D01's positive-opponent mask.
No iterations or model changes; assert all learning arenas and age unchanged.

Report histograms separately for all active slots and exact unique distributions.
The unique histogram estimates the work left after ideal exact CDF reuse.
Do not count the already-eliminated duplicate work as a second opportunity.

Admit a sparse-kernel prototype only if at least 20% of the large game's unique
current-play distributions have one or two nonzero classes. Report the average
policy result separately since checks can behave differently. Otherwise reject.
This inventory is not a speedup. A prototype would still need identical terminal
bits and paired complete benchmarks; sparse direct formulas must preserve
prefix-scan rounding and equal-mass subtraction.

Build/classifier cap: 240 seconds. Each saved inventory: 180 seconds.
Use run07's serial workload/live-app guard. Port 56708 stays read-only.
