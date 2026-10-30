# Reuse query inputs across the complete played model bank

The new `stack_context_played_bank_v1.py` evaluator constructs each native query
batch's inputs once, then reuses them for every saved model. Each model keeps
its own weights and preflop overrides. Averaging still weights each model by
its probability of having taken the player's earlier actions in that history.
It does not truncate the bank, substitute the latest model, or average actions
without accounting for earlier decisions.

The bounded check passed 28 cases: both 362- and 387-input representations,
all seven existing stack geometries, and CPU and CUDA evaluation. Its references
were the authenticated CPU averages already retained by the complete-model
control. Maximum action-probability difference was 2.22e-16 and maximum own-reach
difference was 4.44e-16. Each case encoded features exactly once for its two-model
bank. Ten invalid-input checks rejected reordered generations, an extra unplayed
generation, zero averaging weight, missing native history, and the wrong game.

The check took 10.75 seconds. It used native query fixtures and synthetic routing
models; it did not draw fresh scientific samples, fit a model or measure playing
strength. The two-model check is a correctness qualification, not a claimed
end-to-end speedup for a long bank. No production code was changed.

The check ran from the task's `.work/board-recovery` directory. Its exact sources
and immutable registration, attempt and result are retained in the repository;
the registered original source paths remain available. Do not rerun the completed
attempt. The adapter can be used by the existing crossed-policy evaluator through
its `average(queries, guard=...)` interface after loading the complete played bank
from a validated checkpoint. The checkpoint's final unplayed model must remain
excluded.
