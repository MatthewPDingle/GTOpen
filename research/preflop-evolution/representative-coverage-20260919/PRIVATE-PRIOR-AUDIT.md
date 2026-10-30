# How board sampling changes the entering hand distribution

This chance-only audit reads board manifests and the frozen entering ranges,
not reserved strategic outcomes. It leaves every registered experiment
unchanged. Exact physical-card compatibility and all 24 suit relabelings are
included for the supported 322 opener and 106 reraiser combinations.
The supplied entry ranges remain fixed and earlier folded-card posteriors
are omitted, as in the connected study.

Restricting possible flops also reweights private hands: a hand blocking many
sampled boards appears less often in that finite game. This is separate from
whether a sample adequately represents sets, draws, and other postflop values.

| Panel | Target distribution | Joint private-pair variation | Opener hand-class variation | Reraiser hand-class variation |
|---|---|---:|---:|---:|
| Two development flops | Full deck | 6.128% | 4.227% | 4.483% |
| Ten training flops | Full deck | 3.957% | 2.239% | 2.185% |
| 47 training flops | Full deck | 0.541% | 0.360% | 0.323% |
| Original ten reserved flops | Full deck | 2.910% | 2.330% | 1.687% |
| Independent 95 reserved flops | Eligible complement | 0.461% | 0.334% | 0.235% |

Variation is total variation distance: the amount of probability mass that
would have to be redistributed to match the target. It is **not** an EV error,
a confidence level, or the fraction of incorrect strategy decisions. None of
these panels completely removes a private pair with positive target mass.

The 47-board panel reduces this particular distortion substantially compared
with ten training boards. The largest opener hand-class share discrepancy
falls from 0.798 to 0.077 percentage points; the reraiser's falls from 2.120 to
0.161 points. This supports the broader panel's structural coverage, without
establishing its strategic accuracy or adequate hand-making opportunities.

The 95-board sample targets the eligible complement after excluding complete
training/development and original reserved suit orbits. That population
contains 21,100 of 22,100 physical flops. Its joint private-pair distribution
differs from the full population by 0.0327% total variation. This small
private-prior difference does **not** make it a full-deck validation sample:
excluded postflop outcomes can still have different strategic values.

## Independent checks

The sparse physical-pair enumeration reproduces the previously recorded
dense enumeration for the two- and ten-board panels within 1.5e-16 total
variation. The 47-board normalizer agrees with the running solver within the
registered 1e-7 relative tolerance. For the eligible population, the exact
full-deck count C(48,3) for each compatible four-card private deal is reduced
by the complete excluded flop orbits. No Monte Carlo estimate is used.

See [raw audit](chance-private-prior-audit.json) and
[audit code](../../../tools/research/chance_prior_audit.py).
Source hashes are recorded. Continue to compare policies under a common
entering prior and evaluate their values on complete independent panels;
this audit cannot replace those steps.
