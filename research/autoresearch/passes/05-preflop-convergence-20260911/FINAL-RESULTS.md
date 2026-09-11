# Preflop convergence feasibility results

The strongest measured improvement is **7.69x faster to the same global stopping
target** on the original large eight-player game: 84m 41s becomes 11m 01s.
The adaptive Ignition-model fixture improves **5.12x**, from 8m 11s to 1m 36s.
This is actual computation to two passing full-model checks, not earlier preview
access. It is not yet a 10x result or a production-qualified improvement.

The remaining obstacle is decision quality on rare branches. Both the original
and accelerated all-solver strategies fail some selected local checks even after
passing the global target. The modeled fixture passes its two selected learning
nodes; four other inspected nodes are forced by profiles and cannot count as
convergence successes. The live app on port 56708 was not changed.

## What was changed

Research-only code rotates 64, 128 or 256 of the existing 1,024 multiway equity
particles during each player's learning update. The sampled set changes, rather
than permanently removing most particles from the game. Full convergence checks
restore all 1,024 original particles. Tree, actions, rake, player constraints,
heads-up continuation model and stopping threshold remain unchanged.

This estimator is unbiased for the existing finite terminal mean at fixed inputs.
That does not prove multiplayer convergence, remove the underlying equity-model
approximations, or establish exact physical-card equity. No neural network,
range predictor, additional hand histories, warm start or action pruning was used.

Separate experiments changed the iteration discount schedule. The best small
six-player schedule-only result was about 1.25x; it has not been validated as a
large-tree improvement. Combining HS15 with 128 samples did not improve over
ordinary 128-sample DCFR in the small screen.

## Matched measurements

Time is initialization plus learning plus full checks through the second
consecutive summed learning-gap result <=0.005bb. It excludes the later offline
local audits. Save/reload time is shown separately in the machine-readable data.

| Game and candidate | Iterations | Time to target | Baseline / candidate |
|---|---:|---:|---:|
| Eight-player native, 1,567,754 nodes | 1,050 | 5,080.60s | 1.00x |
| Eight-player 128 samples, seed 42 | 1,050 | 940.73s | 5.40x |
| Eight-player 128 samples, seed 314159 | 1,100 | 972.48s | 5.22x |
| Eight-player 64 samples, seed 42 | 1,100 | 660.54s | 7.69x |
| Modeled six-player native, 1,845,520 nodes | 150 | 490.64s | 1.00x |
| Modeled six-player 128 samples, seed 42 | 150 | 95.79s | 5.12x |

All six large trials exited successfully, produced two passing full checks, and
preserved strategy arenas exactly through native save/reload. Within each pair,
input, executable, equity-cache and realization-fit hashes match. The large
64-sample result and modeled comparison each have only one sampled seed.

The smaller six-player screen (23,038 nodes) found 128-sample improvements of
4.0-4.4x across three seeds and a 5.8x improvement for one 64-sample seed.
Independent CPU global checks agree with GPU gaps within 1e-6bb. Tiny three-player
controls are correctness checks, not useful speed benchmarks; native and explicitly
configured original DCFR produced byte-identical saved strategies there.

The eight-player 64-sample run spends 491.48s learning and 166.73s checking.
Native learning takes 4,920.68s. Learning work alone is therefore about 10x faster,
but checks account for 25.2% of accelerated wall time: **the delivered global
convergence-time result is 7.69x**. Save/reload-inclusive totals are 5,090.43s
versus 668.08s, about 7.62x. Modeled totals are 502.49s versus 105.23s, about 4.78x.

Every timed run uses a 23,000 MB GPU budget. The eight-player allocation enables
the heads-up cache with 32-particle batches; the modeled allocation disables that
cache and uses 31-particle batches. Comparisons are matched within each fixture,
not between the two games or against a live app with another allocation budget.

## What the local audits mean

For each saved strategy, inspect BTN facing an open, SB and BB after cold calls,
BB facing an open with earlier folds, and BTN/BB in a limped line. Evaluate both
against its own arriving ranges and continuation play, and against the reference
strategy. A separate reference-self check exposes weaknesses in the reference.

