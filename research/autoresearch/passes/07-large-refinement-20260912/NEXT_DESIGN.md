# Compact GPU branch refinement: implemented, not qualified

The compact prototype passed its numerical tests and completed both large-game
runs. Both final results passed only 26/27 conditional paths and failed the
0.005-bb global gate. See COMPACT_RESULTS.md for timing and accuracy evidence.
Subsequent global restart and ancestor-only repair also failed qualification;
see RECONCILE_RESULTS.md and ANCESTOR_RESULTS.md. These experiments have not
established a deployable end-to-end improvement.

Next, inspect current/average arena scales and uniform-fallback counts on the
original native and sampled saved solves. Tiny incoming branch mass alone does
not prove numerical cutoff failure: direct per-hand learning-state evidence is
needed before changing normalization or thresholds. Keep the same 27-path and
global accuracy gates. CPU speed comparisons remain excluded.

The CPU refinement experiment supplies a correctness reference under fixed,
normalized incoming ranges. The research GPU path now supplies these ranges
at the compact root; the production GPU path retains its unconditional prior.
The CPU performance comparison was canceled at the user's request.

The implemented extraction design was:

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
