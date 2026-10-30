# Independent small-gain numerical audit

**PASS_FIXED_FAMILY_NUMERICAL_AUDIT. All four candidates remain rejected.**

All128 evaluator processes and five unit suites were retained in the frozen order. All384 complete non-timing result payloads,2944 convergence checkpoints and full normalized stage trajectories match the accepted anchor. Unit summaries are84/4,84/4,84/4,85/4,85/4; the focused E03634-pair/68-launch marker is exact.

| Candidate | Aggregate gain | Positive pairs | Failed gates |
|---|---:|---:|---|
| E007 | 2.21285850% | 13/16 | fixture_guard_pass |
| E008 | 0.51710774% | 12/16 | aggregate_ge_1pct, at_least13_positive_pairs |
| E032 | 0.53065818% | 14/16 | aggregate_ge_1pct |
| E036 | 0.84880341% | 11/16 | aggregate_ge_1pct, at_least13_positive_pairs, every_block_median_positive |

E007 river median slowdown is 1.54252955%, with 11/16 paired slowdowns. It therefore fails the frozen no-repeatable-fixture-slowdown guard despite clearing the aggregate threshold.

The file-only auditor passed 10611 checks, independently recomputing component distributions, complete-cycle medians, all pair/block/order gains, descriptive MAD/outcomes and every effective gate. No assessor module was imported, no measurements were repeated, and the audit had no execution failure.

Source/build/lock/custody is reviewed separately. This audit makes no statistical-confidence, additive speedup or adoption claim. No solver, compiler, native test or GPU work was performed by this reviewer.