The gate rejects more than 10% probability on actions losing over 0.1bb for a hand
class with at least 0.25% of the arriving range. These are one-step deviation
diagnostics under the existing payoff model, not full subgame best responses or
a claim about unaudited branches. Forced/frozen choices are excluded from
learning gates. Unreachable or missing checks cannot count as passes.

All-solver six-player candidates, including native, fail four of six self-policy
checks. A tighter 3,000-iteration native reference still fails two cold-call
checks; it reached a 0.000254bb global gap but not its requested 0.0001bb target.
The eight-player candidates and native baseline likewise retain local failures.
Thus the earlier cross-reference failures were not solely differences between
two strategies: own-policy checks also find locally inferior choices.

The adaptive modeled candidate and baseline pass the two inspected BTN learning
nodes, both against themselves and the baseline. The other four nodes have
profile-forced behavior. This supports the measured result in those specific
modeled lines, not every adaptive response in the tree.

Rare lines can carry negligible weight in the global metric while being central
to a user's study. For example, the eight-player native SB cold-call line has
independent-model joint reach about 0.00000518 but conditional average one-step
action loss about 1.54bb. The joint reach is an internal independent-range model
quantity, not an observed population frequency.

V2 audit outputs are retained. V3 corrects path coverage for equal blinds: SB
must check for free in the limped line to reach BB, since no fold exists there.
V3 requires all six distinct paths. This changes audit coverage only; timed
strategies and acceptance thresholds are untouched.

All 11 V3 audits completed normally with six paths each. The eight-player native,
64-sample and second 128-sample seed fail four self-policy gates; the first
128-sample seed fails three. No all-solver candidate passes every selected local
gate, so none is promoted as a qualified replacement.

## Recommended next work

1. **Make branch convergence a measured requirement.** Investigate the rare-line
   failures, including reach weighting and average-strategy accumulation. Then
   test extra learning work on deficient branches with their actual arriving
   ranges, legal actions and fixed profiles preserved. Recheck both those lines
   and the full game afterward. The output must be improved converged decisions,
   not a preview relabeled as a solution.
2. **Close the remaining global performance gap with small experiments first.**
   Repeat 64-sample large tests with more seeds; compare gamma15 plus sampling;
   screen cheaper or better-timed full checks. Retain the threshold and two full
   passing checks, and compare changed schedules against equally scheduled native
   baselines. Do not project combined gains or remove validation time from the
   advertised total.
3. **If sampling noise limits progress, test a variance-reduced estimator.**
   Reuse a periodically refreshed full evaluation and sample the change from it.
   Measure memory, reference-refresh cost and total time. The detailed proposal
   in [NEXT-CANDIDATES.md](NEXT-CANDIDATES.md) is unimplemented and has no measured
   speedup. Neural value prediction is a later option if these methods fall short.

The release gate should be elapsed time to the global target **and** acceptable
selected-line quality across representative all-solver and modeled games.
The current research is a promising starting point, not a qualified 10x release.

## Validation and evidence

- `cargo test --release -p solver`: passed, including the default solver suite
  and documentation tests; manually ignored benchmarks/stress tests stayed ignored.
- Both research-quality unit tests passed, including independently summed
  heads-up call/fold payoffs under a nonuniform range and input immutability.
- Both research sampling/schedule unit tests passed.
- The updated research audit example built successfully. Offline audit executions
  and their independent snapshot/executable hashes are recorded in `raw/`.
- Normal process exits, two full global checks and native save/reload equality
  are recorded for every large timed trial. GPU and CPU timing work ran serially;
  a read-only guard stops owned research if live solve/report work starts.
- No production deployment, server restart, live session replacement or main-branch
  merge was performed. A full GPU regression/release qualification remains future
  work before deployment.

[comparison.json](comparison.json) contains matched global ratios.
[summary.json](summary.json) contains per-trial timing and audit status.
[local-v2-summary.json](local-v2-summary.json) summarizes the latest expanded audit
revision per trial, with own-policy and reference-policy outcomes kept separate.
[PROTOCOL.md](PROTOCOL.md) records the experiment and audit rules.
