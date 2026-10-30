# Exact river call/fold reference qualified

The 2026-09-29 probe passed on its first execution. This supplies exact targets
for a bounded learning diagnostic. It does not establish better preflop ranges.

At five fitting depths, the native trees contain 476 river decisions with
exactly fold/call. The native terminal audit confirms that every admitted call
ends at showdown. Both players are represented at every depth. Independent
public cash-flow calculations agree with the native terminal values to 8.89e-16 bb.

| Stack | Admitted states | Distinct calling prices* | Equity needed to call |
|---|---:|---:|---:|
| 20 bb | 36 | 5 | 5.84%-35.09% |
| 40 bb | 70 | 7 | 4.78%-35.35% |
| 100 bb | 110 | 12 | 9.70%-35.09% |
| 200 bb | 118 | 15 | 9.60%-35.09% |
| 400 bb | 142 | 16 | 21.95%-35.09% |

*Counting prices after rounding to nine decimal places. This is the coverage of
these restricted native menus, not all possible poker prices. The opponent's
holding distribution is deliberately uniform among legal hands; it is not an
inferred range conditioned on the preceding bets. Some bets are all-ins and
others leave chips behind. This is a diagnostic of price/hand-value learning.

Twelve probe boards include fixed royal-board, quads-board, dry-board and
four-flush cases plus eight deterministic random boards. Every board has 1,081
legal hero holdings and 990 legal opponent holdings per hero. All 12,972 holding
ranks and 12,842,280 directed legal private-hand pairings agreed between native
enumeration and a separate Python evaluator that maximizes over every five-card
subset. Tie classes and ordering matched exactly. Card/suit transformations,
probability mass, win/loss complement symmetry, nuts and board-only ties passed.

Across all probe boards and admitted public states, 6,174,672 call values agreed
between endpoint-weighting and the equity/calling-price formula; maximum error
was 1.14e-13 bb. Choosing the higher-value call/fold action has zero calculated
regret, choosing the opposite loses the absolute advantage, and a 50/50 mix
loses half that amount. Nine malformed-input cases were refused.

Separate readback verified 204 source/evidence files and 22,848 selected values
using exact rational arithmetic (maximum float discrepancy 3.56e-15 bb).

The whole invocation took 188.797 seconds, mostly the existing global storage
inventory. Each board worker took 0.297-0.406 seconds, including native exports,
independent ranks, count comparisons and publication. The native conditional
enumerations totalled 0.427 seconds of component elapsed time across boards. These component
times must not be represented as the full invocation's speed. Eight hidden
workers were allowed; all 115 owned worker/descendant processes exited normally.
No GPU allocation was needed for this probe.

The 59 compressed evidence files use 0.337 MB allocated / 1.146 MB logical.
Global allocated research storage at admission was 740.163 GB, within the 800 GB
cap. No old evidence was deleted. No model was fitted and no final test scored.
Held-out depths 60/150 bb had no strategic labels generated or read. All probe
board groups must be excluded from subsequent fitting, validation and final tests.

## Next action

Implement the bounded supervised comparison in STACK-PRICE-LEARNING-PLAN.md,
qualify its visible feature adapter against retained native observations, and
freeze its registration before fitting. This uses exact answers to diagnose
learning quality before another broad self-play experiment. A passing result
still needs a subsequent multi-decision reference with an independent best
response before supporting a full preflop-model claim.

## Evidence

- stack-price-reference-control-v1-registration.json
  SHA256 aad577169e3c0cc688cd0ef988bc4db64c070515d2227ae3b1605804cca5801e
- stack-price-reference-control-v1-result.json
- stack-price-reference-control-v1-readback-v1.json
- tools/research/stack_price_reference_v1.py
- tools/research/stack_price_reference_control_v1.py
- tools/research/stack_price_reference_readback_v1.py
- S:/GTOpen-research/stack-price-reference-control-v1

No deployment or production-session change follows. The broad research goal
remains active. Preserve the executed source and registered inputs unchanged.
