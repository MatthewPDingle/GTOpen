# Preflop interactive performance experiment

Four-hour research window: **10 September 2026 23:03:27 UTC to 11 September 03:03:27 UTC**. In progress; no approximation is qualified for default use yet.

The target is time to a useful preflop strategy and exported postflop spot. This pass allows explicitly versioned evaluator approximations, measured separately from implementation-only speedups. It does not train player-behavior ranges or restore the old product-of-heads-up-equities shortcut.

## Current evidence

- The already-optimized server binary first published its fresh eight-seat strategy at iteration50 after **308.38 seconds** in the initial private API run. That harness regenerated a1024-sample pairwise equity cache; the standalone benchmark and current unoverridden server configuration use20000. Treat this as the private API configuration baseline, not a matched-input live/standalone comparison.
- A deterministic64-particle representative subset passed ordinary physical-equity and cheap-BB-call checks, but the larger one-million-deal overlap audit **failed** the unchanged error gate. The32-particle candidate also failed overlap checks. Neither is qualified for default use.
- On the small three-seat development tree, the candidate passed global strategy-loss limits at iteration10 and20, but selected individual decisions still failed. An iteration2 display is only an early preview.
- Matched eight-seat50-iteration work took302.45seconds with the full evaluator and29.28seconds with64particles:10.33times faster for the measured solver stage,8.38times including offline initialization/storage. The64-particle1,000-iteration solve took461.65seconds and passed large-game global policy gates against the full reference (excess summed gap0.00209bb; worst unilateral loss0.00119bb). Physical overlap and selected local-decision failures remain; this is not a qualified end-to-end speedup.
- The frozen128-particle candidate passed newly reserved physical-equity contexts and both overlap audits with uncertainty accounted for. Native policy and latency tests are next; passing physical checks alone does not qualify the model.
- Full-model refinement of three selected branches in the million-node game took4.43seconds including loading and restoration. Two weak local games improved below0.005bb summed local gap; one already-good baseline worsened after reset. A keep-better-baseline safeguard is being added. Prefix quality and original-continuation decision gates remain separate limitations.
- Fresh full-model policy initialization is being tested separately from approximate continuation: full learning starts at iteration0 with zero learning averages, using only the preview policy as a bounded regret prior. Small tests improved some local decisions but did not clear every gate. Large tests remain pending.
- Four focused CPU/GPU tests passed: frozen table identity, pot conservation/ties, partial31+31+2 particle batches, and graph replay parity. Saved model identity and preview publication metadata remain explicit.
- All four `preview-api-a` cases passed. Full-model early publication off/on produced exactly identical final native files, both full arenas, gaps and EVs at iteration50. First strategy publication moved from304.06s to12.09s (iteration2); first export was63.86s. The64-particle model first published at3.94s and exported at8.38s, but these early states are not quality-qualified. These are all1024-sample pairwise-cache API controls; a header-pinned20000 run is required before combining them with standalone timing. See [the cache discrepancy resolution and API parity evidence](proposals/early-preview/BENCH-API-DISCREPANCY.md).

See [the registered corpus and gates](proposals/quality-gates/README.md), [initial quality results](proposals/quality-gates/RESULTS-FIRST-PAIR.md), and [the research contract](program.md). Raw run logs and frozen per-run protocols are in `raw/`; large native checkpoints stay in the isolated lab's ignored `target/research-preview/` directory.

The corrected20,000-sample API qualification (`preview-api-b`) has now passed all four cases. Full preview off/on and standalone full50 all produced exactly the same native SHA and gap. First full snapshot was12.469s versus307.531s without early publication; the navigated export was66.187s versus307.781s. Fast64 exported at8.109s, but remains disqualified by its separate accuracy failures. See [API qualification](proposals/early-preview/API-QUALIFICATION.md) for the measured scope.

## Isolation

Experiments use a separate worktree and owned private processes. The guard polls the user's server on56708 and stops the research child if a solve/report starts. No experimental model has been deployed to that server during this pass.

Candidate names identify different payoffs. A saved preview solve must never be relabeled or resumed as a full-reference solve. Policy comparisons copy average strategies into a fresh evaluation workspace; they do not reuse approximate regrets as reference learning state.
