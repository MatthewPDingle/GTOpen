# Preflop convergence follow-up — research milestone

Research branch: `codex/preflop-convergence-followup-20260911`.
The live app on port 56708 is unchanged. None of these experiments is a production
release, and the all-solver large-game results do not yet pass every local gate.

## 1. Sampling and averaging repeats

All timings below include startup and full checks through two consecutive
learning-gap measurements <= 0.005 bb. Every check uses the canonical 1,024
particles. Native save/readback time is separately retained in `RESULTS.json`.
Inputs, equity cache, fit, memory limit and the original benchmark executable
match pass 05. Code prepared concurrently with frozen-binary timings did not
change that executable; each protocol records its SHA-256.

| Fixture / candidate | Seeds | Iterations | Seconds to two full checks | Speedup over native |
|---|---|---|---|---|
| Eight-player, 64 particles, DCFR repeats | 314159 / 90210 | 1200 / 1000 | 714.078 / 577.874 | 7.11x / 8.79x |
| Eight-player, 64 particles, gamma15 | 42 / 314159 | 1050 / 1100 | 585.144 / 568.640 | 8.68x / 8.93x |
| Modeled six-player, 64 particles, DCFR | 42 / 314159 | 150 / 150 | 65.935 / 65.923 | 7.44x / 7.44x |
| Modeled six-player, 64 particles, gamma15 | 42 / 314159 | 150 / 150 | 65.497 / 63.739 | 7.49x / 7.70x |
| Small all-solver six-player, gamma15 | Three seeds at 64 and 128 | 250–325 | 2.960–4.297 | 5.63x–8.18x |

The native eight-player baseline is 5,080.600 seconds; modeled baseline is
490.637 seconds. These are time-to-global-target ratios, not time to verified
accuracy at every conditional decision. No reliable general 10x claim follows.

Every modeled candidate passes the two audited BTN learning decisions. Four
other selected nodes are fixed by the player models and are excluded from
optimal-response gates. All-solver candidates retain local failures. More
aggressive averaging sometimes makes a selected branch unreachable under its
own average; such a branch is **unverified**, not counted as passing.

## 2. Rare-branch diagnosis and actual conditional solving

In the eight-player native and sampled saves, selected SB/BB cold-call branches
have zero current opponent-prefix mass while their average strategies retain
positive mass. Their regrets stop learning against that history even though
Browse can still show the average branch. The observed problem is not a uniform
fallback caused by tiny positive-regret normalization: diagnostics found no such
fallback among the material hands at those nodes. Switching to the current
action alone does not fix the large errors. This problem predates sampling.

Implemented and tested a bounded, research-only conditional solver. It holds
saved incoming average hand distributions fixed, normalizes their positive
prefix masses, and runs fresh local DCFR in selected proper subtrees. It preserves
upstream play, unrelated arenas, action menus, payoffs, models, frozen players
and point locks. After each experiment, global and all six selected local
decisions are independently reevaluated.

| Treatment on small six-player fixture | Extra seconds, including load/global check/save | Global gap | Local gates |
|---|---:|---:|---:|
| Native, 100 iterations at two larger roots | 8.042 | 0.004135 | 2/6 |
| Native, 100 at each selected root | 9.650 | 0.003951 | 2/6 |
| Sampled, 100 at each selected root | 8.812 | 0.004661 | 4/6 |
| Native, 1,000 at each selected root | 70.159 | 0.003768 | **6/6** |
| Sampled, 1,000 at each selected root | 58.044 | 0.003942 | **6/6** |

The independent six-path audit adds about 6.1 seconds to each row. These extra
seconds are **not** included in the GPU speedup table. This is actual additional
convergence work, not earlier preview access. The unrefined native and sampled
inputs each passed only 2/6; even the older 3,000-iteration native reference left
two cold-call gates failing.

The gate rejects over 10% probability on actions losing more than 0.1 bb for a
hand with conditional mass >= 0.25%. It tests one-action deviations followed by
the evaluated policy's continuation, not a full subgame best-response guarantee.
Passing six selected paths does not qualify every branch of the game.

Refined saves are offline inspection artifacts. Local DCFR ages differ from the
unchanged global iteration counter, so normal live global continuation is not
supported. Before production use, provide a separate conditional session or
explicit local-age/state handling, automatic branch selection and large-game
validation. The underlying finite coupled-equity model remains unchanged;
physical-deal/postflop-model validation is outside these performance tests.

