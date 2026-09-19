# Physical verification of the near-indifferent responses

Secondary diagnostic registered before sampling. Check TT and AKo, identified
by the exact affine response audit as nearly indifferent in the starting
range state. Use 32 million independent physical deals per hand, 40 batches
of 800,000, deterministic seeds `9026191900 + hand_index*1000 + batch_index`.
Deal seven other holdings and a shared five-card board without replacement.
Evaluate actual seven-card poker ranks; do not use the cached equity table.

Use the frozen earlier preflop policies and the compatible fresh root jam
policy, setting AA to jam with probability one for the q=0 baseline. Accumulate
AA and non-AA opponent holdings separately. This supports paired estimates
for all five registered AA fractions by multiplying the AA component by 1-q.
Compare both two-live-hand conditioning and conditioning on all six earlier
folds. Fixed LJ cards make LJ's own earlier action likelihood cancel.

Report call values relative to folding: 397.5 times equity minus 182 bb.
Report batch delta-method standard errors and approximate 95% intervals.
These intervals quantify physical Monte Carlo error only. Keep the complete
fixed ranges; no postflop preparation floor or trimming applies here.
Four CPU threads, no production access or saves. This verifies all-in prices;
it neither re-solves preflop policies nor certifies an equilibrium.
