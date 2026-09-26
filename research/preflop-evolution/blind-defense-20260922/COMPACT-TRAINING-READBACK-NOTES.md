# Independent compact-training readback

The reader reconstructs the registered deal and action random streams, current probabilities from the saved network weights and tables, scalar BB root targets from native forced-action values, exact initial-jam targets, postflop conditional-action targets, exact BTN updates, and root regret sums. It independently scores showdown cards for corrected arms. At saved recovery boundaries it rebuilds the reservoirs and checks the original archived arrays, counters, and RNG states. It performs no training or GPU inference.

Version 1 reviewed the first four baseline updates (2,048 root deals) through their per-update numeric checks, then failed its final count assertion because that assertion still expected the full 78-update run. The failed result and registration are retained. It is not a passing review and does not qualify the prefix.

Version 2 replaces that final full-run count with the explicitly requested prefix count. It can also follow a fixed target count while verifying that the registered training worker remains live. Only retention markers published after a completed update are consumed. Its final result binds the hashes of every marker actually reviewed. Waiting does not create new poker samples or change the training worker.

The first version-2 target is eight baseline updates, including the first recovery snapshot. A full arm is not audited until all 78 updates pass. Numeric reconstruction and archive integrity checks are implementation evidence; they do not establish poker strength or range accuracy, and the reader does not independently refit neural-network weights.
