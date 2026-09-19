# Existing GPU engine: independently reproduced

All eight exported policies passed independent value and best-response-gap reconstruction within 0.0001 chip. This isolates a chance-model difference, rather than a CPU/GPU disagreement. Production remains unchanged.

| Stack | Iterations | Native-model gap | Compatible-model gap | Native-policy compatible value | Compatible minimax value |
|---|---:|---:|---:|---:|---:|
| 3 | 1000 | 0.000000 | 0.000000 | 1.000577 | 1.000577 |
| 3 | 10000 | 0.000000 | 0.000000 | 1.000577 | 1.000577 |
| 10 | 1000 | 0.000000 | 0.000497 | 1.112025 | 1.112265 |
| 10 | 10000 | 0.000000 | 0.000499 | 1.112024 | 1.112265 |
| 50 | 1000 | 0.000001 | 0.006152 | 0.537505 | 0.540081 |
| 50 | 10000 | 0.000000 | 0.006148 | 0.537508 | 0.540081 |
| 200 | 1000 | 0.000003 | 0.024308 | 0.121505 | 0.131369 |
| 200 | 10000 | 0.000000 | 0.024235 | 0.121497 | 0.131369 |

Units are the configured chip units (posts 1 and 2), not straddle-normalized big blinds. Values add back the SB post to make folding worth zero. Chance counts are exact; cached class equities remain sampled.

These uniform-range, heads-up push/fold trees are deliberately small. They do not measure full-tree performance, model the saved eight-player game, or establish that a similarly small root gap implies accurate rare-branch ranges.

[Frozen protocol](NATIVE-PROTOCOL.md) · [Inputs](native-freeze.json) · [Native outputs](native-policies.json) · [Independent review](native-review.json)
