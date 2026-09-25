# Both later-action training histories verified

Both independent CPU audits passed on September 25. Each reconstructed all
78 planned updates from generation zero, including the sampled roots,
postflop targets, reservoir insertions, policies, and final checkpoint.
The second audit covered the original T: evidence and the resumed S: evidence
as one contiguous training history. Neither audit refitted a model.

| Measure | First trial | Second trial |
| --- | ---: | ---: |
| Completed updates | 78 | 78 |
| Reconstructed BB roots | 39,936 | 39,936 |
| Reconstructed postflop targets | 883,514 | 952,096 |
| BB reservoir insertions | 814,687 | 899,983 |
| BTN reservoir insertions | 132,196 | 115,657 |
| Maximum root-state difference | 2.73e-12 | 3.64e-12 |
| Maximum target difference | 5.69e-14 | 5.69e-14 |
| Maximum policy difference | 1.22e-12 | 2.71e-12 |
| Audit seconds | 7,257.422 | 6,396.578 |

The audit/source registration, result, readback-registration, and final
checkpoint bindings were checked again after each audit completed. Different
target counts reflect different sampled training trajectories; the counts are
not a quality comparison. Audit times are operational measurements under
different concurrent loads, not a controlled speed benchmark.

The recovered pipeline accepted both reviews and started its evaluation
control. That control uses 64 previously inspected deals and all four complete
trained model banks. It must establish CPU/GPU agreement and pass independent
readback before the registered 65,536 fresh physical deals are drawn. The
crossed old/new player comparisons and separate root-stability diagnostic
remain outstanding at this note's creation.

These successful audits establish implementation/evidence consistency, not
stronger play, equilibrium convergence, general preflop accuracy, or agreement
with GTO Wizard. No production deployment has occurred.

Independent-review identities:

- First: `later-action-first-audit-recovery-v1-independent-review.json`,
  SHA-256 `6e49c766053b2acb288a7076c4f0d4e8b3ba31a811a50bfa7f6f563d6a8bd34e`.
- Second: `later-action-replication-volume-continuation-v1-independent-review.json`,
  SHA-256 `a0d43710f8f33b58f1194ee0472f939d02a9c6fb5470bf0cc8ee603638e364d0`.
- Second readback registration:
  `46665d9f3beb05d65965045819d74108441705b8fa54d29d318c831866eddff0`.

The second audit's preserved console output is
`later-action-recovered-pipeline-v1-replication-full-audit.log`.
