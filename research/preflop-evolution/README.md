# Flexible preflop modeling — development passes 1–3

Started 9 September 2026. This program separates behavior prediction, continuation
valuation and runtime cost so improvements in one are not mistaken for proof
of the others. No raw histories or session-level observations are published.

| Research path | First deliverable | Evidence |
|---|---|---|
| Contextual opponent behavior | Versioned Ignition NL10 re-raise predictor in the runtime and editor | [Usage and design](../../docs/contextual_preflop.md), [retrospective prediction comparison](../ignition-reraise/README.md) |
| Runtime cost and correctness | Representative traces, whole-range parity, source/fallback fixtures and CPU cost measurements | [Benchmarks and charts](benchmarks/index.html) |
| Continuation values | Matched HU ranges, three selected flops, paired rake settings | [Audit and charts](continuation/README.md) |

The [progress page](index.html) brings the separate paths together. Repeatable
benchmarks retain each run; a new measurement is not automatically an improvement.

## Measured action sizing

The next behavior extension adds observed size distributions over limpers and
for 3-bets, squeezes and later re-raises while preserving hand-action frequencies.
The [7,545-raise study](../ignition-action-sizes/README.md) includes source
coverage, chronological selection gates and two graphs. Only ordinary 3-bets
supported extra position/table detail; other released situations use observed
pools. The [app guide](../../docs/preflop_action_sizing.md) explains menu routing,
compatibility and separate hand/sizing evidence.

## Pass 2

- **Behavior and uncertainty:** [16 strategy solves and 64 cross-model evaluations](behavior/README.md)
  distinguish broad opponent assumptions from narrow cheap-call stress tests.
  [Frozen-model transfer](transfer/README.md) scores 3,835 re-raise decisions in
  four separate NL5/NL25 regular/Zone groups. Average prediction improves, but
  sparse subgroups and overcalling remain; no profile or support guard is changed.
- **Runtime:** [Precomputed inference](benchmarks/README.md) is 3.20 times faster
  in the paired measurements, with identical observed f32 predictions and about
  24 KB of added numeric storage. This is an inference improvement, not a claim
  of a 3.20-times faster complete solve.
- **Continuation:** [All 192 reference solves](continuation/pass2/README.md)
  met the numerical target. The joint value/rake candidate's held-out mean
  absolute error is **0.378 bb per player**, versus **1.176** for calibrated and
  **0.419** for static. Its small lead over static is uncertain. These weighted
  estimates cover three fixed range fixtures; the candidate remains research-only.
- **Inspection:** Heads-up flop endpoints now expose a read-only continuation
  estimate: both current modeled values, their total, and the unallocated amount.
  The UI distinguishes embedded training rake from the requested game rake.
  This diagnostic calls the existing pricing function and does not alter it.

Source histories, session observations and collection manifests stay private.
Public validation contains aggregate measurements and provenance digests.

## Pass 3

- **Saved-game continuation:** [All 150 reference solves](continuation/pass3/RESULTS.md)
  met the numerical target. With current saved $2/2 and $2/5 settings and two
  transported saved range pairs, mean valuation error was **3.018% of starting
  pot** for the frozen joint candidate, **4.810%** for static and **4.951%** for
  calibrated. Paired intervals support the average improvement on these cases,
  but calibrated wins both $2/5 3-bet/call cases. Fifteen sampled boards and
  restricted heads-up betting menus do not justify general promotion; production
  pricing is unchanged. The weighting and intervals were independently checked.
- **Calling behavior:** A [first-entry correction](behavior/pass3/README.md)
  separated prior limps, cold calls and raises, with price and stack interactions.
  It did not improve overall retrospective prediction on 2,351 later decisions
  (log loss 0.485777 existing versus 0.485807 candidate). The current predictor
  is retained. Prior cold-callers are overcalled and prior limpers undercalled;
  reducing all calling frequencies would worsen one group.
- **Evidence in the app:** A compact [evidence badge](../../docs/model_evidence.md)
  identifies the source of the editor's selected policy and the policy actually
  used at a game node. Source counts are pooled coverage, not confidence scores.
  Edited ranges are checked against supplied history probabilities, and solver
  overrides take precedence. Existing profiles need no migration.
- **Data availability:** The existing NL10 source has no new files or hands
  since the prior snapshot. The current audit is retrospective development,
  not a new independent holdout. Tiny weak-hand/cheap-call cells remain the
  limiting evidence; more model complexity alone did not resolve them.

## Promotion rules

- A new behavior model must preserve probability normalization, actual-history
  conditioning, legal action handling and CPU/CUDA agreement. Old profiles and
  saves must retain their behavior; uncertainty and unsupported formats must be
  visible. Retrospective loss improvements are a reason to test a candidate,
  not proof of profitability.
- Timing and memory results must use the same workload and state whether they
  measure inference, policy compilation, tree construction or solving. A more
  detailed opponent model can cost more without changing CFR's numerical method.
- Continuation comparisons must use consistent ranges, pot/stack/rake and EV
  units. Selected-board solves are diagnostics, not an all-flop expected-value
  label or an exact unrestricted poker solution.

## Next priorities

1. Investigate the continuation candidate's $2/5 3-bet/call regressions, then
   validate on fresh ranges and richer menus. The pass-three average gain over
   static is now supported on its fixed fixtures, but is not uniform across
   cases. Keep the existing pricing available and make any future candidate
   explicitly opt-in until its supported domain is established.
2. Extend the completed strategy-sensitivity checks to broader game menus and
   reaching ranges. Keep sparse cheap-call contexts visible and distinguish
   stable decisions from actions that depend heavily on uncertain inputs.
3. Reserve genuinely fresh histories before further model selection. Target
   missing positions, table formats, raise depths and prices. Evaluate transfer
   to equal blinds and larger tables explicitly, including the saved $2/2 and
   $2/5 formats, before enabling contextual inference there.
4. Use the validated continuation cases as a foundation for a range-conditioned
   value model, then selective multiway work. Larger neural models come after
   the benchmark and evidence coverage justify them.

The first pass changes opponent behavior only when its separate library entry
is selected. Production continuation pricing is not changed by the audit.
