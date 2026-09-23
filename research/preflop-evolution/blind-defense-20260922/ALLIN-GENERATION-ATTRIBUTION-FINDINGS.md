# Early policies account for most of the measured all-in error

23 September 2026. Both candidates and every saved generation were checked.
The independent reviewer reconstructed all 78 ordered prefixes, each with all
265 decision rows, using the original complete-bank CPU constructors. Every
prefix matched exactly. Independently summed error differed by at most
1.78e-15 bb. Review time was 278 seconds; the attribution itself took 22 seconds.

## What this establishes

The output strategy averages all played policies, including the initial policy.
For the newer 302-input candidate, generation 0 and generations 1–25 contribute
**88.8% of the BB error and 75.3% of the BTN error** measured by our two exact
all-in checks. Thus much of the final average's error is inherited from early
play. The initial policy alone contributes 33.7% and 6.7%, respectively.

All numbers below are profitable unilateral response gains, in bb per original
entry into the fixed spot. Each tested generation faces its candidate's frozen
complete-average opponent. These are not per-shove gains or full-game gaps.

| Candidate / player | Initial policy | Early mean, 1–25 | Middle mean, 26–51 | Late mean, 52–77 | Complete average |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original 269 / BB | 3.95471 | 0.32449 | 0.04673 | 0.05066 | 0.18717 |
| Original 269 / BTN | 0.89041 | 0.34149 | 0.05558 | 0.02307 | 0.14708 |
| Newer 302 / BB | 4.04888 | 0.26451 | 0.02312 | 0.02880 | 0.15399 |
| Newer 302 / BTN | 0.79501 | 0.32501 | 0.08101 | 0.03155 | 0.15188 |

The groups were declared before running this diagnostic. Their sizes differ;
the table gives within-group means, not their contributions to the overall mean.
The result JSON records both definitions and all 78 individual records for each
candidate. Arithmetic averaging exactly reproduces the previous endpoint tests.

Later policies still make measurable mistakes. In particular, BB's late mean
is slightly worse than its middle mean in both candidates. The trace does not
show a uniformly improving sequence or establish that further training alone
will fix the remaining problem.

## What this does not establish

Neither the final generation nor a selected tail has been promoted. The opponent
was held fixed at the original complete average, so these measurements do not
describe two late policies playing each other. Changing averaging changes both
players and therefore requires new joint-policy evaluation. Different candidates
also face different opponents; this table is not a common-opponent ranking.

The BB test only reallocates existing fold/shove mass while retaining call and
non-all-in raise frequencies. The BTN test chooses fold/call against a shove.
Neither measures the quality of ordinary calls, later raises or postflop play.
The two gains must not be added into a simultaneous win-rate claim.

## Next experiment

Test a fixed later-weighted output average on a fresh training run, alongside
that same run's ordinary equal-weight average. Specify the weights, budget and
evaluation before training; do not choose a cutoff from this trace. Recompute
exact all-in values against each resulting opponent, and include cross-pairings
to separate changes in own policy from changes in the opponent.

This is an output-averaging experiment, not an implementation of discounted
regret training. A narrow improvement must still pass broader call/raise and
postflop evaluation before it can support any deployment decision. See the
[next experiment design](LATER-WEIGHTED-AVERAGING-DESIGN.md).

## Evidence

- `allin-generation-attribution-v1-registration.json`
- `allin-generation-attribution-v1-result.json` — every generation and fixed group
- `allin-generation-attribution-v1-independent-review.json`
- `ALLIN-GENERATION-ATTRIBUTION-PLAN.md`
- `EXACT-ALLIN-ENDPOINT-FINDINGS.md` — endpoint definitions and complete support

No production or preview model was changed. Both candidates remain research-only.
