# Alternating GPU updates: interim evidence

The sampled-input experiment is still running its registered four-cycle cap.
The native-input comparison has not started. No qualification claim is made.

| Sampled cycle (zero based) | Full global gap (bb) | Conditional paths passing |
|---|---:|---:|
| 0 | 0.2886308583 | 26/27 |
| 1 | 0.4700423331 | 27/27 |

The unchanged global target is 0.005 bb. Cycle 1 demonstrates why passing all
conditional paths alone is insufficient: all 27 passed while the complete
strategy's unrestricted gap increased substantially. These conditional tests
cover one-step deviations at the registered paths, not every ancestor, every
branch, or full subgame best responses.

Both completed cycles passed the exact native arena roundtrip check. The
upstream operation checks retained/fixed arenas; each compact operation checks
its authorized arena blocks and global age. These invariants do not imply
strategic accuracy.

Current evidence is in the guarded active log
`raw/large-eight-sampled-joint-v1.log` and immutable completed cycle records in
`target/convergence/large-eight-sampled-joint-v1/cycle-{0,1}.json` under the
research worktree. Final archived results and independent audit are pending.
