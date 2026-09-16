# Accuracy and runtime night shift

User objective: pursue better preflop accuracy while approximately maintaining
performance, for ten hours. Start **2026-09-16 10:49:02 UTC**; stop launching new
experiments at **2026-09-16 20:49:02 UTC** (17 September, 06:19 Adelaide).
Finish or safely checkpoint the current bounded job, validate and publish the
measured result. The goal is active throughout this window; one completed
experiment is not completion of the night shift.

## Operational constraints

- Preserve port 56708 and its sessions. No application POSTs, deployment,
  restart or replacement of the live executable.
- One research GPU workload at a time. Verify live process command lines,
  including orphaned reference children, before resuming. A stale status file
  or an observation timeout does not prove a process stopped.
- Defer GPU research when a live solve/report is active. Resume checkpoints
  without weakening numerical precision, convergence thresholds or poker trees.
- Original datasets, frozen candidates and completed studies stay immutable.
  New experiments use separate directories and record exact provenance.
- Keep the unrelated `compatibility-batch/patch-check` directory untouched.
- Push bounded, verified research changes and results to GitHub. No automatic
  promotion to production, even when an offline screen passes.

## Research sequence

1. **N01: targeted data.** Finish the already-running
   [260-reference refinement](../policy-refinement-20260916/README.md). Its fixed
   protocol predates outcomes. Fit the same predictor with two additional
   development ranges, then evaluate on fresh boards from other source families.
   Publish the result regardless of whether it improves accuracy.
2. **N02: compact predictor revision.** Use only training families to compare
   the existing feature set, its smaller base encoder, and a limited hand-strength
   curvature extension. Fixed ridge candidates: 0.03, 0.1, 0.3. Keep all related
   cases in the same family fold, including the two new development ranges.
   Select by equal-source-family held-out training error; report worst-family
   changes as well as the mean. A preliminary original-24-case comparison is
   diagnostic only. The final fit uses 26 cases after N01 development completes.
   Freeze before fresh evaluation. Never select using N01 evaluation results.
   Require at least 5% lower family-CV mean than the shape/0.1 control and no
   more than 5% worse error in any training family before paying for a new
   prospective evaluation. Retain failures as evidence, not silent tuning.
3. **N03: range coverage.** The [range-bridge experiment](../range-bridges-20260916/README.md)
   is now prospectively specified: 36 synthetic contexts interpolate between
   concentrated and broad training-source ranges at three SPRs. Its 720 training
   references and 400 reserved evaluation references preserve source-family and
   board separation. The controller is deadline-bound and refuses overlap with
   the currently running reference controller. Final N02 selection found no
   eligible candidate, so this data expansion is the next accuracy experiment.
4. **N04: runtime.** For candidates that pass accuracy checks, eliminate repeated
   compatible-mass and prediction work, preserve the exact legal-pair action-value
   oracle and benchmark repeated matched workloads. Compare with both ordinary
   Balanced and the unoptimized identical predictor. Aim for no more than 10%
   median iteration-time overhead versus ordinary Balanced, with memory and
   end-to-end fixed-work timings reported. This is an operational interpretation
   of "approximately maintaining performance", not permission to trade away
   correctness. Report tradeoffs rather than disguising a miss.
   An [opt-in scheduling prototype](../interface-work-reuse-20260916/README.md)
   now removes ordinary terminal values that the interface overwrites, plus
   unused ordinary equity-cache work. It builds and passes CPU regressions,
   independent GPU oracle checks and GPU regressions. Timings remain queued
   behind reference generation.
   Preparing and testing this exact-work removal does not qualify the old
   predictor for deployment. It uses an isolated executable and leaves defaults
   unchanged. The timing comparison
   checks every saved regret and accumulated strategy entry for exact equality.
5. **Decision and robustness follow-up.** If accuracy and runtime support proceeding,
   test new-policy ranges, representative full preflop configurations and
   longer iteration checkpoints. Range-conditioned frozen-value BR gaps are
   diagnostics, not certificates of full-game exploitability. Wider calls or
   more mixed hands alone are not proof of better strategy.

## Additional fixed training diagnostics

- **N05, [projected fitting](../projected-fit-20260916/RESULTS.md):** rejected;
  accounting-aware feature fitting worsened held-out training-family error.
- **N06, [small nonlinear residual](../nonlinear-residual-20260916/RESULTS.md):**
  the best mean improved 6.77%, but its worst-family error ratio of 1.050442
  missed the fixed 1.05 gate. No threshold rounding and no candidate promotion.
- **N06b, [expanded-data repeat](../nonlinear-expanded-20260916/README.md):**
  repeat the unchanged choices after N03 training completes. It must beat both
  the same-data and original-data controls, using only the original 26
  validation cases and whole-family exclusion.
- **N07, [rank-event controls](../rank-controls-20260916/RESULTS.md):** exact
  feature moments passed enumeration, but 6–21% historical dispersion reduction
  missed the all-family 20% gate. Reference labels remain unchanged. See the
  separate [sampling precision diagnostic](label-precision.md).
- **N08, [precision-weighted training](../precision-weighted-20260916/README.md):**
  after N03 training completes, test fixed square-root and linear board-count
  case weights. Same inference cost; no new evaluation labels for selection.

N06b and N08 are CPU screens. Finish CPU training before timing the GPU.
Each surviving model still requires a separately frozen fresh-board evaluation;
N03's reserved outcomes must not become a second model-selection set. A
[shared prospective evaluation](../expanded-validation-20260916/README.md)
now reserves another 50 disjoint flops per held-out context. Both training
screens must finish and all eligible candidates must be registered before any
of its 400 references are generated. If neither qualifies, skip that workload.

Choose later bounded experiments from evidence and remaining time. Do not keep
spending the night on a rejected model merely because it is already implemented.
New targets, datasets or model families require a prospective specification and
new evaluation protection; do not retune against already inspected test labels.

## Evidence required for the final report

`continuation_night_queue.py 39132` sequences the existing plans after the live
N03 controller. It verifies that controller's actual process identity, waits for
all training references, runs N06b/N08 sequentially on CPU, then waits for N03
to finish before reporting, timing N04 and registering any eligible fresh-board
models. It never starts another N03 controller. Its GPU children enforce the
live-app guard and single-workload rule. All stages respect the fixed deadline.
Inspect `queue-status.json` and the controller/child processes before starting
anything manually; a waiting queue is still active work. Queue completion is
not goal completion: review, reporting, pushing and combined-model checks remain.

State what improved, what failed and what remains uncertain. Include input and
candidate hashes, training/evaluation separation, reference quality, conditional
value error and uncertainty, independent action-value/accounting checks, repeated
runtime measurements when applicable, and production status. Show accuracy and
runtime separately. An offline value-error gain does not establish a faster or
more accurate full preflop equilibrium. If no version clears both gates, say so
and keep the live app unchanged.

The protocol and N02 implementation are [recorded in the ledger](ledger.json).
