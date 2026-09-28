# Coverage study: next actions after the live jobs finish

Prepared at 2026-09-28 18:17 Adelaide. The main collector/pipeline are still
the recovered sessions listed in BOARD-RIVER-DEAL-COVERAGE-STATUS.md:
collector session 52256 / PID 85404; pipeline session 37598 / PID 27284.
Latest verified collection count at 18:15 was 889 / 1,344. Both sessions were
polled live. Do not start another collector or GPU owner.

Follow the handoff's main analysis first: require the complete recovery,
collection, readback, merged dataset, frozen-model, evaluation and report proofs;
run the pre-registered robustness analysis; review gates, subgroup/generalization
results, sensitivity and plot. Source bytes and sampling remain frozen.

## Independent CPU work completed during collection

`board_river_shared_preparation_profile_v1.py` completed (session 48159 exited 0).
The two frozen banks currently repeat identical CPU preparation. Preparing it
once passed byte-for-byte controls on ten old training cases, covering both
actors and every pot band. Wrong bank context was rejected, original query
objects unchanged. Separate/shared/shared/separate timings gave 1.93x CPU-stage
speedup and 0.401 s/case saved. This excludes GPU inference and bank-specific
tables. See BOARD-RIVER-SHARED-PREPARATION-FINDINGS.md and its JSON evidence.

The instrumented profile identified repeated deep copies and card-summary
construction as major CPU work. Instrumented seconds include profiler overhead;
use the uninstrumented counterbalanced timings for the stage comparison.

## Deferred GPU qualification - prepared, NOT executed

After BOTH main sessions are confirmed terminal, and their queued stages have
completed successfully/released the shared locks, run:

`python -B tools/research/board_river_shared_preparation_gpu_v1.py`

Use the documented Python312 executable and usual elevation/working directory.
The checker itself requires a successful main pipeline and idle shared locks.
Read BOARD-RIVER-SHARED-PREPARATION-GPU-PLAN.md first. No result or registration
exists yet. Do not mistake preparation of this checker for a passed GPU test.

The candidate helper's AST was checked equal to the CPU-qualified shared()
function. It does not import the CPU-only profiler module, whose environment
settings would hide CUDA. Each bank still separately validates context, prepares
its own tables/uploads and runs unchanged float64 inference/ordered averaging.

The GPU check uses only old inspected TRAINING cases. Require byte-identical
reference/candidate policy and own-reach arrays, agreement with archived outputs
and reconstructed labels, then a counterbalanced end-to-end timing benefit.
No precision, chunk size, model, target, dataset or reduction-order change.

This is an output-preserving runtime check and may be useful regardless of the
scientific learning result. It is distinct from estimator integration, which
still requires BOTH scientific gates and its separately derived sampling/
reach correctness controls. Neither result permits a production deployment.

If the GPU runtime check passes, document actual gain and consider reuse in a
newly registered future collector. Do not rewrite the completed live study's
registered sources. If it fails, preserve evidence and investigate without
loosening thresholds. No new learning study is launched from this note.

Keep the broader objective: better preflop ranges across positions, sizing and
stacks. Current river diagnostics and this efficiency improvement alone do not
prove that outcome. No deployment, broad GitHub push, archive deletion or Jev.
