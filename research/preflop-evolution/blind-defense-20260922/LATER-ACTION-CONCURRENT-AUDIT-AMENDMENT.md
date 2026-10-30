# Scheduling-only amendment: overlap CPU audit and GPU replication

Declared while the first matched trial is still training, before either candidate's final ranges or fresh evaluation outcomes are available. The mathematical experiment, two seed sets, sample counts, fitted models, averaging rules and storage limits are unchanged.

After the first training controller completes successfully, its CPU-only independent reader may run concurrently with the second trial's GPU training controller. The reader explicitly disables CUDA and sets its CPU math to one thread. It reads the completed first store and writes only that trial's audit metadata. The second trainer creates a separate new store and performs its own fresh global storage admission. Only one research GPU owner remains active.

The replication admission in `hu_later_action_replication_concurrent_20260925.py` requires the first successful complete training result and terminal controller status, plus the already passed two-update implementation/audit gates. It defers the first full audit as an evaluation prerequisite rather than requiring it before the independent second seed can start. Its training worker is unchanged from the original controller; structural comparison verifies an identical worker syntax tree.

A supervising sequence must stop its owned replication processes if the first independent audit fails. Neither candidate may enter the complete-policy evaluation before both full training audits pass. A failed or interrupted stage is preserved and not automatically retried. The live first trainer and production are never terminated by this supervisor. No checkpoint, seed, budget or strategy is selected based on intermediate results.

This replaces the strictly sequential scheduling of steps 1 and 2 in `LATER-ACTION-COMPARISON-OPERATIONS.md`. It should avoid an idle GPU during a lengthy CPU audit. The actual wall-clock saving remains to be measured; all resource reserves and the 800 GB combined allocation ceiling still apply.
