# Weighted river values match actual played-policy histories

The new all-holdings reference reproduced the existing per-hero native
calculation when opponent weights were derived from actual betting histories.
The main control and a separate reconstruction from saved evidence both passed.
This qualifies an input binding, not a learned model or improved preflop ranges.

The fixed comparison covered 16 public situations: both actors, both retained
generation-77 current policies, and four retained TRAIN boards. Each situation
used three disjoint private holdings to reconstruct all 1,081 board-legal
opponent weights; a fourth disjoint holding checked the result independently
of that reconstruction. Suit permutations were restored before combining
holdings. All 30,224 overlapping comparisons had consistent opponent histories
and mass. The source entry ranges passed all 24 suit permutations.

Across 64 hero holdings and 63,360 compatible opponent pairs:

| Check | Maximum absolute error |
| --- | ---: |
| Opponent mass | 8.53e-14 |
| Posterior probability | 5.56e-17 |
| Conditional equity | 1.12e-16 |
| Call-minus-fold value | 7.11e-15 bb |

All exact outcome comparisons passed. Fifty-two hero holdings had supported
opponent ranges; the other twelve remained explicitly unsupported, rather than
receiving invented values. Separately, 52 holdings had zero own-history reach.
These are structural/counterfactual checks, not a representative sample of
frequently played states. They do not establish low strategic error.

The run took 50.234 seconds including global storage accounting and input
verification. Four CPU workers used one BLAS thread each. Native children ended
normally with no active descendants. Evidence occupies 13.39 MB allocated
(52.93 MB logical) across 114 compressed files. This timing is not an
end-to-end training speed comparison.

The independent CPU readback verified 193 source/artifact hashes and rebuilt
entry times opponent-action likelihoods directly from the native histories,
saved policies, and terminal payouts. Its largest payoff discrepancy was
5.56e-17 bb. It took 2.797 seconds. Negative controls rejected incomplete
coverage, inconsistent overlapping weights, and mismatched opponent histories.

Evidence:
- `river-range-policy-binding-v1-registration.json`
- `river-range-policy-binding-v1-result.json`
- `river-range-policy-binding-v1-readback-v1.json`
- `S:/GTOpen-research/river-range-policy-binding-v1`

The registration SHA256 is
`11c2e778b60a25d95a462f8efa960df14ea87058f82b706cbb645e22a2306642`.
Executed sources and registered inputs are immutable.

The result applies to one fixed current played policy at a time, with the
source suit-invariant entry ranges and terminal river Fold/Call states.
Historical average-policy mixtures need their existing reach-weighted mixture
logic; replacing that with one unweighted average range is not justified.
It also does not replace the full-action future-tree evaluator.

The next learning result remains the separately registered relative-hand-input
comparison. Its prepared data, model selections, holdouts, and gates were not
changed or inspected by this control. If its new inputs help, the next step is
to bring them into the actual versioned training/checkpoint path and evaluate
with history-conditioned opponents. If they fail, examine the retained fitting
versus validation errors before choosing another modeling change. Do not repeat
arithmetic controls or extend training merely because those are easy to run.

No GPU training, production change, deployment, or GitHub push occurred here.
