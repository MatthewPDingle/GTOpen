# Preflop interactive performance experiment

Four-hour research window: **10 September 2026 23:03:27 UTC to 11 September 03:03:27 UTC**. In progress; no approximation is qualified for default use yet.

The target is time to a useful preflop strategy and exported postflop spot. This pass allows explicitly versioned evaluator approximations, measured separately from implementation-only speedups. It does not train player-behavior ranges or restore the old product-of-heads-up-equities shortcut.

## Current evidence

- The already-optimized production server first published its fresh eight-seat strategy at iteration50 after **308.38 seconds** in this run. This is the comparison baseline, not the slower version before the previous research pass.
- A deterministic64-particle representative subset of the1,024-particle coupled evaluator passed the ordinary independent physical-equity checks and the cheap-BB-call regressions. The new overlapping-range stress is borderline under the registered uncertainty rule, not an unconditional pass.
- On the small three-seat development tree, the candidate passed global strategy-loss limits at iteration10 and20, but selected individual decisions still failed. An iteration2 display is only an early preview.
- The first large eight-seat64-particle run completed50 iterations and its own-model gap check in29.28seconds, including construction/GPU initialization and six CPU previews. Full-reference paired timing and large-game policy quality remain pending. This is not yet a qualified end-to-end speedup.
- Four focused CPU/GPU tests passed: frozen table identity, pot conservation/ties, partial31+31+2 particle batches, and graph replay parity. Saved model identity and preview publication metadata remain explicit.

See [the registered corpus and gates](proposals/quality-gates/README.md), [initial quality results](proposals/quality-gates/RESULTS-FIRST-PAIR.md), and [the research contract](program.md). Raw run logs and frozen per-run protocols are in `raw/`; large native checkpoints stay in the isolated lab's ignored `target/research-preview/` directory.

## Isolation

Experiments use a separate worktree and owned private processes. The guard polls the user's server on56708 and stops the research child if a solve/report starts. No experimental model has been deployed to that server during this pass.

Candidate names identify different payoffs. A saved preview solve must never be relabeled or resumed as a full-reference solve. Policy comparisons copy average strategies into a fresh evaluation workspace; they do not reuse approximate regrets as reference learning state.
