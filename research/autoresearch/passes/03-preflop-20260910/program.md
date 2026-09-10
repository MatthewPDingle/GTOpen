# Preflop autoresearch: 10 September 2026

Run for ten hours, from 11:34:18 UTC to 21:34:18 UTC (07:04:18 Adelaide,
11 September). Scope is preflop performance only. The user authorized this
run and GitHub publication of validated improvements.

Use the Karpathy-style propose / change / measure / retain-or-reject loop
from ../../program.md. Do not replay the historical scripts or overwrite
their evidence. This directory records this pass; implementation experiments
live in the isolated worktree in run.json.

## Fixed controls

- Preserve coupled_deck_v1, all 1,024 samples, split-pot semantics, precision,
  bet menus, all game branches, model policies and convergence targets.
- Never change the live server's game or restart it during research. Its
  preflop and postflop sessions were backed up before this run. Check its
  status before each GPU experiment; pause research while user jobs run.
- One hardware benchmark at a time. Normal candidates have a ten-minute
  budget, with explicitly recorded exceptions for final convergence/tests.
- Commit each candidate in the isolated branch, save its patch, measure
  identical workload and initial state, record failures and rejections.
- Keep repeatable >2% speed gains or >5% memory gains without material time
  regression. Repeat marginal results. Implementation-exact changes should
  preserve arena fingerprints; changed accumulation order requires bounded
  numerical parity and time-to-accuracy validation, not relaxed tests.
- Correctness gates: preflop CPU suite, CUDA equivalence including coupled
  3/6/9-seat terminal and batch tests, forced/frozen/adaptive seats, legacy
  saves and new-model saves. Check postflop CUDA if shared GPU code changes.

## Rotation

1. Coupled multiway CDF/terminal throughput (current dominant cost).
2. GPU memory layout, reuse and transfers.
3. Accuracy checks and iteration orchestration.
4. CPU preflop fallback and tree/build/save/load overhead.

Primary fixtures are the user's eight-seat 150bb $2/2 tree and the seven-seat
200bb corrected BB example. Include smaller 3/6-seat controls and the legacy
model so an optimization does not silently penalize other supported games.
Measure build/init, iteration, gap check, sync, save/load, GPU memory and
time to fixed accuracy where practical. Preserve raw logs and input hashes.

At the deadline stop proposing experiments, complete validation of accepted
changes, integrate only verified changes without overwriting other work,
push to GitHub, produce the final measured summary, pause the heartbeat,
and mark the goal complete only after required work is finished.
