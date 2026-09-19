# Wizard-baseline continuation audit

Research in progress, 19 September 2026. No production changes.

The 80 references are complete, including 59 stricter per-probe reruns.
Use [the reviewed results](RESULTS.md) and `precision-summary.json`.
Original references remain in `jobs/`; their `summary.json` is superseded.
All sampled probes pass the specified hand-level check. Refinement changed
the all-flop value estimates by at most 0.084bb.

The clear findings in this fixed-range call branch are a large AA undervalue
and an A5s overvalue. AA's direct explicit value is about 65.5-67.8bb versus
31.76bb from Balanced; the direct 95% board intervals remain far apart. A5s is
about 8.1-8.5bb versus 12.39bb. Other selected hands have wider or overlapping
intervals; do not infer a blanket correction or claim the range problem solved.
AA is injected at tiny weight here, so its floor sensitivity remains important.

Two follow-ups are registered and run serially after precision refinement:

- `floor-sensitivity/`: raise the four tiny OOP probe weights from 0.001 to
  0.01 and repeat the paired panel. This tests whether rare-hand values depend
  materially on the injected weight.
- `fourbet-call/`: test the actual called 4-bet branch, where the pot is
  93.5bb and stacks are 155bb. AA already has material weight in that range.

`premium-branches.json` is a read-only audit of the saved 4-bet/jam subtree.
The opponent folds 40.93%, calls 41.07%, and jams 18.00% against the 4-bet.
The AA branch decomposition reproduces the saved 40.1196bb action value
within 0.0001bb. This establishes the right accounting; it does not validate
the continuation approximation. See the focused protocols for limitations.

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
python tools/research/wizard_continuation_floor.py pipeline
python tools/research/wizard_fourbet_continuation.py pipeline
python tools/research/wizard_continuation_report.py
```

The initial runner has a process lock and skips validated completed jobs. Do
not run two reference batches concurrently. Never rerun `prepare` over a frozen
manifest. Each job checks that production is idle; all solves are offline.
The runner emits local `status.json` and per-job logs. Raw references and input
hashes are retained. A failed quality check requires review, not silent deletion.
The two `pipeline` commands wait for their predecessors and then run serially;
do not start duplicate instances. The report command requires completed
precision results. Follow-up result files are written only when their full
registered panels finish.

The live app on 56708 and the completed baseline save are preserved. Jev is
deferred. The reserved Wizard 100bb cases remain unopened.
