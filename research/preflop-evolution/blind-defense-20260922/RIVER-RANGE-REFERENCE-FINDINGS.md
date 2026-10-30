# Weighted opponent-range reference v2 is qualified

Use river_range_reference_v2.py for future payoff calculations. V1 passed its
original cases but failed an additional extreme-weight check; that failure and
the unchanged original implementation are retained below and in the amendment.

The new CPU reference accepts a nonnegative opponent reach vector over all
1,081 board-legal holdings, removes card conflicts separately for each hero
holding, and calculates terminal river Fold/Call values. It does not predict
an opponent range, train a model or solve a betting game.

The v2 control passed on all 12 retained probe boards and eight fixed weight cases:
uniform, lognormal, zero, single-hand, sparse and tiny surviving mass beside a
large blocked weight, plus smallest-positive-float single and uniform ranges.
Those boards are separate from the queued learning
experiment. Their original native ranks and independent rank qualification
were reused without alteration.

| Check | Result |
| --- | ---: |
| Hand/range outcome-mass rows | 103,776 |
| Terminal payoff rows across ten existing public states | 1,037,760 |
| Maximum normalized mass error against filtered sums | 1.01e-15 |
| Maximum normalized mass error against scalar math.fsum | 7.11e-16 |
| Maximum equity difference | 7.78e-16 |
| Maximum native-endpoint payoff difference | 6.26e-13 bb |
| Invalid input cases rejected | 12 |

Uniform weights reproduced the original integer win/tie/loss counts exactly.
Scale, suit relabeling, hole ordering and board-order controls passed. A
single supported opponent holding leaves exactly 990 supported hero holdings.
Zero compatible mass produces explicit unsupported rows with no payoff,
never an invented fallback strategy. Tiny surviving ranges remained supported.

The implementation sums nonnegative outcome contributions directly. It avoids
subtracting blocked masses from nearly equal totals, which could erase tiny
surviving ranges through floating-point cancellation. This is mathematical
reference infrastructure; no end-to-end speed claim was tested.

The CPU-only v2 control completed in 60.313 seconds including storage inventory,
using four workers and one BLAS thread each. Retained study allocation is
11,494 bytes. A separate readback rehashed 58 source/evidence files and reproduced
the aggregate maxima. No GPU was initialized, model fitted or production
setting changed. Sources and registrations are now immutable.

## Preserved failure and numerical correction

An extra adversarial probe after the v1 control set one opponent holding to
the smallest positive float64 weight, approximately4.94e-324, on the retained
board-only royal flush. V1 correctly retained990 supported hero holdings but
returned equity0 rather than0.5. Halving the tie mass before division erased
it through floating-point underflow. V1's passed result covers its registered
six cases; it is not a qualification of this additional boundary.

V2 normalizes win/tie/loss masses before applying the half-tie share and rejects
nonfinite accumulated mass/payoffs. Its control reproduced the old failure,
then checked the fix against scalar single-opponent outcomes and the original
integer uniform counts. The independent expected-payoff arithmetic was also
corrected to normalize first; the discrete-outcome checks prevent repeating
the same mistake in both implementations. Tolerances were not relaxed. See
RIVER-RANGE-REFERENCE-NUMERICAL-AMENDMENT.md.

## What remains before use with the full trainer

The vector supplied to this calculation must be the opponent's entry weights
times actual prior-action likelihood at a fixed public state, before hero-card
exclusion. The full research trainer already constructs such conditional
posteriors per visible decision. This new all-holdings reference still needs a
binding check against those real native history exports; its synthetic weight
tests do not establish that integration.

A bounded next control can use retained TRAIN cases and frozen played policies:
reconstruct a common opponent reach vector across several hero holdings at the
same public board/history, check every overlapping hand weight, then compare
the reference's conditional payoffs with the existing per-hero exact posterior
calculation. Preserve zero support, actual history keys, current-policy identity
and canonical card mapping. No hidden opponent cards enter model inputs.

The ongoing 362-versus-387-input experiment remains unchanged. Neither this
control nor a successful uniform-opponent learning result establishes accurate
range-conditioned continuation, equilibrium or complete preflop ranges.

Evidence: river-range-reference-control-v2-registration.json (SHA256
2b21da81719612fae1c065d1c5d197f2169ea606b993382bb05b81447543083d),
river-range-reference-control-v2-result.json and retained per-board records
under S:/GTOpen-research/river-range-reference-control-v2. The separate v1
registration, result and store remain unchanged.
