# Why the BB overcall range is too tight

Diagnosis and replacement validation, 10 September 2026. The reproduction below records the original model.

## Reproduction

The captured game has seven Solver seats, 200 bb stacks, 0.5/1 bb blinds,
5% rake capped at 2 bb, and calibrated continuation. At iteration 450 its
summed best-response gap is 0.00494848 bb.

Line: UTG raises to 2 bb; MP, HJ and CO fold; BTN calls; SB calls; BB acts.
API path: `[2,0,0,0,1,1]`. The pot is 7 bb; BB adds 1 bb to close the action
and see a four-player flop. KQo folds 99.2081% and calls 0.7918%.
All seven profiles are null and all frozen flags are false.

The snapshot is in [node.json](node.json) and [session.json](session.json).
These are diagnostic inputs, not full saved solver sessions.

## Finding

The original CPU and CUDA terminal evaluators multiplied heads-up equities
against each live opponent. For KQo these are approximately 43.12%, 38.07%,
and 34.55%, giving only **5.67%** four-way equity.

This treats the outcomes against different opponents as independent.
They share a board: when KQo makes a strong hand, it often beats multiple
opponents together. Conversely, AA does not receive the same downward bias.

One million shared-board deals per tested hand, with compatible live hole
cards and split ties, give the following comparison against the *same fixed
arriving ranges*:

| BB hand | Production product | Shared-board equity | Monte Carlo 95% half-width |
| --- | ---: | ---: | ---: |
| KQo | 5.670% | 20.798% | 0.079 percentage points |
| AQo | 11.576% | 20.422% | 0.072 percentage points |
| KQs | 7.252% | 24.080% | 0.083 percentage points |
| 76s | 3.763% | 19.991% | 0.078 percentage points |
| AA | 62.040% | 58.827% | 0.096 percentage points |

As a check on the cause, multiplying pairwise outcomes measured on these
same compatible deals still gives only 6.094% for KQo, versus 20.798% for
its actual share. Cross-opponent card removal alone does not resolve the
independence error.

Keeping the production starting-pot rake (0.4 bb) and BB realization weight
(0.973333), the call-minus-fold proxy for KQo changes from **-0.581 bb** to
**+0.539 bb** when only the equity estimate is replaced. This is a local
valuation comparison, not a re-solved strategy or full postflop EV.

## Scope and implications

- `calibrated` uses its fitted hand factors only at heads-up flop terminals.
  This four-way terminal takes the static positional fallback in
  `PreflopSolver::terminal_value`; CUDA mirrors it in `kernels.cu`.
- `raw` still uses the same multiway equity product. Changing that dropdown
  does not fix the underlying equity error.
- The small convergence gap measures convergence to these approximate
  payoffs. More iterations cannot correct the payoff model.
- The BTN/SB ranges are already narrow (about 49 combos each), and were
  themselves learned under approximate continuation values. This experiment
  holds them fixed; a corrected equilibrium may move every player's range.
- Sampling uses one representative suit combination per tested class;
  class-only ranges are suit symmetric. Entire conflicting hole-card tuples
  are rejected, avoiding sequential sampling bias. Folded-player card
  removal and future betting/rake are not modeled. Confidence intervals
  describe Monte Carlo noise only, not model uncertainty.

The replacement is `coupled_deck_v1`: a fixed latent hand-strength model
that preserves shared variation and distributes one net-of-rake pot among
three or more live players. It is a coupled-deck approximation, not literal
compatible-card dealing. [Alternative-model validation](alternative-models.md)
includes the rejected candidates and important narrow-range failures.

The production implementation reproduces the fixed-seed audit (KQo 21.52%
versus the 20.80% compatible-deal reference). Pot conservation, split ties,
CPU traversal, versioned saves, and CPU/GPU equivalence pass. The full CPU
suite passes; GPU validation includes mixed ruled/live seats and all 169
classes at 3/6/9 seats. [GPU runtime evidence](gpu-runtime.json) records the
initial three-iteration benchmark, not total convergence time.

Legacy saves keep their original model. A fresh build is required to change
payoffs; old arenas are never continued against the new model. Heads-up
realization and its embedded training rake remain separate limitations.
Multiway continuation still omits future betting. This change fixes a major
source of excessively tight ranges, not every approximation in preflop EV.

## Run again

From the repository root, using its existing equity cache:

```sh
cargo run --release -p solver --example multiway_equity_audit -- research/multiway-equity-audit/node.json cache/preflop_eq169.bin research/multiway-equity-audit/session.json 1000000
```

The diagnostic only reads JSON/cache files and prints results. It does not
build or solve a new preflop tree, call the server, or modify sessions.
Full numerical output: [results.json](results.json).

Equity-cache SHA-256 used for this comparison:
`78b4656ddace5efdb84c77811e9e7891982fb9180d9909a770e7ca4a28fd27ad`.
