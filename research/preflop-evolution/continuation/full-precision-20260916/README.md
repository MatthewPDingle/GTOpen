# N20: retain the qualified predictor at full precision

N17's first joint repeat rejected its mixed-arithmetic implementation: maximum
inspected strategy change was 0.2014702111 and maximum player EV change was
0.0022197933 bb, exceeding the fixed 0.001 limits. The mixed implementation is
rejected; N17's incomplete timing experiment is not promoted. Its first full
precision timing was promising, but is not reused as a completed runtime gate.

Use N17's exact frozen double-precision source and the unchanged N15 predictor.
No arithmetic, features, weights, precision or accuracy thresholds change.
Require the existing N15 fresh400 accuracy pass and both double implementation
oracles. Additionally evaluate the ordinary and double candidate iteration-150
saves from N17 with both the original validated N15 warp implementation and
the N17 double implementation. Compare every emitted action value at every
inspected hand/node, require finite matching layouts and <=0.000002 bb maximum
absolute difference. The binary verifies evaluation does not mutate either
policy. This supplements rather than replaces the independent small-tree oracle.

Run three NEW original/candidate timing pairs, in orders original/candidate,
candidate/original, original/candidate. Keep 50 warm-up and 100 timed iterations,
the unchanged 410270-node source game and no concurrent CPU numerical work.
Require complete ordinary numeric arenas exactly equal to N04 baseline in
each repeat and complete candidate numeric arenas exactly equal across repeats.
Report all times; require median candidate overhead <=10%. No selection among
failed mixed-arithmetic outcomes, averaging of models or relaxed tolerances.

If this passes, apply the unchanged four-context, 200-fresh-reference changed-
policy protocol through the optimized adapter, labelled N20. Every context must
improve value error >=15% over Balanced and regress <=10% versus the prior
predictor. Neither runtime nor the numerical oracle replaces that accuracy
check. Follow-up stability diagnostics remain conditional on all gates passing.

The live app, model cache and production executable remain unchanged. A single
research controller owns GPU work until it exits, including child-stage gaps.
Stop new stages at the fixed20:49:02 UTC deadline; begin changed-policy work only
with >=60min remaining. Save metadata is still Balanced and cannot be loaded in
the ordinary app. Full-game convergence, exact multiway equity, wider postflop
trees and untouched-scenario accuracy are not established by this protocol.
