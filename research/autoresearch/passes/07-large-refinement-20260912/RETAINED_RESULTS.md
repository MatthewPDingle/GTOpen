# Retained upstream history: interim comparison

The sampled-input run remains active; the native comparison is queued.

| Cycle | Reset-history global gap (bb) | Retained-history global gap (bb) | Retained local passes |
|---|---:|---:|---:|
| 0 | 0.2886308583 | 0.2886308583 | 26/27 |
| 1 | 0.4700423331 | 0.1907721765 | 27/27 |
| 2 | 0.5568304135 | 0.1393915414 | 26/27 |

Cycle 0 matches exactly before history reuse starts. Cycles 1 and 2 retain
local ages 25->50 and 50->75 respectively while parent global age stays 1,050.
This controlled comparison supports retaining history over repeated short
reinitialization, but does not qualify the resulting policy. All global gaps
remain above the unchanged 0.005-bb target, and all local paths must pass together.

The failed cycle-2 path is `[3,0,0,0,0,1,1]` (BB): its worst relevant hand places
0.6134479 probability on actions losing more than 0.1 bb. The registered limit
is 0.1 probability for hands with conditional mass at least 0.0025. Its small
weighted mean action loss (0.00150097 bb) does not override that tail gate.

Evidence: completed `cycle-0.json`, `cycle-1.json`, and `cycle-2.json` under
`target/convergence/large-eight-sampled-joint-retained-v1` in the research
worktree, plus the active guarded log. Final archived records and independent
audit are pending. No production deployment.
