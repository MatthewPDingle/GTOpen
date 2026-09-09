# Flexible preflop modeling — development pass 1

Started 9 September 2026. This pass separates behavior prediction, continuation
valuation and runtime cost so improvements in one are not mistaken for proof
of the others. No raw histories or session-level observations are published.

| Research path | First deliverable | Evidence |
|---|---|---|
| Contextual opponent behavior | Versioned Ignition NL10 re-raise predictor in the runtime and editor | [Usage and design](../../docs/contextual_preflop.md), [retrospective prediction comparison](../ignition-reraise/README.md) |
| Runtime cost and correctness | Representative traces, whole-range parity, source/fallback fixtures and CPU cost measurements | [Benchmarks and charts](benchmarks/index.html) |
| Continuation values | Matched HU ranges, three selected flops, paired rake settings | [Audit and charts](continuation/README.md) |

The [progress page](index.html) brings the separate paths together. This is the
first recorded comparison for this development pass; it does not fabricate a
historical improvement curve. Repeatable benchmarks retain later runs so the
same metrics can be tracked as implementations change.

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

1. Extend the continuation audit to a weighted, held-out flop set and broader
   reaching ranges. Model both players' continuation values and rake jointly;
   inspect accounting before considering a replacement predictor.
2. Measure strategy sensitivity to plausible opponent predictions, including
   sparse cheap-call contexts. Distinguish stable decisions from actions that
   depend heavily on uncertain inputs.
3. Reserve genuinely fresh histories before further model selection. Target
   missing positions, table formats, raise depths and prices. Evaluate transfer
   to equal blinds and larger tables explicitly, including the saved $2/2 and
   $2/5 formats, before enabling contextual inference there.
4. Use the validated continuation cases as a foundation for a range-conditioned
   value model, then selective multiway work. Larger neural models come after
   the benchmark and evidence coverage justify them.

The first pass changes opponent behavior only when its separate library entry
is selected. Production continuation pricing is not changed by the audit.
