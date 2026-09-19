# Wizard-baseline continuation audit

Research in progress, 19 September 2026. No production changes.

We are testing the heads-up continuation after UTG calls LJ's 3-bet in the
completed NL25 Wizard comparison. The pot is 39.5 original bb, remaining stacks
182bb, rake 4% capped at 6bb. Both valuation methods use the same prepared ranges.
All eight original fast continuation prices reconcile with the saved call EV
after subtracting the incremental 12bb call, within 0.000004bb.

The study freezes 40 stratified flops and two separate betting-size menus
(80 explicit postflop solves). See PROTOCOL.md. Probe inclusion and negligible
range trimming are measured, not hidden: removed combination mass is 0.0489%
OOP / 0.0168% IP, and added OOP probe mass is 0.0317% of the original normalized
range mass. Fast prices are recalculated on those same perturbed ranges.

The initial global convergence check does not settle every rare probe hand.
A separate precision pass selects failures of the preregistered hand-level
check, preserving original references. See precision/PROTOCOL.md. No inference
about all-flop values should be made from the first few completed boards.

Run from the repository root with Python 3.12 and NumPy:

```
python tools/research/wizard_continuation_study.py run
python tools/research/wizard_continuation_precision.py prepare
python tools/research/wizard_continuation_precision.py run
```

The initial runner has a process lock and skips validated completed jobs. Do
not run two reference batches concurrently. Never rerun `prepare` over a frozen
manifest. Each job checks that production is idle; all solves are offline.
The runner emits local `status.json` and per-job logs. Raw references and input
hashes are retained. A failed quality check requires review, not silent deletion.

The live app on 56708 and the completed baseline save are preserved. Jev is
deferred. The reserved Wizard 100bb cases remain unopened.
