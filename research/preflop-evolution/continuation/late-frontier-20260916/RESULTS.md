# Remaining one-action improvements at1500 iterations

One-action deviations at17 selected nodes only. Gains overlap and must not be summed as full exploitability. Values remain frozen learned or approximate Balanced continuation.

| Path | Position | Ordinary gain(bb) | Learned gain(bb) |
|---|---|---:|---:|
| [0, 0, 0, 0, 1, 0, 0] | UTG | 0.00000889 | 0.00004506 |
| [1, 0, 0, 0, 0, 0, 0] | UTG | 0.00000246 | 0.00000382 |
| [] | UTG1 | 0.00000479 | 0.00005880 |
| [0] | MP | 0.00000971 | 0.00014560 |
| [1] | MP | 0.00000177 | 0.00063855 |
| [0, 0] | HJ | 0.00000180 | 0.00004845 |
| [1, 0] | HJ | 0.00000179 | 0.00002718 |
| [0, 0, 0] | CO | 0.00000652 | 0.00003258 |
| [1, 0, 0] | CO | 0.00000033 | 0.00007155 |
| [0, 0, 0, 0] | BTN | 0.00000158 | 0.00000597 |
| [1, 0, 0, 0] | BTN | 0.00000546 | 0.00007800 |
| [0, 0, 0, 0, 0] | SB | 0.00000087 | 0.00000161 |
| [0, 0, 0, 0, 1] | SB | 0.00001005 | 0.00002666 |
| [1, 0, 0, 0, 0] | SB | 0.00000043 | 0.00040499 |
| [0, 0, 0, 0, 0, 0] | BB | 0.00001068 | 0.00000019 |
| [0, 0, 0, 0, 1, 0] | BB | 0.00000305 | 0.00005241 |
| [1, 0, 0, 0, 0, 0] | BB | 0.00000815 | 0.00001236 |

The largest inspected learned one-action gain is0.00063855bb, versus0.00001068bb for ordinary Balanced. These are small relative to the learned full frozen-value gap0.078407bb, but this is not an additive decomposition and does not locate all of that gap. Uninspected branches and coordinated successive deviations remain candidates for follow-up. No source save changed and no current strategy was substituted for averaged play.
