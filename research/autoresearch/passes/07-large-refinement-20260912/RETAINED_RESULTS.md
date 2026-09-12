# Retained upstream history: completed comparison

The sampled-input run completed in 819.703 seconds; its final independent audit
passed 27/27, but global gap was 0.16842107 bb. It still fails qualification.
The native-input run completed in 770.500 seconds; its final independent audit
passed 26/27 with global gap 0.07067669 bb. Neither input qualifies.

| Cycle | Reset-history global gap (bb) | Retained-history global gap (bb) | Retained local passes |
|---|---:|---:|---:|
| 0 | 0.2886308583 | 0.2886308583 | 26/27 |
| 1 | 0.4700423331 | 0.1907721765 | 27/27 |
| 2 | 0.5568304135 | 0.1393915414 | 26/27 |
| 3 | 1.1170154599 | 0.1684210684 | 27/27 |

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
worktree. Completed sampled results and independent audit are now archived as
`raw/large-eight-sampled-joint-retained-v1-{exit,result,broad}.json`; the
independent `check_joint.case('sampled','joint-retained-v1')` recomputed the gates
and verified exact agreement between saved-file and final-cycle per-hand values.

Native results:

| Cycle | Reset-history global gap (bb) | Retained-history global gap (bb) | Retained local passes |
|---|---:|---:|---:|
| 0 | 0.7919581038 | 0.7919581038 | 27/27 |
| 1 | 2.4294273040 | 0.1051569364 | 27/27 |
| 2 | 0.3547301964 | 0.0680201709 | 27/27 |
| 3 | 0.3085225639 | 0.0706766863 | 26/27 |

Retaining history improves the global result compared with repeated resets,
but the final cycle worsens both global and local accuracy. More cycles alone
are not an established solution. The independent `check_joint.py joint-retained-v1`
recomputed all gates and confirmed both final saved-file audits match their
last cycle exactly; its exit code 1 correctly records failed qualification.
Native evidence is archived under `raw/large-eight-native-joint-retained-v1*`.

Next: a read-only GPU diagnostic of one-step action values at upstream and
adjacent branch decisions, under actual prefix reach. These overlapping values
are not an additive decomposition of full best-response gap. CPU is used only
as a small correctness reference for the diagnostic. No CPU performance work
or production deployment.
