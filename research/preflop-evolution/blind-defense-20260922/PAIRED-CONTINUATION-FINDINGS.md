# Continuation sensitivity remains substantial, alongside card noise

25 September 2026. The fixed same-card diagnostic completed all 10,816 reused
deals (64 per hand class), all four crossed continuation profiles and both
forced root actions. The separate scalar reader passed all 338 archived batches
and 4,916,820 observations. Maximum scalar discrepancy was 1.82e-12.

This is a diagnostic of two existing learned policies, not a fresh holdout,
new solve, best-response bound or evidence that either policy is accurate.

## Main measurements

AA and BB use the two original full played banks. AB swaps only BTN's policy;
BA swaps only BB's policy. All later actions are integrated on the same sampled
private cards and board. Each bank retains its correct own-reach-weighted
behavioral average; the initial BB action alone is forced to call or raise.

The table reports incoming-mass-weighted RMS **per-class** mean effects and
descriptive standard errors, in bb. The errors are neither simultaneous
confidence bounds nor the standard error of the whole-population mean.

| Paired effect | Call: RMS mean / RMS SE | Raise: RMS mean / RMS SE | Call minus raise: RMS mean / RMS SE |
| --- | --- | --- | --- |
| Both policies, BB − AA | 2.218 / 1.372 | 5.450 / 3.119 | 5.686 / 3.124 |
| BB policy, averaged over BTN choice | 1.920 / 1.048 | 4.843 / 1.788 | 4.993 / 1.966 |
| BTN policy, averaged over BB choice | 1.021 / 0.913 | 2.543 / 2.578 | 2.480 / 2.437 |
| Interaction | 0.750 / 0.712 | 2.358 / 2.273 | 2.370 / 2.350 |

The BB-policy component produces the larger measured hand-specific differences
in this sample, especially for raising and call-versus-raise comparisons. The
BTN and interaction estimates remain particularly noisy. These RMS comparisons
are descriptive, not a formal significance test or a percentage attribution of
range error. Changing BB's continuation also changes which historical models
contribute after a given root action; it does not isolate neural fitting error.

Chance uncertainty is still large even with each policy held fixed. The four
profiles' weighted RMS class standard errors are 1.70–1.91 bb for calls,
2.94–3.19 bb for raises, and 2.44–2.53 bb for call minus raise. This budget
cannot settle small preflop action-value differences hand by hand.

The signed population-weighted BB-policy effects were −0.401 bb for calls and
−0.436 bb for raises. Similar aggregate shifts conceal the much larger
hand-specific changes above. Neither a similar overall calling total nor a
small signed effect establishes stable individual-hand recommendations.

## A limitation exposed by the comparison

A post-hoc accounting check investigated why changing BB's bank had exactly
zero effect on forced AKs calls. In both banks AKs calls only 0.008114% at the
root, exactly the contribution of the initial uniform model: 0.25 / 3,081.
Generations 1–77 contribute no additional call mass to the displayed average.
Consequently, conditional on forcing that call while retaining the averaged
continuation, BB's subsequent policy comes from the initial uniform model.
The later learned strategies are excluded by the own-reach weighting.

This is correct behavioral averaging, not a newly discovered averaging bug or
a reason to insert arbitrary minimum action frequencies. It does explain why
forcing a rarely chosen root action can test an early, weak continuation. It
does not test the best continuation the player could adopt after that action.

The check covered every class and action and passed a separate scalar review:

| Root action dominated at least 95% by generation 0 | First bank | Repeat bank |
| --- | --- | --- |
| Call | 7 classes; 3.26% of incoming class mass | 9 classes; 3.72% of incoming class mass |
| Raise | 33 classes; 24.07% of incoming class mass | 32 classes; 23.08% of incoming class mass |

These are shares of **hand-class mass**, not shares of actual calls or raises.
Generation 0 accounts for only 0.0178% / 0.0194% of all actual call mass in
the first/repeat banks. Thus the caveat matters especially when evaluating
forced alternatives; it does not mean most normally played calls use the
initial strategy. The follow-up was exploratory and did not change the fixed
study, select a new policy, or create fresh validation data.

## Decision

Do not promote a range change. The comparison supports investigating learned
continuations as well as reducing card/runout uncertainty. It does not justify
fixing selected root probabilities or labeling either seed as the right answer.

The next accuracy experiment worth preparing is action integration for the
later sampled training records, rather than only the BB root accumulator.
Preserve the existing sampled visits, physical deals and RNG stream, and test
conditional expected targets at those visited nodes before any training trial.
This needs an explicit conditional-unbiasedness argument and native/readback
controls; it is a hypothesis, not an established improvement. Board/private-
card noise and approximation capacity would remain unresolved.

Evaluation must also distinguish a forced root deviation with a fixed historical
continuation from a response that improves both the root action and later play.
Report early-generation support when interpreting forced-action values. Do not
reinterpret these results as full-game exploitability or optimal calling EVs.

The bulk runtime makes the next experiments cheaper. A separate exact-replay
test of captured GPU gradient calculations is prepared; bounded concurrent
batch evaluation is another performance candidate. Neither may alter completed
scientific outputs, and neither is a poker-quality improvement by itself.

## Cost and evidence

The worker completed in 1,084.53 seconds (18.1 minutes), followed by a 240.28-
second scalar review. Bank loading took 86.70 seconds combined; complete bank
averaging 408.95 seconds; native payoff evaluation 81.81 seconds. The remaining
time includes exports, JSON transport, checks and archiving, not a measured
single bottleneck. The compact evidence store occupies 1.372 GB measured file
allocation across 3,044 files, below its 4 GB cap. Production 56708 was unchanged.

- `paired-continuation-v1-result.json`, `-analysis.json`, `-independent-review.json`,
  `-storage.json`, terminal status and log.
- Raw authenticated batch archives: `T:/GTOpen-research/paired-continuation-v1`.
- `initial-generation-share-v1-registration.json`, `-result.json` and
  `-independent-review.json`: exploratory uniform-generation accounting.
- `PAIRED-CONTINUATION-DIAGNOSTIC-PLAN.md`: original fixed sample and estimands.
- `BULK-AVERAGE-CONTROL-FINDINGS.md`: exact inference-equivalence control.

All 169 class results, all four profiles, unfavorable outcomes and sampling
errors remain available. Broader positions, stacks, menus and multiway ranges
are still outside this study's evidence.
