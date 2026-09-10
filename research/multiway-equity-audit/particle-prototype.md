# Shared-board particle feasibility audit

This is an offline experiment against the saved BB decision and the existing
one-million-deal, compatible-card Monte Carlo references. It does not change
production pricing or the running game. Results are in `particle-audit.json`;
the reproducible example is `multiway_particle_audit`.

## What was tested

Eight deterministic seeds, each using nested prefixes of 32, 64, 128, 256,
512, 1,024, 2,048 and 4,096 uniform five-card board samples. Five hands were
compared: KQo, AQo, KQs, 76s and AA.

On each board, opponent ranges are categorical distributions of hand ranks.
An exact polynomial calculation splits ties among all tied opponents. Unlike
the old product of unconditional heads-up equities, all opponents therefore
share the same board.

Four variants were evaluated:

- **One combo:** one uniformly sampled board-compatible combo per class,
  shared by hero and all opponent distributions.
- **Four combos:** four samples with replacement per class.
- **All combos:** enumerate every board-compatible combo per class.
- **Hero excluded:** enumerate all combos and remove the hero's exact two
  cards from each opponent's distribution before calculating its CDF.

Each board is importance-weighted by the available hero combo fraction and
the product of board-compatible opponent range masses. The hero-excluded
variant also includes hero card removal in those masses. Equity is a ratio
of weighted share to weighted opportunity mass. Omitting this conditioning
badly overweights ace-containing boards for AA and increased its error to
approximately eleven percentage points in an initial diagnostic.

All variants still permit two different opponents to hold overlapping hole
cards. They are approximations, not compatible-deal equity calculations.

## Results

Errors below are **percentage points of equity**, pooled over eight seeds and
five hands, against the compatible-card Monte Carlo reference.

| Variant | Boards | Mean absolute error | RMSE | Largest absolute error |
|---|---:|---:|---:|---:|
| One combo | 32 | 4.83 | 6.20 | 20.09 |
| One combo | 64 | 3.72 | 4.86 | 11.80 |
| One combo | 128 | 3.26 | 4.20 | 11.61 |
| One combo | 256 | 2.77 | 3.54 | 8.47 |
| One combo | 4,096 | 2.20 | 3.29 | 7.29 |
| All combos | 256 | 2.37 | 3.35 | 7.71 |
| All combos | 4,096 | 2.20 | 3.17 | 7.28 |
| Hero excluded | 32 | 4.74 | 5.63 | 12.58 |
| Hero excluded | 64 | 3.47 | 4.16 | 10.45 |
| Hero excluded | 128 | 2.15 | 2.70 | 8.11 |
| Hero excluded | 256 | 1.93 | 2.36 | 4.85 |
| Hero excluded | 1,024 | 1.45 | 1.83 | 4.10 |
| Hero excluded | 4,096 | 1.32 | 1.72 | 3.98 |

## Interpretation

Shared boards fix the major missing positive correlation for hands such as
KQo and suited connectors. However, simply replacing the old formula with a
small fixed set of independent categorical ranks does not produce reliably
accurate pricing. More boards alone cannot remove card-collision bias.

Hero card exclusion is material here because the opponents' narrow ranges
contain many of the same strong ranks. Even after that correction, AA remains
about four points too high and 76s about two points too high under the
cross-opponent independence approximation.

For this fixture, 32–128 naive board particles are too noisy; 256 with hero
card exclusion is a useful experimental starting point, not validated
production accuracy. Any production approximation needs explicit accuracy
and performance gates against compatible shared-board simulation, including
strong card removal cases, same-class matchups, and tie/pot conservation.
The five-hand, single-range fixture cannot establish general accuracy.
