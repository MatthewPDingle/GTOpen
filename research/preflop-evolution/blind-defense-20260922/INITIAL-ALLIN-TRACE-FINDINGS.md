# What the proposed all-in correction changes in real old training traces

23 September 2026. Read-only diagnosis of the completed visible 302-input
trial, not a new candidate or an inspection of the running averaging trial.

The four generations were fixed at 0, 25, 51 and 77, evenly spanning the old
played bank. All eight batches per generation were retained: 2,048 BB root
updates and 168 visited BTN responses. Source metrics and batch bytes match
the completed training audit. Current-generation policies match the separately
audited catalog; no inference or new native execution was needed.

The record stream can be split at the root observations into its original
deal/updater traversals. Root regret plus the traversal value reconstructs the
sampled action payoff. Deterministic fold payoffs and policy-centred regrets
check that reconstruction. Maximum discrepancy was 1.51e-14 bb. The proposed
correction was computed separately; no original record was changed.

## Descriptive result

Ratio of corrected to original sample variance, with all four BB coordinates
shown in fold/call/raise/shove order:

| Played generation | BB observations | BB ratios | BTN observations | BTN fold/call ratios |
| --- | ---: | --- | ---: | --- |
| 0 | 512 | .3986 / .4553 / .8329 / .1717 | 128 | .2763 / .2763 |
| 25 | 512 | .9333 / .9492 / .9877 / .2869 | 14 | .0989 / .2341 |
| 51 | 512 | .9959 / .9875 / .9912 / .3472 | 14 | .1452 / .6150 |
| 77 | 512 | .9733 / .9829 / .9725 / .3392 | 12 | .1186 / .7598 |

These are finite old-sample variances, including differences between hand
classes. They are not unbiased estimates of conditional noise reductions, a
training-speed benchmark, or confidence intervals. The small BTN counts make
its ratios particularly fragile. The complete finite-population arithmetic
control separately established preservation of the expected initial targets.

The strongest practical finding is coverage: later batches visited the BTN
response only 12–14 times across 96 supported classes. Better conditional
values do not by themselves make unvisited classes learn. Also, after the
initial generation, observed ordinary-call and raise variance generally falls
only about 1–5 percent. This correction alone is unlikely to resolve the broad
calling-range problem.

## Implication for the next decision

Keep the current averaging study unchanged. If a subsequent training change is
justified, compare the limited sampled-visit correction with an explicitly
weighted exact update for the tractable initial response table. The latter
would require a new derivation and controls: accumulate population/class shove
reach times conditional regret once per iteration, preserve iteration weights,
exclude duplicate sampled records for that decision, and keep the average
strategy's own-reach weighting separate. Do not insert fictitious unweighted
visits into the existing uniform reservoir. Any zero-reach generation contributes
zero regret rather than a manufactured response target.

That idea is not implemented or authorized for automatic launch here. Exact
initial all-in updates still leave sampled call/raise continuations and neural
postflop errors. The wider evaluation and the user goal of accurate ranges
across positions and stacks retain priority.

The diagnostic took 8.58 seconds on CPU. The preliminary attempt stopped before
registration because a metrics hash was looked up in the wrong audit field;
the correct per-step audit hashes were then used. No outcome was inspected or
registered evidence overwritten during that correction. This diagnostic has
not received a separate full audit of its own. Production is unchanged.
