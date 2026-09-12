# Candidate next step: compact GPU branch refinement

This is a design proposal, not an implemented or measured speedup.

The CPU refinement experiment gives a reference for solving a selected branch
under fixed, normalized incoming ranges. The GPU engine currently initializes
every root seat with the unconditional class prior. A compact subtree cannot
be passed to it correctly without also supplying the actual incoming ranges.

A possible research implementation would:

1. Extract only the selected subtree, preserving player identities, live/folded
   masks, investments, pot and calibrated continuation metadata. Remap node,
   child and arena offsets, plus point locks; preserve frozen/profile policies.
2. Add a research-only per-seat root-range initializer. Update root EV weighting
   consistently; a correct traversal with the wrong root weighting is not a
   valid convergence test.
3. Start fresh local learning arenas and a separate local iteration age, just
   as the CPU reference does. Copy only authorized mutable arena blocks back
   to the offline parent; never mix local and global iteration ages.
4. Compare terminal values, per-hand action values and learning updates against
   the full-particle CPU branch reference. Include fixed seats, point locks,
   folded opponents, true-zero and tiny-positive incoming reaches.
5. Benchmark end-to-end extraction, upload, full-particle learning, quality
   checks and copy-back on the registered one/two/three-limper branches.

Do not change the live engine or claim an improvement until those checks pass.
The negative GPU control-variate result does not establish that compact GPU
branch refinement will also fail: it is a different reduction in work.
