# Retained-model averaging and the longer finite control

Status: longer comparison running with a verified checkpoint-reader correction.
This is a method-qualification test, not a new BB or UTG policy. Production and
the range preview remain unchanged.

The completed [highest-regret fallback comparison](SAMPLED-NEURAL-CONTROL.md)
reduced the four neural candidates' gaps by 56.9–73.4%. However, their fitted
average-policy networks were worse than exact averaging of the decisions they
actually played. The next control removes that extra approximation without
changing advantage training or the sampled learning trajectory.

## Representation

Retain each iteration's two advantage networks. At a queried decision, weight
each past model by its iteration weight and its own probability of reaching
that observation. Opponent reach does not belong in this weighting. An iteration
model that never takes an earlier own action cannot contribute its hypothetical
later strategy to the average. Initial uniform play is included; the final
newly trained model has not yet been played and is excluded.

This follows the retained-model principle of
[Single Deep CFR, sections 5.2–5.3](https://arxiv.org/pdf/1901.07621). That paper
uses linear iteration weighting; this controlled comparison retains ordinary
equal weights to preserve the existing learning experiment.

This is not constant storage. It grows with training iterations rather than
with every encountered river information set. At the registered 2,048-iteration
cap, these small models require 101,711,336 bytes of float32 parameter payload
for 4,094 played networks, before scales, temporary arrays and framework
overhead. These numbers describe the finite network, not an unknown future
physical-poker architecture. Sampling reservoirs remain bounded.

## Averaging controls

The independently written bank adapter reconstructs earlier own actions from
the public history, own card and already visible public card. It does not use
the opponent's card or future public information. Across three model choices
per player and all 24 deals, enumerating independent root model draws and
holding each selected model for the whole trajectory matches the averaged
behavioral policy's complete terminal distribution. Maximum error was 5.56e-17.

The bank average also matches the separate full-chance own-reach accumulator,
with maximum error 2.23e-16. A negative control with zero prior own reach rejects
naive probability averaging even when the unreachable model has 100 times the
iteration weight. If no retained model can reach a query, it returns a legal
uniform fallback and zero support, rather than claiming an evidenced policy.

The finite arrays used in these controls are evaluation oracles only. They are
not proposed storage for the actual poker tree. Physical-poker integration
still requires inference from observable card/history features.

## Registered learning comparison

- Same two seeds (17, 31), no-rake and raked games, sampler, network architecture,
  advantage reservoirs, 128 training steps per update and highest-regret fallback.
- Separate average-policy networks and their reservoirs are omitted.
- Shared checkpoints must reproduce the prior experiment's **entire exact
  average-policy arrays** within 1e-10, not merely similar aggregate gaps.
- At each checkpoint, save the actual model parameters and reload every retained
  model. Reconstructed played policies must match within 1e-12 before evaluation.
- Primary evaluation is the independently evaluated bank average. Stop at summed
  exact best-response gain <=0.01 in control payoff units on two consecutive
  checkpoints, or at 2,048 updates. There is no automatic extension.
- Checkpoints: 1, 16, 32, 64, 128, 256, 512, 768, 1,024, 1,536 and 2,048.
- Continuous production-idle guard, 20 GB free RAM and 3 GB free VRAM reserves,
  and a 6,000-second overall deadline. Any guard failure retains available
  checkpoints and stops only the research child.

Model-bank checkpoints are stored under `target/research-sampled/`, with paths,
byte counts and hashes in the per-run evidence. Only the most recent complete
bank per seed/payoff setting is retained; it includes the earlier played models.
The code does not yet implement interrupted-run training resume. Original
evidence uses prefix `sampled-neural-bank-v1`; its replacement uses
`sampled-neural-bank-cached-v1`.

The first 256 updates reproduced the frozen comparison, and all saved-model
replay errors were zero at those checkpoints. The longer-run outcome remains
pending. Even a passing result here would only justify proceeding to physical
poker qualification; it would not itself validate new preflop ranges.

## Checkpoint I/O correction and preserved partial result

The original run verified seed 17/no-rake through update 768, and saved its
1,024-update model bank before becoming occupied with unnecessarily expensive
verification. The reader decompressed entire model-history arrays each time it
indexed one iteration. This made verification work grow quadratically.

A frozen-copy probe compared 168 array slices; all were exactly equal when
each array was loaded once and indexed from memory. The small timing comparison
was 2.576 s versus 0.205 s, but the former included production-idle checks; this
is neither a clean kernel benchmark nor a solver-training speedup claim. The
cache held 50,839,008 bytes at this checkpoint.

Only the verified research child was deliberately stopped. Its partial output,
log, resource samples, terminal status and explicit interruption reason are
retained. This was an I/O correction, not an outcome-based cancellation.

The corrected reader recovered all played policies from the saved 1,024-update
bank in 2.156 seconds. Every previous completed checkpoint's entire averaged
policy matched exactly. Independent evaluation of the recovered average gave
summed deviation gain **0.0356857734**, above the 0.01 target. Previous gains
were 0.0301699934 at 512 and 0.0339510888 at 768: longer training has not yet
shown sustained improvement.

The separately registered replacement restarts from the original deterministic
seeds because training reservoirs were not checkpointed. Sampling, fitting,
architecture, budgets, stop rules and strategic evaluation are unchanged; only
saved-model reading changes. Recovery of the old snapshot runs before the
restart, so its strategic evidence is not discarded. No promotion is justified
by the recovered result.
