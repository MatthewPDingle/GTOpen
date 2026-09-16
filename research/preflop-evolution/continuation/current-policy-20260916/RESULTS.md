# Current versus averaged policy at 1500 iterations

Read-only inspection of the same17 selected N19 nodes. No payoff evaluation or policy modification.

| Path | Position | Ordinary current/average TV | Learned current/average TV |
|---|---|---:|---:|
| [] | UTG1 | 0.00023710209641002552 | 0.0011188885505271373 |
| [0] | MP | 0.0005315590091980363 | 0.0007965753774537608 |
| [0, 0] | HJ | 0.0002011097063783104 | 0.0004039376992594041 |
| [0, 0, 0] | CO | 0.0006777423661864952 | 0.001669993057267857 |
| [0, 0, 0, 0] | BTN | 0.00020106581246981278 | 0.00045764682874240015 |
| [0, 0, 0, 0, 0] | SB | 0.00020092014054963768 | 0.0006932744731593118 |
| [0, 0, 0, 0, 0, 0] | BB | 0.0014791902294069676 | 0.0002688470352569592 |
| [0, 0, 0, 0, 1] | SB | 0.0010700782255748365 | 0.0008772329633916567 |
| [0, 0, 0, 0, 1, 0] | BB | 0.000982183284427737 | 0.0016368946969593412 |
| [0, 0, 0, 0, 1, 0, 0] | UTG | 0.002854400897111369 | 0.0021032927804004566 |
| [1] | MP | 0.00030761951306344315 | 0.0010053837254828935 |
| [1, 0] | HJ | 0.0005490221312800735 | 0.00037632243491564777 |
| [1, 0, 0] | CO | 0.00015429174868460414 | 0.0021079352976818883 |
| [1, 0, 0, 0] | BTN | 0.0012324040703770751 | 0.0021005385492381934 |
| [1, 0, 0, 0, 0] | SB | 0.0002930524455566297 | 0.0010273205292816179 |
| [1, 0, 0, 0, 0, 0] | BB | 0.001626768721797511 | 0.0018602370812307765 |
| [1, 0, 0, 0, 0, 0, 0] | UTG | 0.0016930137231012034 | 0.00029452319303746366 |

TV is weighted by the averaged policy own-range distribution. A missing range is recorded as null, not stable. Current/average differences at one instant do not prove oscillation over time or explain the remaining gap by themselves. The current policy has not been substituted into any reported convergence metric.

The largest learned current/average weighted TV is 0.002108 (about0.211 percentage points), versus0.002854 for the ordinary path. These17 decisions do not show large hidden current/average separation at this checkpoint. Deeper nodes and temporal trajectories remain unmeasured; this does not certify stability across the whole tree.
