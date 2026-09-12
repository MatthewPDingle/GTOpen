# GPU opponent-reach exploration: registered first experiment

Earlier local repairs damaged upstream/global consistency. Test whether modest
early coverage of low-reach branches helps ordinary full-tree learning avoid
that repair step. This is a heuristic, not a proven multiway convergence method.

For traverser p, at each learning opponent node (actor != p, source == learning),
replace its down-pass reach multiplier sigma with
`(1 - epsilon) * sigma + epsilon / legal_action_count`. Use
`epsilon = 0.01 * max(1 - completed_iterations / 250, 0)`.
The traverser's own reach and strategy remain unperturbed, so its existing
regret/average updates learn against the temporarily mixed opponents. Frozen
and forced/profile/point-locked policies remain exact. This does not claim that
every traverser is solving one common perturbed equilibrium. After iteration
250, ordinary native updates resume; epsilon-zero arithmetic is exactly native.

Implement as a research-only correction immediately after each down-pass level,
before descendants read reach. Use one stable device epsilon scalar updated
outside graph capture each iteration. Initially favor a simple extra kernel
over native-kernel changes. Global evaluation uses native reach, no correction,
all canonical 1,024 particles and all learning seats. Preserve pots, investment,
rake, calibrated heads-up leaves, regrets, average rules and discount schedule.
Reject combinations with other experimental optimizers, CVs, masks or custom
root ranges. No live-server mutation or deployment, no CPU speed optimization.

Before learning: independently reconstruct every reach block on a small fixed
fixture, covering the traverser's unchanged actions, learning opponents, frozen
seats, point locks and impossible branches. Check zero-epsilon exact equality.
Check captured/eager learning across the decay boundary, frozen averages and
full CPU/GPU final evaluation (CPU correctness reference only).

Registered screen: fresh same-binary six-player gamma15/64 controls and candidates,
seeds 42 and 314159, limit 1,000, full checks every 25, <=0.005 bb twice. Runtime
cap 600 seconds each. Both candidates must converge, with each total time <=1.25x
its control. Count the two required passing checks only after iteration 250,
when complete learning iterations have used epsilon zero. Earlier full checks
remain recorded but cannot trigger convergence. Require these conditions before
large qualification. This permits a bounded overhead to
investigate conditional quality; it is not itself a speedup criterion. Preserve
all failures without retuning epsilon, decay, seeds or the accuracy threshold.

If passed: initial existing eight-player user-session fixture, seed 42,
gamma15/64, limit 1,500, full checks every 50, <=0.005 bb twice, cap 1,200 seconds,
exact saved-state roundtrip and independent all-27 conditioned audit. Large
success requires both the native global gate and all existing local gates.
Further seeds, constraints and matched large controls remain necessary before
deployment, even if the initial screen passes.

Post-screen diagnostic: if the speed gate fails, retain that rejection. Audit
the six existing historical small-fixture paths from P5 six-s64-a-local-v3
against each control/candidate's own saved policy. Do not choose paths based on
the exploration results, and do not use this diagnostic to waive the speed
gate. It asks only whether the extra training bought any conditional accuracy
on an already established path set. CPU execution here is an independent
correctness reference, not CPU performance work.
