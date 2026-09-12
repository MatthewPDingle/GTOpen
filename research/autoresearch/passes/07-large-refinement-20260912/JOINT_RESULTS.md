# Alternating GPU updates with resets: rejected on both inputs

The sampled-input experiment completed all four cycles in 912.813 seconds.
Its independent final audit passed 27/27 paths, but the final global gap was
1.11701546 bb, so it fails qualification. The native-input comparison completed
in 774.906 seconds; its final global gap was 0.30852256 bb with all 27 paths
passing the independent conditioned audit. It also fails qualification.

| Sampled cycle (zero based) | Full global gap (bb) | Conditional paths passing |
|---|---:|---:|
| 0 | 0.2886308583 | 26/27 |
| 1 | 0.4700423331 | 27/27 |
| 2 | 0.5568304135 | 27/27 |
| 3 | 1.1170154599 | 27/27 |

| Native cycle (zero based) | Full global gap (bb) | Conditional paths passing |
|---|---:|---:|
| 0 | 0.7919581038 | 27/27 |
| 1 | 2.4294273040 | 27/27 |
| 2 | 0.3547301964 | 27/27 |
| 3 | 0.3085225639 | 27/27 |

The unchanged global target is 0.005 bb. Cycle 1 demonstrates why passing all
conditional paths alone is insufficient: all 27 passed while the complete
strategy's unrestricted gap increased substantially. These conditional tests
cover one-step deviations at the registered paths, not every ancestor, every
branch, or full subgame best responses.

All eight cycles passed the exact native arena roundtrip check. The
upstream operation checks retained/fixed arenas; each compact operation checks
its authorized arena blocks and global age. These invariants do not imply
strategic accuracy.

Sampled evidence: `raw/large-eight-sampled-joint-v1-{exit,result,broad}.json`
and `raw/large-eight-sampled-joint-v1.log`. Native evidence has the same suffixes
under `raw/large-eight-native-joint-v1-*`. Both guarded processes and independent
audits exited successfully; numerical qualification failed, not execution.

Cycle 2 continues the same adverse global trend. The global gap in cycle 1 was
concentrated in seats 0 and 1 (0.19832234 and 0.22149984 bb respectively).
See PERSISTENT_UPSTREAM_PLAN.md for the next controlled comparison; repeated
short learner reinitialization is a hypothesis to test, not a proven cause.
