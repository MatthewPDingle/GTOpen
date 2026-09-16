# Heads-up settling diagnostic

Two fixed small heads-up fixtures; separate approximate continuation games. Not full-postflop exploitability, runtime benchmarking or deployment qualification.

| Stack (bb) | Path | Iterations | Frozen-value gap (bb) |
|---|---|---:|---:|
| 40 | original | 500 | 0.000638 |
| 40 | original | 1500 | 0.000078 |
| 40 | balanced | 500 | 0.000462 |
| 40 | balanced | 1500 | 0.000058 |
| 40 | candidate | 500 | 0.000480 |
| 40 | candidate | 1500 | 0.000484 |
| 100 | original | 500 | 0.002004 |
| 100 | original | 1500 | 0.000274 |
| 100 | balanced | 500 | 0.000975 |
| 100 | balanced | 1500 | 0.000135 |
| 100 | candidate | 500 | 0.003581 |
| 100 | candidate | 1500 | 0.005513 |

The learned path has a much smaller gap here than in N19, but it does not improve between500and1500: it stays near0.00048bb at40bb and rises from0.00358to0.00551bb at100bb. Both baseline paths improve strongly. This shows the plateau/growth can occur without a multiway chance reset, while its severity depends on the game. It does not identify a faulty model feature, prove eventual divergence or establish full-game accuracy.
