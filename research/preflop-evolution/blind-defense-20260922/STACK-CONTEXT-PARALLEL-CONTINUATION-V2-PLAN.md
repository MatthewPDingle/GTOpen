# Parallel continuation and diagnosed comparison correction

The user requested concurrent comparison runs on 30 September 2026, with light
desktop/video use allowed and heavier competing work taking priority. This is
an explicit continuation amendment to the existing four-arm registered study.
It is not a new trial or a restart of failed scientific collection.

The original serial runner failed after completing A-relative cycle two. Its
raw board-plan hash comparison included each representation's learned parent
state. Independent readback established that all 70 other input hashes and all
five actual board draws/configurations match. Every board plan also reconstructs
exactly from its own authentic parent. Preserve the original failure and all
original inputs. Do not change the frozen source files or registration.

## Permitted correction

Validate a complete board plan against its own authentic frozen model state,
then compare its chance fields across the matched representations. Keep all
original raw hashes; append separate immutable chance receipts. An actual
board, physical-deal, action-stream, configuration or generation difference
still fails. An unexpected partial cycle or new terminal failure cannot retry.

Recover only the diagnosed, complete A-relative cycle two checkpoint/metrics.
Restore and validate it, compare its chance receipt, archive its already-created
raw evidence and publish its completion marker. Do not repeat collection or
fitting. The compatibility check exercises this exact recovery path read-only,
with only archive/publication mocked, and forbids calling the scientific update.

## Parallel operation

Run one spawned process per arm (four maximum). Each owns its existing folder,
model/RNG/reservoir state and status file. Cycles within an arm remain sequential.
Each cycle uses the unchanged admitted pipeline, four target workers and one
board worker; archive packing retains its qualified four-thread implementation.
At most 20 target/board workers plus four coordinator processes run concurrently.
No new seeds, deals, fits, targets, model layers or evaluation budgets are chosen.
Original 64-cycle horizon, original 72-hour deadline and 12-hour complete-boundary
invocations remain. A peer failure signals the others to stop before their next
cycle, after finishing their current cycle. The supervisor holds ownership until
all children exit. No automatic retry or forced mid-cycle termination.

CUDA reservation is 2 GB per arm / 8 GB combined. Admission requires 40 GB RAM
and 12 GB VRAM available, original idle/production checks and a 70 GB transient
logical reservation within the unchanged 800 GB global allocated-file cap.
The supervisor owns the combined storage check. Per-arm production, RAM, disk,
CUDA and heavy-GPU guards remain. Higher sustained use from our own overlapping
GPU phases may cause conservative waits; do not weaken guards silently.

## Qualification and final interpretation

The one-shot v2 check must authenticate completed checkpoints and the diagnosed
recovery, reject damaged chance receipts, show unchanged old progress files,
and run four concurrent CUDA scorers using retained generation-one models and
the native physical preflop catalog. Compare each with the serial CPU complete
policy reference at 1e-10 tolerance and identical positive support. This tests
compatibility, not full-cycle speedup or new scientific accuracy. No model fit
or fresh scientific test deal is part of this check. Record the first actual
overlapping cycle timings before claiming a wall-time improvement.

The amendment binds this plan, runner, passed check, original registration,
original failure and diagnosis by SHA-256. Success has a new versioned training
result; the old failure remains present. Final-bank selection and evaluation
must explicitly understand this correction and preserve original fresh-test
gates. Never bypass an old failure by deleting it. All 64 cycles and matching
receipts must complete before the final eight-profile, 4096-deal/seven-depth
evaluation. No push, deployment, production change or broad-accuracy claim.
