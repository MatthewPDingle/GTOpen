# Candidate follow-up: retain upstream learning history

Joint-v1 restarts the ancestor learner before every 25-iteration pass: regret
blocks are seeded from the current average policy at scale one, strategy sums
are cleared, and the local discount age starts at zero. This is explicit in
`research_refine_ancestors_gpu`; it is not ordinary continuation. Three sampled
cycles have increasing global gaps despite 27/27 local passes in cycles 1/2.
Repeated short warm-up is a candidate explanation, not an established cause.

After completing the registered v1 comparison, isolate this factor:

1. Retain a research-only ancestor state containing its allowed-node set and
   local discount age. Seed and clear only on initialization. Subsequent calls
   must preserve the previous ancestor regret/average history and continue that
   same local age. Never repurpose the saved parent global iteration.
2. Validate the same topology and selected ancestors on continuation. Reject
   changed fixed constraints, altered path sets, or an incompatible parent.
   Compact descendant updates remain disjoint from the ancestor arena blocks.
3. Before a large run, compare a continuous 50-step masked run with two 25-step
   calls using retained history and unchanged downstream policies. Check policy
   agreement, local age 50, unchanged fixed/retained arenas, and fresh unmasked
   final CPU/GPU values. This is a small correctness reference, not CPU timing.
4. Repeat exactly the v1 four-cycle/25-step/1,000-or-4,000 downstream schedule on
   the same compact inputs. Keep all 27 final path checks, the 0.005-bb global
   gate, full particles, and the per-input cap. Compare complete-cycle results
   rather than immediate per-branch passes.

Changing downstream strategies while retaining upstream learning is an
algorithmic experiment requiring qualification; this plan provides no
convergence or multiplayer subgame-safety guarantee. No live deployment.
