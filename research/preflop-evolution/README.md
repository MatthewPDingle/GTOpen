# Flexible preflop modeling — development passes 1–2

Started 9 September 2026. This pass separates behavior prediction, continuation
valuation and runtime cost so improvements in one are not mistaken for proof
of the others. No raw histories or session-level observations are published.

| Research path | First deliverable | Evidence |
|---|---|---|
| Contextual opponent behavior | Versioned Ignition NL10 re-raise predictor in the runtime and editor | [Usage and design](../../docs/contextual_preflop.md), [retrospective prediction comparison](../ignition-reraise/README.md) |
| Runtime cost and correctness | Representative traces, whole-range parity, source/fallback fixtures and CPU cost measurements | [Benchmarks and charts](benchmarks/index.html) |
| Continuation values | Matched HU ranges, three selected flops, paired rake settings | [Audit and charts](continuation/README.md) |

The [progress page](index.html) brings the separate paths together. Repeatable
benchmarks retain each run; a new measurement is not automatically an improvement.

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

1. Expand continuation evaluation to unseen ranges, pot/stack ratios, rake
   structures (including the saved $2/2 and $2/5 settings), suit textures and bet
   menus. Retain static as a serious baseline: the current candidate's small
   mean advantage over it is not established by the paired interval.
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
