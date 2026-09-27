# Comparing the complete board-root models

The final comparison now has a dedicated four-bank assembly module,
`tools/research/board_complete_evaluation_support_v1.py`. This is preparation,
not a completed model comparison or evidence of better ranges.

The policy order is fixed before any new evaluation results:

| Slot | Policy |
| --- | --- |
| 0 | First seed, existing stratified model |
| 1 | First seed, board-root candidate |
| 2 | Replication seed, existing stratified model |
| 3 | Replication seed, board-root candidate |

This order matches the existing crossed-policy evaluator. Each BB strategy is
compared against its corresponding control against both BTN strategies, and
each BTN strategy against both BB strategies: all eight predefined contrasts.
The prospective plan remains unchanged: 65,536 fresh deals, seed 9281101, one
final look, simultaneous 95% intervals, and all 169 root hand classes.

The loader requires complete independently audited training. It selects played
generations 0–77, weights them 1–78 with each player's own action reach, and
excludes unplayed generation 78. Board-root policies use their explicit root
table in both the CPU reference and GPU bank. Their configurations must match
the fixed seed-specific treatment. Historical control settings cannot change.

The CPU-only preparation control passed in 0.625 seconds. It checked the actual
prospective configuration and pending-input gate, then used synthetic bank
objects to test ordering, reference routing and 15 invalid cases. It did not
load the complete candidate models, initialize CUDA, draw new test deals, or
test prediction accuracy. Evidence:

- `board-complete-evaluation-support-control-v1-registration.json`
- `board-complete-evaluation-support-control-v1-result.json`

Still required, in order:

1. Complete the currently running historical-model evaluation and its queued
   independent review.
2. Finish the queued genuine board-training/restart and typed-bank controls,
   actual-budget two-generation prefix, and independent prefix audit.
3. Measure full-study storage requirements, admit the complete budget, train
   both candidates to 78 generations, and independently read back all results.
4. Qualify the actual four complete banks against CPU reference predictions on
   previously used control deals, including own-action histories and native
   transport. The existing two-model check cannot establish this equivalence.
5. Run and independently review the fresh fixed evaluation, with fresh storage
   and resource admission. No production deployment follows automatically.

The new module does not schedule or launch those stages. Existing jobs, frozen
registrations, production port 56708, and the original scientific plan remain
unchanged.

## Prepared full-history numerical check

`board_complete_evaluation_control_v1.py` now implements the next numerical
control, followed by `board_complete_control_readback_v1.py`. Both default to
read-only readiness; explicit execution is refused while their prerequisite
training or control results are missing. These rejection paths and syntax
checks passed; see `board-complete-control-preparation-v1.json`.

The actual control remains unrun. It will reuse an already-inspected 64-deal
batch, compare all four complete GPU banks against their CPU references at
the 265 catalog observations and all batch observations, including action
histories, then preserve the crossed profiles and native values for readback.
The subsequent CPU reader checks model identities, the generation chain,
actor routing, cashflows and all statistical reductions. It shares the existing
poker engine and inference implementations; it is not an independent solver.
Admission requires an idle GPU, available CPU/RAM and a fresh inventory under
the global storage ceiling. Its output cap is 256 MB, with a two-hour limit.
Neither script draws fresh test deals or changes the fixed study plan.

## Prepared fixed evaluation and restart recovery

`board_complete_evaluation_study_v1.py` implements the full fixed comparison,
with `board_complete_study_readback_v1.py` for the final CPU review. Both default
to read-only readiness and require explicit execution after all prerequisites.
The output identity is `weighted-complete-board-root-study-v1`; its directory
name permits direct reuse of the qualified archive and checkpoint helpers.

The final runner preserves the registered 65,536-deal endpoint and seed 9281101.
It can stop at an operational batch boundary and resume the identical committed
chance sequence and statistical accumulator. Incomplete attempt files remain
preserved and excluded. Progress distinguishes evaluated deals from deals whose
archives and recovery checkpoint are committed. Every invocation rechecks global
storage admission; the original 800 GB ceiling and reserve remain in force.

An isolated integration test replayed 64 old deals across two invocations. Actual
CPU archive workers, checkpoint publication and restoration ran; final statistics
matched the uninterrupted reference exactly. It also rejected an over-budget
launch before creating the study directory or sampling. GPU inference and
scientific qualification were replaced with old-outcome fixtures in this test;
it does not validate candidate predictions. The live training lock was unchanged.
This took 20.532 seconds. Evidence:

- `weighted-complete-board-driver-control-v1-integration-proof.json`
- `board-complete-study-preparation-v1.json`

The actual candidate evaluation has not started. The final CPU reader will
reconstruct the registered chance stream and check every archived batch across
all restart attempts using eight workers. Full training, its audit, the genuine
complete-bank numerical control and its readback are still prerequisites.
