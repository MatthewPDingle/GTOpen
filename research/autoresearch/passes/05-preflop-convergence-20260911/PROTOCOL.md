# Preflop convergence feasibility

Base: 92c86ed. Production port 56708 is read-only. No preview milestone counts.
Primary metric: elapsed time to two consecutive full-1024 learning-gap checks <=0.005 bb.
Iteration, initialization, checks, save/readback and independent audit are recorded separately.
The target model remains coupled_deck_v1, not exact physical equity or full postflop solving.

Registered first screen: unchanged DCFR; HS15 and HS30 (equation 4,
https://arxiv.org/html/2404.09097v2, fixed horizon 1000); gamma15-only ablation;
DCFR with 128/256 randomly shifted particles per player update. Test a combined
candidate only after the independent effects are measured. Sampling uses a uniform
cyclic offset from SplitMix64; each particle has inclusion probability K/1024.
The arithmetic sample mean is unbiased for the full finite terminal mean at fixed
input reaches. This does not itself prove unbiased downstream strategy updates or
multiplayer convergence. Seeds 42, 314159, 90210 are registered repetitions.

Full checks restore canonical particle tables and do not change regrets/sums.
No action pruning, tree simplification, warm start or fitted value surrogate.
HS is applied at the existing engine's end-of-iteration discount point; schedules
are inspired by the cited method, not an assertion of multiway theoretical guarantees.

Screen small three-player all-solver, then six/eight-player full action trees and
adaptive model fixtures. Small results cannot establish large-game acceleration.
Reject candidates with nonfinite/illegal policies, save changes, failed independent
full-model checks, or increased probability >0.1 on >0.1bb inferior actions in
material hand/node contexts (minimum arriving hand mass .0025). Compare local
action quality against a high-accuracy full reference; report baseline failures too.
Two equal checks are a stability screen, not proof of equilibrium in multiplayer games.

One owned hardware process at a time. A guard polls live preflop/postflop/report
status, terminates only its owned benchmark if user work starts, and records the
reason. Failed/partial runs are retained, never counted as completed speedups.
No production deployment unless later validation justifies one. Raw outputs,
inputs, executable and source hashes are preserved. Research updates are pushed.
