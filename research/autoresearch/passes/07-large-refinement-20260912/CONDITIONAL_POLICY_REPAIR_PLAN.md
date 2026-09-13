# Registered non-root conditional policy repair diagnostic

Research only, GPU full-game evaluation, no live writes or ordinary resume.
This is a bounded accuracy diagnostic, not an accepted optimization. It changes
selected decision policies only, unlike previous full-subtree or root repairs.

## Admission and preservation

Use the original 1,567,754-node sampled gamma15/64/seed42 saved policy at age
1050, with its original fit and canonical 1,024-particle evaluation. Fix the
existing 27 paths in broad-paths.json; do not replace failed paths. Require all
27 initially reachable, unconstrained action nodes with <=50,000-node subtrees.
Never alter root policy, regrets, iteration, constraints or any unselected
average entry. Batch validation must finish before any write. Rejection tests
include malformed probabilities, duplicate paths, roots, terminals, frozen or
locked nodes, cancellation, and a valid first/invalid last batch. Invalid
batches preserve both complete arenas exactly. Test selected GPU average
evaluation against the CPU correctness reference and exact save/reload.

Select twelve additional diagnostic paths BEFORE reading their action values:
collect siblings along the original paths, exclude originals and the root,
sort by (depth, lexicographic path), then keep unconstrained action nodes with
positive prefix mass and <=50,000 descendants. Stop after twelve. Record the
selection and initial audits. These nodes are held out from the target updates;
selection uses topology and reach only, never action loss or gate results.

## Policy change and selection

First normalize only the selected average entries to their represented policy.
This loses their history scale deliberately; verify the resulting global gap
against the original within 1e-5 before using this normalized baseline.

At each of at most three cycles, obtain all 169 conditional per-action values
at each original node under the current average continuation. For every hand,
form a best-response distribution over actions within 1e-8 bb of maximum value:
preserve their relative current probabilities, or use uniform weights if their
current mass is zero. Apply the same mixture alpha to every selected node and
hand, using alpha in [0.125, 0.25, 0.5, 0.875, 1]. Every trial starts from the
same cycle baseline; trials do not accumulate. Normalize each hand explicitly.

Recompute unrestricted full-game GPU gap and all 39 conditional audits for
every trial. A trial is eligible only if gap <=0.005 bb, all original/held-out
paths remain reachable, each held-out node's weighted action loss increases
by <=1e-5 bb from the original anchor, and no originally passing held-out gate
becomes failing. Among eligible trials choose the minimum sum of the 27
conditional mass-weighted action losses; require improvement >1e-6 bb, break
ties by smaller alpha. Do not select by the number of passing hands/branches.
Include the baseline as the no-change choice; stop if no improvement. Recompute
targets from the selected policy only on the next cycle.

Admission for further research requires gap <=0.005 and all 39 unchanged
per-hand gates, verified twice plus a separately loaded saved-game audit.
Unreachable paths fail, not skip. No threshold changes, added locks, or forced
actions. Retain all rejected candidates. No large speed claim follows from a
saved-policy repair; end-to-end timing must include original solving, repair,
checks and serialization. The historical 592.50-second solve is context only.

## Limits and execution order

1. Implement/test batch preservation, deterministic held-out selection, and
   pure target/mix arithmetic on a small fixture, including exact rollback.
2. Run native GPU equivalence and default release solver suite.
3. Build the diagnostic example, then run one sampled anchor with a 600-second
   process cap under run07's live-work guard. Independent audit cap 120 seconds.
4. If accuracy fails, reject this bounded rule; do not extend its cycle/alpha
   budget or run further seeds unchanged. If it passes, register fresh complete
   runs and broader coverage before claiming qualification or speed.

At registration, no non-root repair candidate has run. CPU work is reference
correctness/auditing only; this does not pursue CPU preflop performance.
