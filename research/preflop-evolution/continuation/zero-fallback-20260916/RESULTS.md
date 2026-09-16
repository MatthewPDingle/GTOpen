# N32: zero-own-range continuation control

The proposed uniform-prior fallback did not improve settling. Both runs continued the identical 1500-iteration learned-model checkpoint for another 500 iterations. Model coefficients, positive-range predictions and all other kernel logic stayed fixed.

| Arm | Final gap (bb) | Learning time (seconds) |
|---|---:|---:|
| control | 0.077251845 | 523.864 |
| uniform_prior | 0.077964347 | 529.691 |

The modified/control gap ratio is **1.009223**: the modified result is 0.92% worse. It misses both the fixed 25% interesting-reduction screen and the desired 0.005 bb gap. Neither run qualifies for deployment.

Independent audit rechecked 45 frozen inputs, both snapshots, all selected strategy normalizations, per-seat gaps, chip conservation and node-change calculations. The positive-range oracle matches exactly across 10,309 hand/action values. Sparse two-, three- and eight-player safety fixtures remain finite and conserve chips.

This is a single same-start controlled continuation, not repeated timing or an exact full-game exploitability measurement. A uniform prior for a player whose own current range is empty remains an assumption. The negative result weakens this particular switching explanation; it does not prove that every off-path treatment is harmless.

Production was not changed. Experimental policy saves retain incompatible semantics despite Balanced metadata and must not be loaded into the ordinary app.
