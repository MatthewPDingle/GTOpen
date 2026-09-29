# Prepared numerical diagnostic — not started

29 September 2026. The preceding balanced-board study remains failed on its
accuracy gates and incomplete on independent numerical verification. This is a
separate explanation of one preserved failure, not a retry or a new accuracy
claim. No training, fresh labels, model selection or tolerance changes occur.

## Question

Why did the saved GPU result and CPU reconstruction disagree by one classified
decision on each of two boards? A tiny score change could cross the 50% call
boundary. Another possibility is the rule for two nonpositive action scores:
the larger score wins outright, and an exact tie chooses fold. The synthetic
controls demonstrate both possibilities, but neither is established as the
cause of the observed failure.

## Fixed inputs and scope

- Seed 9297101, random-board training, 362 inputs, selected update 8192.
- The original 40bb public context: all 70 decision situations.
- Test boards 51 and 101, with all 1,081 legal holdings each.
- Saved checkpoint, board features, hand identities, equity counts and public
  states; no new sampling or poker evaluation labels.
- 404 input file identities recorded in
  `stack-board-boundary-diagnostic-v1-registration.json`.
- The original study result and failed verifier are read-only inputs. The
  original successful readback result must remain absent.

The two boards were selected because they failed verification. Results from
them cannot estimate population accuracy or replace the fresh-test comparison.

## Preserve the calculation being diagnosed

The original GPU evaluation used batches of 8,192 rows. Evaluate only the 160
original batches intersecting the target boards, keeping every row in each
batch, both actor networks and the final action selection unchanged. This is
1,310,720 GPU input rows instead of 9,685,760 for the whole context.

The original CPU reconstruction used all 138,368 holdings together for each
public state. Preserve those full matrix dimensions, then retain the target
holdings. This means 9,685,760 CPU input rows, with one BLAS thread as before.
Using smaller CPU matrices or changing thread count could change the floating
point arithmetic being investigated. This short diagnostic therefore cannot
use all CPU cores without compromising its purpose.

Check that the assembled CPU and GPU feature values agree exactly. Save the
raw CPU/GPU scores and call probabilities for every target decision, together
with the board, hand and public-state identities, call advantage, monetary loss
and classification differences. The compact JSON may summarize at most 2,048
disagreement rows; the array artifact retains all target rows without truncation.

Compare reconstructed error counts with the original counts exactly. If they
do not reproduce, report that as nonreproduction; do not rerun until they do.
Even exact counts do not prove every original raw prediction is identical,
because the historical evaluation did not retain raw scores. Any explanation
must distinguish reproduced aggregate counts from newly observed raw values.

## Limits and isolation

- One invocation, no automatic retry, exclusive attempt marker and research lock.
- At most 600 seconds after admission, including resource checks and waiting.
- At most 4 GB CUDA allocation and 2 GB external VRAM headroom.
- At most 32 MB of new raw evidence; no copied training archives.
- Admit only while production is idle and resources are available. Yield to
  active solves or heavy workloads by terminating and preserving evidence.
- Production on 56708 is never changed. No GitHub push or deployment.
- The original failed verifier is not called, modified, or replaced.

## Preparation verification

Seven preparation controls passed: exhaustive chunk geometry against a tiny oracle;
complete target coverage at the original dimensions; rejection of invalid
targets; probability conversion against the original pure function at ties,
zeros and adjacent float values; a classification flip with tiny monetary
impact; a nonpositive-score order flip with a large probability change; and
exact registration equality after JSON serialization.

The first preparation check caught a tuple/list mismatch in the diagnostic's
batch manifest after writing JSON. The rejected registration and its source
are preserved separately. The diagnostic was never admitted or invoked. The
manifest now uses JSON-native lists; this development fix changes no scientific
input, model, batch interval or tolerance in the original study.

The prepare command verified the 404 recorded file identities and published
the registration without importing CUDA or running scientific inference.
It did not create the diagnostic store or attempt marker.

## Entry point, after authorization to run the follow-up

`C:\Program Files\Python312\python.exe -B T:\Dev\GTOpen\tools\research\stack_board_boundary_diagnostic_v1.py run`

Outputs use the `stack-board-boundary-diagnostic-v1` prefix in this research
folder. Raw arrays would go under
`S:\GTOpen-research\stack-board-boundary-diagnostic-v1`.

This plan is prepared only. The monitoring instruction explicitly prohibited
launching another scientific experiment after the comparison. Obtain approval
for this distinct diagnostic before invoking `run`; routine preparation and
synthetic checks are complete. No broader learning experiment is proposed here.
