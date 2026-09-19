# Premium response and card-removal audit

Research only. Conditioning the saved LJ policies on holding AA changes opponent response frequencies and showdown equity. It does not re-solve the game or account for cards held by folded seats.

| AA estimate | Original independent classes | Two-hand compatible cards |
|---|---:|---:|
| Jam EV | 40.10 | 44.20 |
| 4-bet EV with original fast continuation | 40.12 | 42.26 |

With explicit half continuation: call 53.50bb, 4-bet 45.32bb, jam 44.20bb. Calling still has the highest point estimate. These are fixed-policy sensitivities, not new equilibrium action values.
With explicit large continuation: call 55.78bb, 4-bet 45.48bb, jam 44.20bb. Calling still has the highest point estimate. These are fixed-policy sensitivities, not new equilibrium action values.

## Opponent policy differences

Wizard was inspected at the same 200bb NL25 case. Reserved 100bb cases were not opened. Its unconditioned response to 4-bet 45 is fold 46.5%, call 29.9%, jam 23.7%; GTOpen is 40.9%, 41.1%, 18.0%. Rounded Wizard totals can differ from 100%.

| Hand vs 4-bet | Wizard call / jam | GTOpen call / jam |
|---|---:|---:|
| AA | 54.8% / 45.2% | 0.0% / 100.0% |
| KK | 24.3% / 75.7% | 45.1% / 54.9% |
| AKs | 34.5% / 65.5% | 100.0% / 0.0% |
| AKo | 29.1% / 70.8% | 49.2% / 0.0% |
| AQs | 100.0% / 0.0% | 30.7% / 69.1% |
| QQ | 100.0% / 0.0% | 100.0% / 0.0% |
| JJ | 41.7% / 0.0% | 86.6% / 0.0% |

| Hand vs jam | Wizard call | GTOpen call |
|---|---:|---:|
| AA | 100.0% | 100.0% |
| KK | 100.0% | 100.0% |
| AKs | 100.0% | 51.0% |
| AKo | 0.0% | 0.0% |
| QQ | 83.5% | 0.4% |
| JJ | 48.1% | 18.1% |

These policies respond to different entering ranges and continuation models. The comparison locates disagreement; it does not establish that copying a Wizard frequency into GTOpen fixes its value model. The next experiment should test coupled range and policy adaptation rather than add a scalar premium-hand bonus.
