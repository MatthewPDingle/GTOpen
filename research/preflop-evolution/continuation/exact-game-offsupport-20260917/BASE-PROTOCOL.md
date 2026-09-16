# Small exact-game continuation diagnostic

Registered before running the experiment. No production deployment or GPU
performance claim. This independent mathematical harness tests the continuation
design; it does not execute GTOpen's CUDA kernel or establish Hold'em accuracy.

## Game and fixed comparisons

Three distinct ranked cards (0,1,2); each player receives one without replacement.
All six ordered deals have probability 1/6. No public cards, rake or abstraction.
Each antes one chip. In round one P0 checks or bets one. A check ends the round;
after a bet P1 folds or calls. In round two P0 checks to showdown or bets two;
P1 folds or calls. High card wins at showdown. Maximum contribution is four
chips per player. Folding loses the folder's contribution; payoffs are net,
zero-sum. The two public continuation contexts have matched contributions 1 or2.
Each player has nine binary information-set decisions, hence512 pure strategies.

1. Solve the complete512x512 zero-sum normal-form game by primal/dual linear
   programs. Also run simultaneous vanilla CFR with uniform reach-weighted
   strategy averaging on the full extensive tree.
2. Run the same upper-tree CFR, replacing each continuation with its8x8 exact
   equilibrium solved at the current ranges. Preserve per-hand counterfactual
   values, explicit legal-card exclusions and own-reach strategy averaging.
3. Train a fixed local radial-basis value interpolator for this same miniature
   game, then replace exact leaf values with its predictions. Do not reuse N15,
   which was trained for a different game. No fitting to search outputs.

Fixed checkpoints:100,500,2000,5000 iterations, no early stopping or tuning.
Record full-game NashConv (sum of both unilateral gains), upper frozen-value
gap, expected payoff, root action frequencies, strategy differences to the
full-tree reference, and elapsed time. NashConv is computed independently by
enumerating all512 information-consistent pure responses per player; never
maximize separately for each hidden opponent card. Exact cutoff evaluation
includes both its accumulated full policies and an exact re-solve at averaged
upper ranges. The surrogate's continuation policies are supplied by that same
exact reconstruction, so its reported full-game result is explicitly an oracle-
completed policy, not a fully learned agent.

Continuation LP duality tolerance1e-8; full LP duality tolerance1e-8. Numerical
unit tests precede runs. Reference full CFR and exact-interface final NashConv
must each be<=0.005 chips to pass this bounded integration screen. The surrogate
passes the practical screen only if its final oracle-completed NashConv<=0.005
and no more than0.002 above the exact-interface reconstruction. These are fixed
diagnostic thresholds, not deployment qualification. An exact-interface failure
halts prediction work until the failure is explained; no hidden threshold edits.

Training:512 independently drawn range pairs per contribution context, seed
20260917; Dirichlet concentrations cycle0.25,1,4. Inputs are each range's first
two components (last component implied). Outputs are six conditional hand values
divided by matched contribution. Fixed thin-plate radial-basis interpolation,
32 nearest neighbors, degree1, smoothing0.0001. Test:128 new range pairs per
context, independent seed20260918 and same fixed concentration schedule. Report
all errors, including worst and high-percentile errors. Predictions are clipped
to physical per-hand payoff bounds and jointly centered to conserve expected
zero-sum payoff at the supplied legal-pair distribution. Log raw and corrected
test errors separately. Whole range contexts, not individual hand rows, are split.

Entirely zero own reach uses a normalized uniform range for solving the unused
continuation, while its original zero reach remains in CFR and averaging. All
other zero components are retained. Degenerate disjoint legal mass is reported
and handled with a documented uniform fallback, never represented as observed
data. Include sparse-range numerical tests.

No timing comparison here is an RTX3090 production benchmark. Passing this toy
game would justify a production-interface parity fixture and a richer exact game;
it would not explain the overnight Hold'em failure by itself.

Background: ReBeL supplementary Appendix I distinguishes current-belief and
average-belief continuation search. This experiment uses current beliefs; it
does not claim to implement their modified CFR-AVG variant.
https://proceedings.neurips.cc/paper_files/paper/2020/file/c61f571dbd2fb949d3fe5ae1608dd48b-Supplemental.pdf
