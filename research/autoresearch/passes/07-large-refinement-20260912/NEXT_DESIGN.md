# Candidate next step: compact GPU branch refinement

The research prototype compiled and passed the eight refinement tests and two
control-variate numerical tests. The compact comparison covers raw/calibrated
payoffs, nonuniform incoming ranges, frozen/locked policies, conditional EV and
gap weighting, and unchanged parent arenas. Large-game GPU timings and final
accuracy audits remain pending. No speedup has been established yet.

The CPU refinement experiment supplies a correctness reference under fixed,
normalized incoming ranges. The research GPU path now supplies these ranges
at the compact root; the production GPU path retains its unconditional prior.
The CPU performance comparison was canceled at the user's request.

The implementation and qualification plan are:

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
