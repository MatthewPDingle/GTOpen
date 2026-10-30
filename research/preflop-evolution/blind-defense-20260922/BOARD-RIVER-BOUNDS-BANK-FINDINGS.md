# River bounds pass complete-bank numerical qualification

Both complete 78-model histories passed CPU/CUDA and chunking comparisons on **14,547 queries from 32 already archived hands**. Maximum observed probability discrepancy was **8.01e-13**. No target loss or payoff was scored, and no new deals or training were performed. This qualifies the implementation for a separately registered strategy evaluation, not for production or a claim of better preflop ranges.

## What is preserved

Each bank contains played generations 0-77, weighted 1-78. The unplayed generation 78 remains excluded. Direct preflop tables and the board-root/BTN overrides are preserved. Every network uses its own saved player-specific scale for the correction. Model probabilities are then averaged using that model's corrected own-action reach, in the original generation order.

Preflop, flop and turn probabilities and averaging denominators stayed identical within each backend. CPU and CUDA agreed with projection enabled and disabled, for chunks of 1, 8 and all 78 models. The original typed CPU and GPU evaluators supplied baseline references. Hand-calculated controls covered unequal scales, upper/lower violations, negative scores, exact ties, nonuniform generation weights, direct-table overrides, zero reach, and a descendant changed only through its earlier action. Malformed game, model membership, scale, actor, phase, menu and ancestor inputs were rejected.

## Strategy changes on the fixed query archive

| Bank | Query category | Queries | Changed | Mean TV | Maximum TV |
|---|---|---:|---:|---:|---:|
| 9266201-board-root | all | 14,547 | 1,496 | 0.001255 | 0.968619 |
| 9266201-board-root | preflop | 147 | 0 | 0.000000 | 0.000000 |
| 9266201-board-root | flop | 576 | 0 | 0.000000 | 0.000000 |
| 9266201-board-root | turn | 2,752 | 0 | 0.000000 | 0.000000 |
| 9266201-board-root | river | 11,072 | 1,496 | 0.001649 | 0.968619 |
| 9266201-board-root | eligible | 7,296 | 1,496 | 0.002502 | 0.968619 |
| 9266201-board-root | unprojected_reach_descendants | 0 | 0 | — | — |
| 9266301-board-root | all | 14,547 | 1,588 | 0.001092 | 0.715111 |
| 9266301-board-root | preflop | 147 | 0 | 0.000000 | 0.000000 |
| 9266301-board-root | flop | 576 | 0 | 0.000000 | 0.000000 |
| 9266301-board-root | turn | 2,752 | 0 | 0.000000 | 0.000000 |
| 9266301-board-root | river | 11,072 | 1,588 | 0.001435 | 0.715111 |
| 9266301-board-root | eligible | 7,296 | 1,588 | 0.002177 | 0.715111 |
| 9266301-board-root | unprojected_reach_descendants | 0 | 0 | — | — |

TV is half the summed absolute differences between action probabilities. These figures give every archived query equal weight; they are not dealt-hand frequencies, game reach, or estimates of EV gain. Query categories overlap: eligible decisions and descendants are subsets of river. An unprojected descendant can change because an earlier corrected action changes its relative model weights.

## Cost of the correction

| Bank | Baseline median, seconds | Bounded median, seconds | Ratio |
|---|---:|---:|---:|
| 9266201-board-root | 0.1710 | 0.1880 | 1.099× |
| 9266301-board-root | 0.1870 | 0.1720 | 0.920× |

Three warmed, paired repetitions per bank used identical prepared queries, cached tables and model chunk size 8. This isolates the inference cost of projection; it is not a production solve-speed benchmark. Initialization and the original CPU reference are separately recorded in the result JSON.

End-to-end qualification took **4.59 minutes**, including global storage admission and audited model loading. Peak own CUDA allocation was **1.082 GB**. The 800 GB allocated-storage cap, shared locks, production checks and light-desktop GPU sharing rule remained in force.

## Next decision

Compare unchanged and bounded complete policies on newly registered physical deals, with both player roles, paired payoff differences and fixed stopping. Keep preflop tables and entry ranges fixed for this inference-only comparison. Do not claim a retrained equilibrium, broad stack/position coverage, or a solved preflop model from this numerical qualification. A useful policy result would motivate a separate coadaptation experiment.
