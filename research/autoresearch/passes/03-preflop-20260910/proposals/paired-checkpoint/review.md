# Applied f88ac43 checkpoint review

Read-only review completed against the applied evaluator. No correctness blocker found.

## Findings

1. **Shared terminal values are valid.** Modes 1, 2 and 3 all propagate the same forced-or-average actor strategy into each child. BR's own reach is still scaled exactly as in the old implementation, and terminal values exclude the traverser's own reach. Therefore a BR-only off-path action must still be evaluated, and the independent child need flags correctly retain it. No own-reach pruning was introduced.
2. **Constrained/frozen/point-lock semantics match.** Unrestricted mode 2 maximizes even at forced or frozen own nodes; mode 3 maximizes only when the own node is neither forced nor frozen. Profile exemptions for hero and point-lock precedence remain inside unchanged forced_sigma. Missing avg outputs cannot become spurious BR zero values: a requested maximizing BR requests every child.
3. **Reductions preserve bits.** Every requested weighted or opponent-summed output includes every action in the original order. Missing/pruned values mean the old positive-zero vector. Own maxima retain the same f32::max behavior. Root gaps subtract in f32 before f64 accumulation.
4. **Parallel collection preserves order.** Local Rayon 1.12 source confirms Option collection wraps the original iterator with inspect/while_some; its Vec collection combines left chunks before right chunks. No completion-order reduction was introduced. However, while_some loses opt_len, causing LinkedList<Vec<_>> metadata allocation before the final Vec join, instead of the old indexed Vec collector. This is a possible cheap-terminal overhead, not a correctness issue.
5. **Cancellation is joined and read-only.** Rayon collection finishes/join-unwinds its participating work before returning None. Both sequential return paths restore saved reaches. The private evaluator latches a canceled child; public compatibility zeros retain the existing stop-flag publication contract. No arenas are written. Stop is polled only at depth < PAR_DEPTH, so a deep sequential subtree can finish before cancellation is noticed, as in the old traversal; do not advertise instantaneous stop.
6. **Memory tradeoff is bounded to active reductions, but measure it.** Shared child outputs hold two 676-byte vectors instead of one. Old BR roots remained alive while the old AVG pass ran, but that alone is only 676 bytes per seat; the paired internal frontier is the larger change. Reach copies occur once instead of twice serially, while peak reach-copy counts are similar. Option collection adds small temporary metadata chunks. No persistent terminal cache or graph-sized scratch is added. A wide allocation stress complements the existing 6/9-seat RSS figures.

## Additional proposed gates

`review-tests.patch` applies cleanly to the current internal test file. It adds two normal tests and one ignored manual test; no active source edited and nothing compiled/run here.

- `paired_checkpoint_sequential_roots_restore_nonunit_reaches`: force the existing small coupled fixture into the sequential branch by starting at PAR_DEPTH, compare both full output arrays against original traverse in modes 2/3, exercise single/both output requests with pruning on/off, and assert each caller reach float is restored bit-for-bit. Reaches deliberately include zero entries and non-unit mass. This is more direct and cheaper than a much deeper generated game.
- `paired_checkpoint_parallel_cancellation_is_not_completed`: four worker threads install deterministic per-worker visit triggers through the existing test-only TLS hook. The checkpoint must return None, retain the stop flag, preserve arenas, and recover in a fresh uninstrumented pool. No timing sleeps or races determine when cancellation starts.
- `paired_checkpoint_all_fold_frontier_stress` (ignored): six seats, 100k–250k nodes selected deterministically with estimate_tree, prune=false, all-fold/check average strategies. Every structural branch still receives BR/average work; almost all expensive coupled-equity terminals exit on zero opponent reach. This deliberately isolates allocation/frontier pressure and is not a realistic solve-speed benchmark.

## Separate-process memory control

Run the ignored test twice from the same built test binary, separately under run_guarded.py or the existing RSS monitor:

- PREFLOP_CHECKPOINT_STRESS_MODE=original
- PREFLOP_CHECKPOINT_STRESS_MODE=paired
- PREFLOP_CHECKPOINT_STRESS_THREADS=4 (repeat machine's normal thread count only if warranted)

Invoke only `paired_checkpoint_all_fold_frontier_stress --ignored --exact` using its full module path if calling the test binary directly. Both modes use the same outer per-seat Rayon parallelism. The original mode calls unchanged traverse mode 2 and mode 1 separately; paired calls gaps_and_evs. No learning runs. No arena snapshots are retained, as those would inflate the RSS peak. Record exact chosen config, nodes, arena bytes, root result bits and arena fingerprints from CHECKPOINT_FRONTIER output. Compare RSS/private-memory peak and confirm output bits/fingerprints match. Record elapsed time only as diagnostic allocation cost.

Use an external 300-second timeout per process; do not reduce samples or switch payoff model if exceeded. Constructor/static arenas may dominate peak RSS, so a small absolute increase is more informative than a percentage alone. If 100k–250k still exceeds the time envelope, bound the node range lower in the synthetic test and label it accordingly. The configuration estimator may inspect up to 24 alternatives, each capped by the existing estimator; it never allocates solver arenas before choosing one.

The synthetic all-fold state does not avoid own off-path BR actions: pruning is explicitly disabled. It avoids expensive terminal-equity calculations through genuinely zero opponent reach, while keeping the full output allocation/reduction frontier. That is why it is a suitable memory stress without requiring the user's million-node CPU solve.

## Remaining real-workload acceptance

Retain the completed exact benchmark and existing suite results. The parent is adding modeled fixtures; include one with actual forced/adaptive data, because fixed-policy formation cost and sparse BR-only branches differ from plain solver tables. A source-attested same-target solve and standard thread-count RSS measurement are preferable to broad extra microbenchmarks. No additional production rewrite recommended based on this review.
