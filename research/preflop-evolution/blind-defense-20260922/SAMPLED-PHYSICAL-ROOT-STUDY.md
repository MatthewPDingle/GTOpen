# First substantive fresh-deal evaluation: complete and audited

This plan was frozen while the physical BB/BTN pilot was still queued. It ran
after independent review of the pilot's one-hour budget stop and
all 78 completed iterations. The admission binds played generations 0 through
77, excludes unused generation 78 and interrupted iteration 79, and records
the checkpoint, models, review and terminal-source hashes before drawing deals.
It applies the [verified evaluation path](SAMPLED-PHYSICAL-ROOT-EVALUATION.md)
to that budget-limited bank. The [completed findings](SAMPLED-PHYSICAL-PILOT-FINDINGS.md)
show a profitable root deviation: +2.080 bb per entry, with the registered interval
from +0.080 to +4.080. The candidate is not ready for deployment.

The original CPU execution was too slow to finish within its budget. A separate
[persistent CUDA evaluation](SAMPLED-PHYSICAL-GPU-EVALUATION.md) passed fixed
numerical gates and completed the same candidate, deal streams and sample
plan. The CPU run was manually superseded after 1,392 training deals, before any
responder or test stream; its completed artifacts remain available. This is a
backend change, not an independent confirmation or an outcome-driven plan change.

## Policy selection and admission

Use the **last fully published iteration checkpoint**, with every played model
in its own-reach-weighted average. Exclude the newly fitted model that has not
yet played. Do not select an earlier checkpoint based on test performance.

Before running, independently review the pilot's terminal status, source hashes,
all completed iteration artifacts and the published checkpoint. Admit a normally
completed pilot, or a verified execution-budget stop with a valid completed
boundary. An unexplained worker error or other failure does not qualify. A
budget-limited candidate remains labeled as such; evaluating it does not turn
incomplete training into a completed or converged run.

The evaluation admission records that review, final checkpoint, full model bank,
and their hashes before the first new deal. The training controller must have
released its lock. Preparation does not automatically start another job.

## Fixed sample and comparison plan

- **8,192 training deals** to learn one root action per BB hand class.
- Require **16 training deals per class**; otherwise preserve the original
  mixed strategy for that class. No heuristic widening of unsupported hands.
- Freeze and hash this responder before instantiating the separate test stream.
- **16,384 test deals**, with paired complete-deal payoffs for five comparisons:
  trained responder, always fold, always call, always raise and always jam.
- One final statistical look, with a 5% family error budget across all five
  comparisons. No intermediate significance stop or outcome-based extension.
- Independent fixed seeds 49101 and 49102; 16 deals per batch. Retain full
  compatible private-card support, uniformly sampled remaining runouts, and
  every continuation branch in the existing research tree.

The analytic coverage calculation uses the frozen incoming ranges and card
compatibility, without drawing any deals. Expected training counts range from
**22.54 to 77.93** per class. The expected number of classes below 16 observations
is **2.06**, representing about **0.62% of test-deal mass** requiring fallback.
These are planning expectations, not guaranteed or observed coverage. Actual
fallback counts and mass must accompany the final result. They address the
tiny control's complete lack of usable learned-response coverage.

Intervals use the already checked bounded paired estimator and physical-chip
bounds from the stack and dead money, rather than observed sample extremes.
Positive lower bounds identify particular profitable deviations. Zero or
uncertain gains do not establish equilibrium, and none of these intervals
upper-bounds the gain of an unrestricted best response. Per-hand observations
can be diagnostic but cannot silently become additional confirmed comparisons.

## Resource and interruption behavior

The original execution used two CPU inference threads. Its replacement keeps the
model bank on CUDA, with two supporting CPU threads and a 3 GB free-VRAM reserve;
this is evaluation inference, not new model training or CPU performance work.
Stop after two hours, production activity, a reserve violation or an error.
Keep 20 GB host RAM and 40 GB SSD free; cap this evaluation's storage at 30 GB.
Only the evaluator's own worker and descendants can be stopped. There is no
automatic retry, continuation or budget extension. Partial outputs are retained
but are not a completed strength result or an authorized intermediate look.

The old incoming ranges, restricted betting menu and omission of earlier folded
cards remain limitations. This tests the trained BB first decision against its
frozen BTN opponent; it is not a general preflop model qualification or a
direct Wizard comparison. Production and the range preview stay unchanged.

Protocol: `sampled-physical-root-study-v1-registration.json`.
Planning calculation: `sampled-physical-root-study-v1-coverage-plan.json`.
Driver: `tools/research/hu_sampled_physical_root_study_20260922.py`.
Preparation and admission have completed. The invocation was
`--run --pilot-review PATH`, using the pilot's independent terminal review.
Original admission: `sampled-physical-root-study-v1-admission.json`.
Current GPU registration: `sampled-physical-root-study-gpu-v1-registration.json`.
The review is an agent-produced evidence artifact, not a request for user approval.
