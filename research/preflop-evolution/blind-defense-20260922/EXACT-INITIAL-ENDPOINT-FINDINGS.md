# Exact initial all-in learning: interim findings

24 September 2026. Training, independent training readback, exact endpoint
evaluation and independent endpoint readback are complete. The wider test is
running; this document does not contain its results.

## What improved

The predeclared primary candidate uses every played generation, 0 through 77,
with linear weights 1 through 78 for both players. Generation 78 has not been
played and is excluded. No checkpoint or averaging schedule was selected from
these results.

| Restricted deviation | Previous candidate | New candidate | Reduction |
|---|---:|---:|---:|
| BB reallocates its existing fold/jam mass optimally by hand class | 0.05402144 | 0.01379349 | 74.5% |
| BTN optimizes its initial fold/call response to the BB jam by hand class | 0.05424499 | 0.01353993 | 75.0% |

Values are gained bb per original entry into the fixed spot, not per arrival
at the all-in response node. Both beat the prospective requirement of at least
25% improvement relative to the old linear/linear bank.

This supports the narrow hypothesis that exact initial all-in targets and an
exact initial BTN response accumulator improve the previously identified
all-in weaknesses. The run also changes current-policy inference to float64;
this bundled comparison does not isolate the causal contribution of each
change. Training remains fresh and uses the same 39,936-deal budget and seed
configuration as the previous pilot.

These are restricted deviation gains, not total exploitability. The BB test
does not alter call/raise probabilities. The BTN test covers only its initial
response to the BB jam. The earlier model passed a similar narrow screen but
still allowed a broader BB first-action deviation worth about 0.293 bb per
entry. Thus this result is promising but insufficient for deployment.

## Other registered pairings

The pairings below are diagnostic; they do not replace the primary bank.

| BB averaging / BTN averaging | BB restricted gain | BTN restricted gain |
|---|---:|---:|
| Equal / equal | 0.07358510 | 0.02368395 |
| Equal / linear | 0.07584721 | 0.00404528 |
| Linear / equal | 0.00844655 | 0.02943617 |
| Linear / linear — primary | 0.01379349 | 0.01353993 |

## Completed correctness checks

- Training completed 78 updates and 39,936 deals, exit zero, in 10,145 seconds
  including controller overhead.
- Independent CPU readback reconstructed all 39,936 BB root corrections,
  867,178 BB and 131,246 BTN insertion events, exact accumulator updates,
  recorded policies, chance streams, reservoirs and saved checkpoint states.
  Maximum target discrepancy: 5.69e-14 bb. Maximum policy discrepancy:
  1.25e-12. Runtime: 3,378 seconds. It did not refit the networks or rerun the
  native poker engine.
- Independent scalar endpoint review matched the four pairings to 2.88e-16 bb;
  maximum cashflow-conservation discrepancy was 1.43e-14 bb.
- The complete 78-model CPU/CUDA wider-test admission compared 29,042
  observations across all four streets, including 28,772 with own-action
  histories. Maximum policy discrepancy: 3.85e-13; reach discrepancy:
  8.87e-12; native payoff discrepancy: 2.85e-14 bb. This is a 64-deal numerical
  control, not a statistical accuracy test.

## Next test already running

`exact-initial-wider-study-v1` follows the unchanged
[prospective protocol](EXACT-INITIAL-WIDER-TEST-PLAN.md). It fits a new
class-dependent BB first action on 43,264 new training deals and evaluates six
fixed alternatives on 131,072 separate population deals. These include the
exact prior frozen response, so we can check whether that known weakness
still profits. All later play remains the new frozen bank's play.

Report all six simultaneous intervals after the fixed sample and independent
readback. No early strategic stopping, checkpoint selection or sample extension.
A smaller gain for a newly fitted response alone would not establish lower
full exploitability. Even a successful wider test does not validate other
positions, stack sizes, trees or multiway play.

## Evidence

- `exact-initial-fresh-pilot-v1-result.json`: SHA-256
  `929f5b614247b513e63babcc0716c725f11e7ee8013e4747cc42ce472f0f20c1`.
- `exact-initial-fresh-pilot-v1-independent-review.json` and its frozen
  readback registration record the full training reconstruction.
- `exact-initial-fresh-exact-v1-result.json`: SHA-256
  `ddcdd08e9b9597a120368cd7b366fc8bcc2b379b18555ab19cf9aa5bc7568516`.
- `exact-initial-fresh-exact-v1-independent-review.json` records the scalar
  review against that exact result.
- `exact-initial-wider-admission-v1-result.json` records candidate-specific
  numerical and storage admission.

Production on port 56708 is unchanged. None of these checks qualifies the
candidate as a complete, accurate preflop model.
