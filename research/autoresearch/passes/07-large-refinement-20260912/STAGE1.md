# Stage 1: large-game refinement

Two immutable 1,567,754-node eight-player snapshots were independently refined
for 1,000 local iterations on six pre-registered paths. The entire remaining
regret and strategy arenas were checked for exact preservation. Native saves
were reloaded and compared exactly. All checks passed; global iteration stayed
unchanged. These copies are offline artifacts, not normal resumable sessions.

| Input | Process time | Local gates after refinement |
| --- | ---: | ---: |
| Full-sample baseline | 134.5 s | 6 / 6 |
| 64-sample gamma15 seed42 | 135.6 s | 4 / 6 |

Independent local audits added 8.0 and 6.6 seconds respectively. The sampled
candidate still fails BB after two callers (worst relevant probability on an
inferior action 0.10053, threshold 0.10) and BTN in the limped branch (0.12988).
The thresholds were not relaxed. Its full global gap sums to roughly 0.00403 bb,
which illustrates why a global convergence gate alone is insufficient.

Six selected branches do not qualify the entire game. Next: extend conditional
coverage and make local iteration allocation respond to failed conditional
checks. The GPU control-variate implementation is a separate experiment;
compilation or a synthetic variance result is not evidence of useful GPU speed.
