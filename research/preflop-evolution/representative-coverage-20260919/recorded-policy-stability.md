# Recorded training-panel policy stability

Changes between recorded root hand-class policies under each source's fixed entering distribution. TV is the fraction of action probability mass moved. It is not an EV error, confidence interval, independent validation or proof of stability after the final checkpoint. No extra solve was run.

| Source | Checkpoint interval | Weighted hand-policy TV | Aggregate frequency TV |
|---|---|---:|---:|
| 10 flops | 1 to 20 | 60.6640% | 51.1405% |
| 10 flops | 20 to 100 | 12.7014% | 6.7848% |
| 10 flops | 100 to 500 | 4.4107% | 1.0732% |
| 10 flops | 500 to 2000 | 0.5543% | 0.1227% |
| 47 flops | 1 to 20 | 59.5217% | 51.2417% |
| 47 flops | 20 to 100 | 14.4011% | 3.2863% |
| 47 flops | 100 to 500 | 9.2876% | 6.5544% |
| 47 flops | 500 to 2000 | 2.9357% | 2.5257% |

## 10 flops: recorded action frequencies

| Iteration | Fold | Call | 4-bet | Jam | Full gap (bb) |
|---:|---:|---:|---:|---:|---:|
| 1 | 25.0000% | 25.0000% | 25.0000% | 25.0000% | 75.495352 |
| 20 | 76.1405% | 11.4985% | 8.9709% | 3.3901% | 5.625735 |
| 100 | 72.4831% | 12.7696% | 14.4845% | 0.2628% | 0.640217 |
| 500 | 72.3272% | 12.1120% | 15.5577% | 0.0031% | 0.043117 |
| 2000 | 72.2302% | 12.0892% | 15.6804% | 0.0001% | 0.004092 |

Largest weighted hand changes in the final recorded interval:

| Hand | Entering mass | Hand-policy TV | Weighted contribution |
|---|---:|---:|---:|
| A5s | 2.077% | 6.307% | 0.1310% |
| 55 | 3.461% | 2.477% | 0.0857% |
| 66 | 3.732% | 2.263% | 0.0845% |
| A3s | 0.682% | 9.032% | 0.0616% |
| A9s | 1.820% | 2.281% | 0.0415% |
| 99 | 2.720% | 1.286% | 0.0350% |
| KK | 2.902% | 0.794% | 0.0230% |
| T9s | 2.098% | 1.012% | 0.0212% |
| AKs | 1.898% | 1.019% | 0.0193% |
| KQs | 2.002% | 0.493% | 0.0099% |

## 47 flops: recorded action frequencies

| Iteration | Fold | Call | 4-bet | Jam | Full gap (bb) |
|---:|---:|---:|---:|---:|---:|
| 1 | 25.0000% | 25.0000% | 25.0000% | 25.0000% | 73.805552 |
| 20 | 76.2417% | 8.6643% | 11.7202% | 3.3738% | 5.206158 |
| 100 | 74.3622% | 8.6340% | 10.3437% | 6.6602% | 0.775485 |
| 500 | 78.6567% | 2.5807% | 9.8426% | 8.9199% | 0.052653 |
| 2000 | 80.9216% | 0.0550% | 9.9194% | 9.1039% | 0.007424 |

Largest weighted hand changes in the final recorded interval:

| Hand | Entering mass | Hand-policy TV | Weighted contribution |
|---|---:|---:|---:|
| QQ | 3.167% | 21.140% | 0.6695% |
| JJ | 3.541% | 9.825% | 0.3479% |
| 87s | 0.478% | 55.542% | 0.2653% |
| A4s | 2.145% | 9.754% | 0.2092% |
| A5s | 2.192% | 7.290% | 0.1598% |
| AKo | 5.754% | 2.541% | 0.1462% |
| T9s | 2.227% | 5.816% | 0.1295% |
| JTs | 2.314% | 5.598% | 0.1295% |
| TT | 3.453% | 3.694% | 0.1275% |
| A3s | 0.669% | 18.272% | 0.1223% |

The 2,000-step results have no later checkpoint. Their small within-panel deviation gaps therefore do not demonstrate that every mixed frequency has stopped moving. These observations do not change the frozen transfer sources or justify extending a selected source after observing its test outcomes. Between-panel sensitivity and same-panel reconstruction remain separate questions.
