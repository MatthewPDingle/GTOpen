# Equal-budget coverage: live execution handoff

Snapshot: 2026-09-28 18:03 Adelaide. The broader research goal remains active.
This replaces the earlier 17:50 handoff; use these process identities.

## Live jobs - do not duplicate

- Collector recovery: unified exec session **52256**, Python PID **85404**,
  `board_river_deal_coverage_resume_v1.py`. It verifies the completed archives
  then resumes the unchanged registered v2 collector with only progress-file
  replacement made tolerant of transient Windows reader locks.
- Serial continuation: unified exec session **37598**, Python PID **27284**,
  `board_river_deal_coverage_pipeline_v2.py --collector-pid 85404`.
  It waits for the collector's successful recovery proof, then runs independent
  readback, old-training/new-data merge, 48 fixed fits, fresh evaluation and
  independent report publication.
- At this snapshot the collector had **311 / 1,344** new cases archived, and
  both live sessions were re-polled successfully. The resumed collection had
  loaded both banks and advanced from the 116 independently verified saved
  cases. The pipeline was waiting on that exact collector identity.

Current progress: `board-river-deal-coverage-v1-status.json` and
`board-river-deal-coverage-v1-pipeline-recovery-v1-status.json` in this directory.
Do not use the old pipeline-status file as a live signal. A status file or lock
alone is insufficient to prove liveness; poll the listed sessions or verify
the process identity. No duplicate collector or GPU owner.

Store: `S:/GTOpen-research/board-river-deal-coverage-v1`. Current per-stage logs
will be in `pipeline-recovery-v1/`. Cases are retained as ZIPs plus hash
manifests. Original training data is reused read-only by identity.

## Recovery evidence

Sessions **32008** (collector) and **83018** (pipeline) are terminal, exit 1.
The collector encountered Windows access denied replacing mutable progress;
the pipeline correctly did not proceed without a completed collection.
The former had published 114 progress cases; queued archive writers completed
two more, and all **116** were independently verified before resumption.

Commit **53d673bb** preserves versioned recovery sources, failed-run evidence
and passing controls using real Windows read handles. Permanent locks defer
only progress updates and retain the flushed temporary file. Disk-full,
serialization, flush, unrelated IO errors and durable marker failures remain
fatal. Scientific source, original registration, labels and settings are
unchanged. See BOARD-RIVER-DEAL-COVERAGE-PROGRESS-RECOVERY.md.

The original v1 archive-fixture failure was separate: its old-store ownership
guard safely rejected the new path. That evidence remains preserved; the v2
collector's new-store archive controls passed before any labels were collected.
See BOARD-RIVER-DEAL-COVERAGE-ARCHIVE-CORRECTION.md.

## Frozen scientific comparison

Read BOARD-RIVER-DEAL-COVERAGE-PLAN.md. Compare 1,152 rows from 64 versus 192
distinct deals, matching actor/pot strata, with exact and sample16 targets in
both sets. Two banks, two actors and three paired seeds give 48 fits, each
exactly 512 steps. Freeze them all before scoring 576 states from 32 fresh
final deals. Original final cases are excluded and board/key groups separated.

New collection is 768 broad-training plus 576 evaluation cases. Dense reuses
all 1,152 old TRAINING rows; broad reuses 384 of them. New collection has a
2 GB store cap; first-eight admission estimated 1.23 GB conservatively.

No live experiment settings may be edited. Sources and registrations are
immutable. Version corrections separately, preserve failure evidence and
never select data/settings from final outcomes.

## Required next steps after the queued pipeline finishes

1. Confirm terminal exit codes and all stage proofs, including the recovery
   result, collection completion and independent report readback.
2. Run the already registered supplemental CPU analysis:
   `python -B tools/research/board_river_deal_coverage_robustness_v1.py --mode analyze`.
   It reports deal-level and leave-one-deal-out sensitivity. Its plan and
   hand-calculated controls were registered before final scoring. It changes
   no advancement gate or training setting.
3. Review separate coverage and target gates, bank/actor/pot results,
   training-versus-final errors, support counts and sensitivity. View the
   generated plot. Retain failures and mixed results without changing gates.
4. Commit exact completed evidence and verify committed bytes. Update this
   handoff to terminal status only when authoritative process evidence says so.
5. If BOTH gates pass, consider the separately controlled estimator integration
   described in BOARD-RIVER-TARGET-INTEGRATION-NOTES.md. Otherwise choose a
   development-only representation/regularization test or justified alternative.
   No tuning on the spent final set or silent data extension.

The supplemental script expects all 32 final deals to have supported states
for each model. If not, preserve its explicit failure and report unsupported
coverage instead of altering exclusions. The main scientific gate already
requires equal effective actor/pot counts across training sets.

## Prior findings and broad scope

BOARD-RIVER-TARGET-LEARNING-FINDINGS.md: exact targets improved aggregate
prediction/cost but failed the predeclared bank-A comparison with sample16.
BOARD-RIVER-GENERALIZATION-CURVE-FINDINGS.md: 8-to-48-deal training-only coverage
reduced development MSE 25.2% and local decision cost 33.1%; overfitting remained.
These motivated the current fixed-budget test, not a production promotion.

The 302 features have context-specific history and cards, not explicit
cross-depth numeric stack inputs. STACK-CONTEXT-PLAN.md remains required for
flexible modeling. Earlier numeric public-state features failed their separate
noisy-target validation gate; this does not qualify transfer to other stacks.
No result here yet establishes full-policy EV or improved preflop ranges.

Prior completed sessions 20848, 23365 and 67158 exited 0. Earlier evidence is
committed in a54222d2, 9eac3a18 and 2d41d1f2. No new GitHub push or deployment.

Keep one research GPU owner, 4 GB CUDA cap, 2 GB external headroom, 24 GB free
system RAM, 2 GB new study storage and 800 GB global allocated archive cap.
Light desktop/video sharing is authorized; production solves and heavier work
take priority. No production changes, historical deletion, Jev or new windows.
