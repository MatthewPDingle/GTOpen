# Large full-particle normalized-regret qualification screen (v1)

Prerequisite: the independently verified small full-particle normalized run
passed the unchanged combined gate at iterations 925 and 950. This experiment
asks whether that quality transfers to the user's large fixture. It is not
a claim that full-particle learning provides the required tenfold speedup.

One registered candidate: `03-preflop-20260910/user-session.json`, fresh
histories, eight learning seats, 1,567,754 nodes, calibrated HU continuation,
canonical coupled_deck_v1, all 1,024 learning particles, gamma15 (constant
exponent), horizon 1,500, seed 42, dynamic regret normalization enabled.
No sampled learning, control variate, exploration, branch refinement, warm
start, pruning change or payoff changes. GPU budget 20,000 MB; allocation
failure is a failed admission, not permission to disturb the live server.

Hard ceiling: 1,500 iterations and 10,800 seconds for the guarded process.
The historical large native run required 1,050 iterations merely for its
global gate, so this initial large ceiling differs from the small fixture's
1,000-iteration screen. It is registered before any large outcome and must
not be extended after failure. Evaluate every 50 iterations, starting at 50.

Every check uses all 1,024 canonical particles for the native global gaps,
followed by device-history publication and all 27 paths in `broad-paths.json`,
conditioned before CPU reference evaluation. CPU work is correctness only.
Require finite, nonnegative eight-seat gaps summing to <=0.005 bb and all
27 conditional gates: relevant hand mass >=0.0025, probability on actions
losing over 0.1 bb <=0.1. Unreachable paths fail. Stop after two consecutive
combined passes, or at the registered ceiling. Preserve per-hand evidence at
each check on disk even if the process later aborts; partial output is never
a qualified run or an ordinary resumable state.

Record setup, GPU iteration, canonical evaluation, publication, conditional
audit, serialization and total times. On clean completion save the final
research game, verify exact arena roundtrip, then independently audit the
loaded final game. Successful qualification requires all verification too.
The canonical model and one-action conditional checks retain their existing
limitations; this is not exact physical poker or a full subgame BR audit.

Run through run07: source/executable/input hashes, one hardware workload,
read-only live-status checks every second, abort owned research on user
activity or unavailable status. Port 56708 is never changed. No deployment.

If qualified, use the resulting all-path quality as a reference for subsequent
variance-reduction and speed experiments. Before claiming a speedup, measure
controls that also pass the same quality gate. If not qualified, retain the
failure and inspect which conditional paths or global gaps prevented it.