## 3. Full-check overhead

The existing GPU implementation already shares terminal evaluation between
best response and average EV. Full checks account for roughly a quarter of the
sampled eight-player runtime.

The new research benchmark supports coarse-to-fine checks: every 100 iterations
until a full gap <= 0.02 bb, then every 50. It still requires two consecutive
canonical checks <= 0.005. The rebuilt benchmark's default fixed cadence produced
a byte-identical small-fixture native snapshot to the frozen original.

The large seed42 run finished at the same 1,050 iterations with a **byte-identical
saved strategy**: 531.040 seconds versus 585.144 for fixed cadence, 17 checks
versus 21. Save/readback-inclusive time was 540.559 seconds. Measured full-check
time fell by 33.584 seconds; the remaining elapsed difference includes iteration
timing variation and should not all be attributed to scheduling. This is one
matched pilot, not a repeated speed guarantee. Its ratio to the original
fixed-cadence native baseline is 9.57x; a coarse-cadence native baseline was not
rerun. The primary comparison isolates scheduling against the matching sampled
fixed-cadence candidate, with identical final output.

The local audit remains identical in implication: three selected nodes pass,
one fails, and two are unreachable under the candidate's average and therefore
unverified. Faster checking does not cure conditional quality.

## 4. Variance reduction and exact reuse

Implemented a control-variate estimator screen:
`full reference mean + sampled(current particle value - reference particle value)`.
It evaluates all 1,024 cyclic offsets, 16/32/64/128 samples, 2/3/5/7 opponents,
and six synthetic levels of range drift. Full means agree with the existing
coupled evaluator to 2.78e-16. Uniform-offset bias remains at floating-point
noise; identical reference/current inputs eliminate sampling variance.

Across the tested nonzero synthetic drifts, the estimator's MSE is at most 3.2%
of ordinary sampling MSE. This is encouraging but narrow evidence: synthetic
ranges are not actual solver trajectories, and no GPU convergence speedup is
claimed. Refresh costs, reference storage, changing ranges and unclamped
estimates need end-to-end testing.

A separate conservative structural screen found 374,346 potentially reusable
conditional equity vectors in the modeled fixture, 20.1% of terminal/traverser
pairs, about 241 MiB for dense values. None qualify in all-solver fixtures.
For 261,267 qualifying pairs, folded-player reach can still change; cache only
conditional equity and apply current counterfactual mass. Pair counts are not
work-weighted savings. No cache was installed.

## Recommended next work

1. Scale the successful conditional-solving approach to the large eight-player
   fixture and add automated branch selection plus safe continuation semantics.
   This addresses the demonstrated quality failure directly.
2. Implement a bounded GPU control-variate candidate and measure real trajectories,
   memory, refresh cost and time to both global and conditional accuracy. This is
   the strongest remaining route to a dependable speedup beyond the current range.
3. Qualify any combined candidate across additional trees/seeds and saved-game
   continuation before offering it as a live option. Keep main and 56708 unchanged
   until those checks pass. Fixed-policy caching is secondary because it cannot
   accelerate general all-solver games.

## Evidence and validation

- Machine-readable timings and explicit local outcomes: `RESULTS.json`.
- Conditional solve outcomes: `REFINEMENT-RESULTS.json`.
- Current/average reach, regret and reuse diagnostics: `learning-diagnostics-summary.json`.
- Exact inputs/executables, exit codes, timings and full audit rows: `raw/`.
- Five research sampling/schedule/quality/refinement tests passed after correcting
  a test-only `usize` versus `u32` point-lock key compile error. The failed build
  record is retained; it is not counted as a successful test.
- Two variance-estimator tests passed; diagnostics and all refinement runs
  completed normally. The default solver suite passed **181 tests**, with five
  explicitly ignored tests not run, exit 0. See `raw/final-default-suite-exit.json`
  and its log. All 16 timed GPU runs, including the default-behavior control,
  exited normally, reached two full checks, and preserved exact native roundtrips.
- `live-preservation.json` verifies main remains at
  `92c86ed73aa0856df8479b5c7635e1469f48f1e8`, with PID 99900 still serving 56708
  from the existing qualified production executable. Session endpoints were
  read only; no server restart, deployment or session mutation was performed.
