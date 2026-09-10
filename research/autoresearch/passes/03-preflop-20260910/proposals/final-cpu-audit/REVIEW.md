# Final retained CPU audit

**Conclusion: no blocking correctness issue found in the reviewed CPU changes.** This is a source-only review, not a fresh test execution or performance certification.

Reviewed the working-tree CPU files at HEAD `a6f8da893c1aa697dda382ebfdde9182e6cadca9` against original `1b8fc3f`. These three files have no changes relative to the previously reviewed `9333943` CPU version. Active GPU candidates were excluded.

| File | Git blob reviewed |
|---|---|
| `crates/solver/src/preflop/mod.rs` | `ef6827910de35af84e364aaca66dab3f87be8907` |
| `crates/solver/src/preflop/multiway.rs` | `f6a66474ff3fa143c0c4c30bd607f873a56252a4` |
| `crates/solver/src/preflop/checkpoint_tests.rs` | `b044eef214ee2a8ec63878eea4693ceba9f47da3` |

## Quadrature

For O opponents, the tie-share integrand is a product of O linear factors and has degree at most O. Dispatch uses one Gauss point for O=0..1, two for O=2..3, three for O=4..5, four for O=6..7, and five for O=8. Every rule is mathematically sufficient; all 1,024 particles, class ordering, CDF construction, opponent ordering, normalization, and final averaging remain in place. The upper bound of eight opponents is still asserted.

This changes floating-point rounding relative to the original five-point rule. It does not promise original CPU bit patterns. Tests retain a literal five-point reference and compare all 169 outputs for every opponent count 0..8, dense/sparse distributions, same-class ties, all-tied particles, and grouped ranks, with a 2e-12 absolute tolerance. Empty-opponent behavior and exact conceptual tie shares are covered. Ordinary production terminal distributions need not be exactly normalized in f32; polynomial exactness does not require exact unit normalization.

## Paired checkpoint traversal

- BR and average evaluation use the same forced-or-average sigma at a node, just as the previous separate read-only modes did. Their difference is upward maximization versus sigma weighting, so sharing terminal evaluation is valid. Terminal payoff depends on opponent reaches and not the traverser's own reach; both outputs propagate identical reaches along a given history.
- Unrestricted mode 2 still maximizes at the traverser's own nodes even for fixed/frozen policies, preserving their diagnostic bleed semantics. Mode 3 maximizes only when that node has no forced sigma and its actor is not frozen. `constrained_br`, `forced_sigma`, profile/adaptive threshold handling, point-lock precedence, hero profile exemption, and live-seat stopping selection are unchanged.
- Zero-mass pruning is output-specific. An own BR deviation stays requested even when average evaluation prunes it. A missing vector is treated as positive zero, matching the original allocated zero vectors. Nonpruned actions retain action order in max, multiplication, and addition. Gap subtraction remains f32 before promotion to the f64 class-weighted accumulator.
- Parallel branches clone all reach vectors and hold only shared references to solver state. Indexed action results are collected in action order. Sequential branches restore the actor's saved reach on completion and on propagated cancellation. Neither checkpoint path writes regrets or strategy sums.
- Cancellation propagates as `None` internally and remains latched if an ancestor observes it. A second root-level stop check rejects cancellation after the last branch. As before, stop polling is at shallow fan-out depths, so a deep sequential subtree may finish before cancellation is observed; this is not a new responsiveness guarantee.

## Cancellation guard and coverage limits

The public `gaps_and_evs` signature still represents cancellation with zero vectors. These are **not valid completed results**. The current server worker checks its stop flag after checkpoint evaluation and before publishing or applying the convergence threshold. Its running-state guard prevents a new solve from resetting that flag during an active checkpoint, and the previous worker is joined before a replacement starts. `ClearStop` removes the solver's cooperative flag on worker exit. No server changes are present in this CPU diff. Direct library callers installing a stop flag still must discard canceled values; that existing compatibility contract is explicitly documented and tested.

Checkpoint tests compare against the unchanged single-output `traverse` implementation. They cover pristine and learned roots; dense/sparse strategies; pruning on/off; two-/three-seat coupled and four-seat legacy roots under one/four worker threads; a separate four-seat coupled fixture; fixed/adaptive profiles, frozen seats, hero transitions, root/deeper point locks, all requested-output combinations, nonunit/zero reaches, arena immutability, terminal sharing, preset/mid-traversal/parallel cancellation, and recovery after cancellation. No critical missing guard was identified for the retained traversal change.

Limits: the checkpoint oracle uses the current terminal evaluator, so its exact parity establishes traversal equivalence, not end-to-end bitwise identity with the original quadrature. Larger six-/nine-seat paired-policy trees and a literal HTTP cancellation integration test are not directly part of these checkpoint tests; the generic traversal review and existing server guard provide the supporting reasoning. The ignored frontier/RSS stress is a separate manual performance control, not evidence of a realistic solve-speed improvement. No tests, builds, hardware jobs, or active source edits were performed during this audit.
