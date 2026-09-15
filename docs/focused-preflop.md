# Focused preflop studies

When a line has less than 0.001% modeled reach (about one in 100,000), Preflop Lab warns that its responses are unverified. This is an independent-class reach estimate. The whole-game best-response target does not certify accuracy at every node; the warning threshold is a browsing heuristic, not an accuracy boundary.

Select a decision after an action and click **Focused study…**. Review the incoming ranges, especially for an effectively unused jam, then click **Run focused study**. Range weights are relative and each incoming range is normalized. Suit-specific entries are pooled into the solver's 169 hand classes.

The study copies up to 20,000 descendant nodes and starts fresh GPU learning, preserving pot, investments, rake, terminal payoffs, and the selected branch's fixed model/lock policies. It retains the original game's equity approximations. Decisions before the selected node and incoming ranges are fixed assumptions. This is a conditional what-if result, not a replacement full-game equilibrium.

Progress shows iterations out of a 2,000-iteration budget, elapsed time and the local summed best-response gap for learning seats. Accuracy is checked every 25 iterations, with a 0.005 bb local target. Hitting the iteration limit is labeled approximate. Rare descendants can still be poorly resolved and retain the same warning.

Use the action buttons and Back inside the window to explore the study. Cancel or close the window to stop its work. Starting a normal solve/report also cancels the study at an iteration boundary. Normal games, saved games and reports are not modified. The last completed study is held only in memory until another study replaces it or the server restarts; focused results cannot be saved over a normal game.

No focused calculations run until requested. Normal learning kernels and convergence targets are unchanged. The browser warning adds a small reach calculation to node queries only.

Validation on the eight-seat, 200 bb UTG-straddle example: the 255-node jam branch reached a 0.0030 bb local gap in 75 iterations. The first study took 2.8 seconds; a repeat with CUDA initialized took 0.7 seconds. KK called essentially 100% at all seven response seats under the reviewed incoming jam range. These timings are specific to this tree and RTX 3090, not a general completion-time guarantee. CPU/GPU equivalence was checked for both heads-up and multiway conditional roots; the normal solver, preflop GPU, postflop GPU and server regression suites passed.
