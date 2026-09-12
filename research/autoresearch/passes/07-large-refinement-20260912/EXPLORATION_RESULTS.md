# Early opponent-reach exploration: rejected

Research only. Port 56708 was not mutated or restarted. The implemented
heuristic mixes learning opponents' down-pass reaches with a uniform legal
action distribution, starting at 1% and decaying to zero at iteration 250.
The traverser, forced/profile policies and frozen seats are not mixed.
Full evaluation always uses native reach and all 1,024 canonical particles.

Two targeted tests passed: independent reach reconstruction with frozen/locked
and impossible branches, exact native behavior at epsilon zero, native
evaluation with positive epsilon, and captured/eager learning through the decay
boundary. Final CPU/GPU comparisons used CPU only as a correctness reference.
All 6 postflop and 13 preflop GPU regression tests passed, followed by the
default solver regression suite. Guarded durations including compilation:
69.515 seconds targeted, 64.937 seconds GPU regressions, 126.500 seconds default.

Same-binary six-player gamma15/64 learning, full checks every 25, 0.005 bb target
twice. Candidates could count passing checks only after exploration had ended.

| Seed | Control iterations / seconds | Exploration iterations / seconds | Candidate full gap |
|---|---:|---:|---:|
| 42 | 275 / 3.076 | 350 / 4.269 | 0.004086 |
| 314159 | 325 / 3.557 | 350 / 4.182 | 0.004254 |

Both candidates converged and round-tripped their saved arenas exactly.
Seed 42 took 1.388x its control, exceeding the registered 1.25x screen cap;
seed 314159 took 1.176x. No large trial followed the failed screen. These short
measurements do not establish a production runtime ratio.

## Conditional diagnostic after the rejected screen

The six paths were reused verbatim from the historical P5 small-fixture audit,
not selected from candidate results. Each policy was independently audited
under its own arriving ranges. This measures its conditional one-action quality,
not full subgame best response or cross-policy EV under identical ranges.

All four saved policies passed **2 of 6** conditional checks. The two passing
paths were `[2,0,0]` and `[2,0,0,0,0]`. Exploration did not convert any failing
path into a pass. Individual worst-hand probabilities on actions losing more
than 0.1 bb improved in some cases and worsened in others; all are retained in
the raw audits and verified summary. Thus the extra learning did not establish
a conditional-quality benefit on this established path set.

`check_exploration.py` independently recomputes global gaps and post-decay
convergence streaks, controls, runtime gate, save-roundtrip flags, historical
path membership, and every conditional hand/action gate. It reports verified
evidence with `screen_pass: false` and no large qualification result.

Next investigate compatibility of compact branch histories with full-game
continuation. The existing compact API deliberately solves from fresh local
histories under normalized incoming ranges and reports
`normal_global_resume_supported: false`. A useful next test is whether local
counterfactual increments and average weights can be mapped back into full-game
units without changing probabilities or fixed policies. That would be a new
research continuation method, not evidence that current offline copyback is a
production defect. Timing improvements and the joint global/conditional gates
remain unproven.
