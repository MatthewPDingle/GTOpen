# Non-root policy repair: rejected by the global accuracy gate

The original sampled large-game anchor remains selected. None of the five
registered repair strengths is eligible. No live changes or speed qualification.

The 1,567,754-node, eight-player anchor is the original gamma15/64/seed42 save
at iteration 1050. Its canonical 1,024-particle global gap is 0.0039928205 bb.
Normalizing the 27 selected average-policy slices preserves this evaluation
within the registered 1e-5 tolerance. The anchor passes 7/27 original branches
and 3/12 additional topology/reach-selected branches. All 39 are reachable.

| Mixture toward one-action best responses | Global gap (bb) | Original branches | Held-out branches | Sum of original conditional losses (bb) | Eligible |
| --- | ---: | ---: | ---: | ---: | --- |
| Unchanged anchor | 0.003993 | 7/27 | 3/12 | 9.004706 | Baseline |
| 12.5% | 0.029197 | 7/27 | 3/12 | 7.952074 | No |
| 25% | 0.062001 | 7/27 | 3/12 | 7.042378 | No |
| 50% | 0.173508 | 7/27 | 3/12 | 5.147331 | No |
| 87.5% | 0.626270 | 9/27 | 3/12 | 2.147930 | No |
| 100% | 0.803509 | 11/27 | 3/12 | Unavailable: nine paths unreachable | No |

The loss column sums separately conditioned per-node action losses; it is not
an additive global best-response gap. Improving that objective worsened global
accuracy in every trial. The strongest trial also removed reach at nine paths,
which remain failures. This is not evidence that all possible selective repairs
fail, but the registered rule is rejected without extending its cycle budget.

The executable completed in 145.328 seconds including loading, planning,
candidate evaluation, repeated final checks and serialization. Its process wall
time was 148.828 seconds; the independent saved-file audit took 10.031 seconds.
These times are diagnostic costs, not a fresh-solve performance improvement.

## Verification

- Two new numerical tests pass: value-directed targets/mixtures and atomic
  non-root batch edits. Invalid roots, duplicate/terminal/out-of-range paths,
  malformed probabilities, frozen/locked nodes and cancellation leave both
  arenas unchanged. A valid-first/invalid-last batch makes no partial write.
- Regrets, root/unselected averages and global age are preserved. Normalized
  trial rollback is exact; CPU/GPU average evaluations agree on the small
  correctness fixture, and saved arenas round-trip exactly.
- Native equivalence passes six postflop and thirteen preflop GPU tests. The
  full default release solver suite passes. Timings including compilation:
  numerical 92.875 seconds, native equivalence 66.438, default suite 208.015.
- Before the large run, the example's reviewed selection uses the true minimum
  eligible objective and requires improvement from the cycle baseline; rollback
  retains its exact average weights. Builds v1/v2 are retained; only v2 ran the
  large diagnostic. No solver-library changes occurred after numerical testing.
- check_conditional_policy_repair.py independently reconstructs every target
  and mixture, checks their applied policies, recomputes weighted objectives and
  unchanged gates, checks candidate selection and input hashes, and compares the
  separately loaded audit exactly with both final checks. All verification passes.

The original threshold remains global gap <=0.005 bb plus every fixed per-hand
conditional gate. No candidate satisfies it. The final research save is the
normalized anchor, with no repair accepted, and must not be resumed as ordinary
CFR history. The live application on port 56708 is unchanged.
