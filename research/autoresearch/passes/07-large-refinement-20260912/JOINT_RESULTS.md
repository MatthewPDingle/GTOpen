# Alternating GPU updates: interim evidence

The sampled-input experiment completed all four cycles in 912.813 seconds.
Its independent final audit passed 27/27 paths, but the final global gap was
1.11701546 bb, so it fails qualification. The native-input comparison is running.

| Sampled cycle (zero based) | Full global gap (bb) | Conditional paths passing |
|---|---:|---:|
| 0 | 0.2886308583 | 26/27 |
| 1 | 0.4700423331 | 27/27 |
| 2 | 0.5568304135 | 27/27 |
| 3 | 1.1170154599 | 27/27 |

The unchanged global target is 0.005 bb. Cycle 1 demonstrates why passing all
conditional paths alone is insufficient: all 27 passed while the complete
strategy's unrestricted gap increased substantially. These conditional tests
cover one-step deviations at the registered paths, not every ancestor, every
branch, or full subgame best responses.

All four sampled cycles passed the exact native arena roundtrip check. The
upstream operation checks retained/fixed arenas; each compact operation checks
its authorized arena blocks and global age. These invariants do not imply
strategic accuracy.

Sampled evidence: `raw/large-eight-sampled-joint-v1-{exit,result,broad}.json`
and `raw/large-eight-sampled-joint-v1.log`. The native run's first completed
cycle passed 27/27 conditional paths with a global gap of 0.79195810 bb; its
remaining cycles and final independent audit are pending.

Cycle 2 continues the same adverse global trend. The global gap in cycle 1 was
concentrated in seats 0 and 1 (0.19832234 and 0.22149984 bb respectively).
See PERSISTENT_UPSTREAM_PLAN.md for the next controlled comparison; repeated
short learner reinitialization is a hypothesis to test, not a proven cause.
