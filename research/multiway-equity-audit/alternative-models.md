# Multiway pricing alternatives tested offline

These follow-up experiments compare approximate equity with compatible-card,
shared-board Monte Carlo. None is a full postflop game solution.

## Normalized pairwise products: rejected

For each joint tuple of hand classes, multiply each player's pairwise equities,
then divide by the sum of all players' products. This gives a coherent pot
split per tuple, but badly misses the validation fixture:

| Hand | Reference | Normalized product |
|---|---:|---:|
| KQo | 20.80% | 10.59% |
| AQo | 20.42% | 21.58% |
| KQs | 24.08% | 13.69% |
| 76s | 19.99% | 6.84% |
| AA | 58.83% | 83.58% |

Taking a square root before normalization helps AA but still gives only 13.47%
to 76s. A common exponent cannot recover the missing hand-dependent board
correlation. See `normalized-audit.json` and `multiway_normalized_audit`.

## Pairwise collision correction: accurate fixture, integration complications

Starting with the hero-card-excluded shared-board calculation, adjust both
the opportunity mass and the hero-winning mass by the product of pairwise
opponent compatibility factors. For two weighted combo distributions:

```
collision_mass = sum_card(card_mass_i * card_mass_j)
               - sum_combo(combo_weight_i * combo_weight_j)
compatibility = 1 - collision_mass / (total_i * total_j)
```

Subtracting identical-combo mass avoids counting a shared two-card hand twice.
Calculate this within the hero-winning subset as well as the full distribution.
Split ties by integrating `lower_rank_mass + t * equal_rank_mass` for t in
[0, 1], using four-point Gauss quadrature in the four-player experiment.
Higher-order collision correlations remain approximate.

| Boards | Mean absolute error | Largest error |
|---:|---:|---:|
| 256 | 1.19 pp | 3.19 pp |
| 512 | 0.90 pp | 2.61 pp |
| 1,024 | 0.66 pp | 1.89 pp |
| 4,096 | 0.38 pp | 1.02 pp |

These are eight seeds over the five original hands. See `collision-audit.json`
and `multiway_collision_audit`.

This is promising for standalone equity estimation. It is **not** an automatic
drop-in counterfactual utility: normalizing each hero by its own compatible
opportunity mass can break global pot accounting under the engine's current
independent class prior. A proper chance-model change must propagate the same
unnormalized compatibility mass through winning and losing terms, with a
fixed root normalization and consistent folded-player handling.

## Deck-coupled class ranks: coherent practical approximation

For each particle, shuffle a common 52-card deck. Independently sample one
uniform hole-card combo for each class. Each class takes the first five cards
from that deck excluding its own two hole cards, then evaluates its hand.
The resulting 169 class scores define one coherent latent showdown ordering.
Ties split among all tied players; the pot therefore sums to one for every
joint class tuple. Average over particles using the existing independent class
chance model. No board-mass reweighting is used.

Unlike a literal shared board, different classes can skip different cards and
see slightly different boards. This is a coupling approximation, not a physical
deal with mutually compatible hole cards. Its benefit is preserving correct
per-class board marginals while retaining substantial common-board correlation.

Original fixture, eight seeds:

| Particles | Mean absolute error | Largest error |
|---:|---:|---:|
| 128 | 2.13 pp | 6.15 pp |
| 256 | 1.74 pp | 4.83 pp |
| 512 | 1.24 pp | 4.66 pp |
| 1,024 | 0.89 pp | 2.29 pp |
| 4,096 | 0.75 pp | 1.95 pp |

Four sampled combos per class gave no consistent improvement at the increased
cost. See `coupled-audit.json` and `multiway_coupled_audit`.

### Additional synthetic range checks

Each comparison uses 100,000 compatible Monte Carlo deals for each of six
hero hands (KQo, AQo, KQs, 76s, AA, 22), four independent particle seeds
(711281–711284), and 4,096 particles. These contexts were not the original
fixture. The production-candidate seed is compared separately below.

| Opponent ranges | Mean absolute error | Largest error |
|---|---:|---:|
| Two uniform opponents | 1.20 pp | 5.02 pp |
| Five uniform opponents | 1.26 pp | 3.22 pp |
| Eight uniform opponents | 1.09 pp | 4.21 pp |
| Two tight opponents | 1.77 pp | 5.94 pp |
| Three tight opponents | 1.71 pp | 5.23 pp |
| Three pair-heavy opponents | 1.70 pp | 3.42 pp |
| Three premium-only opponents | 6.19 pp | 15.91 pp |

Definitions and exact results are in `multiway_coupled_holdout` and
`coupled-holdout.json`. The premium-only range is AA/KK/QQ/AK. Its strongest
failure is AA: 68.40% reference versus 52.96% mean approximation. This is a
large card-removal effect, not particle noise. Other residual biases include
22 against two uniform opponents (30.76% versus 34.97%) and AA against eight
uniform opponents (34.65% versus 38.22%).

### Fixed candidate seed compared with the old model

The candidate uses seed 90210 and 1,024 particles. Across the six hero hands:

| Opponent ranges | Old mean error | Candidate mean error | Old worst error | Candidate worst error |
|---|---:|---:|---:|---:|
| Two uniform opponents | 5.70 pp | 1.16 pp | 11.46 pp | 3.48 pp |
| Five uniform opponents | 13.40 pp | 1.19 pp | 17.90 pp | 2.18 pp |
| Eight uniform opponents | 12.93 pp | 1.23 pp | 17.54 pp | 3.56 pp |
| Two tight opponents | 8.74 pp | 2.04 pp | 14.72 pp | 5.33 pp |
| Three tight opponents | 10.87 pp | 1.83 pp | 17.97 pp | 4.51 pp |
| Three pair-heavy opponents | 15.44 pp | 1.10 pp | 22.90 pp | 2.48 pp |
| Three premium-only opponents | 12.30 pp | 6.09 pp | 21.57 pp | 15.85 pp |

The candidate improves the aggregate error in every tested context. It does
not improve every individual hand. In the premium-only case, AA is 68.40%
in the reference, 52.96% in the old model and 52.55% in the candidate; AQo is
5.77% in the reference, 1.35% old and 12.47% candidate. The substantial
card-removal limitation remains visible in both approaches.

For the original BB fixture this exact seed gives KQo 21.52%, AQo 19.21%,
KQs 25.38%, 76s 19.27% and AA 59.23%. These are all closer to the
compatible-deal reference than the original product calculation.

### Recommendation

Deck coupling is a coherent, testable improvement over the existing multiway
product approximation, with 1,024 particles a provisional accuracy/performance
candidate. It fixes all five original examples but does not support a claim
of generally exact equity or uniformly small error. Tight overlapping ranges
need explicit limitations and further card-removal work. Pot conservation,
CPU/GPU parity, convergence and runtime must be checked independently of the
equity fixtures before activation.
