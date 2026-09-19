# Card-compatible heads-up accounting with rake

19 September 2026. Research only. **All six fixtures passed.** Production on
56708 was not modified or restarted.

The existing experimental GPU interface now has a separate, opt-in heads-up
entry point that uses the configured rake, cap, and no-flop-no-drop rule. It
passes each terminal's net pot to the unchanged interface kernel. The older
zero-rake entry point keeps its restrictions and behavior. The new entry point
rejects games with more than two players and does not enable learned pricing.

This is more than an all-in-only test: the final two fixtures contain complete
40-node heads-up preflop trees with limps, opens, calls, re-raises and all-ins.
Non-all-in terminals still use the existing fixed Balanced approximation.

| Fixture | Final independent response gap | Expected rake per deal |
|---|---:|---:|
| Push/fold, 10 stack, zero rake | 0.000000030 | 0 |
| Push/fold, 10 stack, 4% / cap 6 | 0.000000005 | 0.327411 |
| Push/fold, 200 stack, 4% / cap 6 | 0.000000061 | 0.021561 |
| Push/fold, 50 stack, 5% uncapped, folded pots included | approximately 0 | 0.380047 |
| Full HU, 40 stack, 4% / cap 6 | 0.000001253 | 0.125081 |
| Full HU, 40 stack, folded pots included | 0.000001675 | 0.157541 |

These are configured chip units. Push/fold fixtures post 1/2; full-tree fixtures
post 0.5/1. Final policies use 10,000 iterations. The two-player best-response
gap is measured independently for the fixed-payoff class game, including rake.
Rake makes it non-constant-sum, so the earlier zero-rake minimax LP is not used
as a certificate here. Tiny negative gaps below 1e-9 are numerical roundoff.

## What was checked

- All 31,772 hand/action values across the 1,000- and 10,000-iteration snapshots,
  including rare branches: maximum independent reconstruction error
  **0.00000181 chip**, below the preregistered 0.0001 limit.
- Both root values and complete-tree best-response gaps; finite, normalized
  policies; terminal probabilities sum to one.
- Expected rake reconciles total player losses. Maximum independent conservation
  error is **0.000000031 chip**.
- Uncalled chips are excluded when a folded pot is raked. Cap binding, uncapped
  rake, and both no-flop-no-drop settings are covered.
- Zero-rake policies match the earlier experimental interface **bit for bit**.
- Read-only action-value inspection preserves the complete stored policy state.
- All **15 preflop GPU and 6 postflop GPU regression tests** passed with the
  research feature compiled and the ordinary solver path unchanged.

The Python evaluator independently enumerates physical hand pairs, reconstructs
fold/showdown and Balanced leaf values, and traverses the entire tree for both
players' best responses. It does not merely compare CPU and GPU implementations
of the original independent-class model.

## What remains

This verifies accounting, not the accuracy of Balanced postflop continuation.
Sampled class equities remain sampled. Earlier research showed that own-range
changes materially alter real postflop values; this experiment does not repair
that limitation.

Ordinary CPU queries and saved-game metadata still describe the independent-class
model. No experimental saves were written and no UI enables this research path.
Those semantics, broader performance checks, and multiway card removal must be
addressed before a production candidate exists. A heads-up chance reset within
an eight-player tree is not validated by these results.

The next useful accuracy experiment is the actual saved UTG-versus-LJ branch,
with both players' later choices adapting under one fixed compatible pair prior.
It must preserve the original positions, dead money, investments and legal tree;
recreating it as an ordinary SB-versus-BB game would change the problem. Folded
cards remain an explicit approximation unless represented in that fixed prior.

## Evidence and reproduction

- [Frozen protocol](PROTOCOL.md), [input/source/binary hashes](freeze.json)
- [Independent accounting results](review.json)
- [Regression record](regressions.json), [test output](regressions.log)
- Each named fixture contains its config and complete tree/policy/value output.
- Runner: `tools/research/card_compatible_rake_audit.py` (`register`, `run`, `review`).
- Offline executable: `card_compatible_rake_audit`, built with `preflop-research`.

Registration refuses overwrite. Run resumes only missing jobs, checks production
idle before each, and verifies frozen hashes. This experiment changes the
research-gated Rust interface; earlier studies retain their recorded source
hashes and binaries rather than having their provenance rewritten.
