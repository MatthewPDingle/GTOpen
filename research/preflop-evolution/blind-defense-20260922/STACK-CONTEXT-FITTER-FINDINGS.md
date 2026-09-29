# Shared-context GPU fitter: implementation qualification passed

The new `stack_context_training_fit_v1.py` fits both player networks over the
complete context-weighted, stack-normalized objective. It accumulates the
gradient of every ordered chunk before each Adam update. Fitting starts from
a fresh seeded network and fresh optimizer each cycle, following the existing
continuation trainer's lifecycle. The extra public and relative input columns
start at zero; both input variants begin with the same predictions.

Four CPU tests passed in 1.787 seconds. They independently compare chunked
loss/gradients with a full-matrix expression, check model export against NumPy
inference, reject malformed objectives, and verify neutral initialization,
unchanged caller RNG and trainable new input columns.

The bounded GPU control ran once and exited0 in71.141 seconds. In all four
actor/representation cases, 256 Adam steps with ordinary execution and CUDA
graph replay produced exactly identical exported networks and recorded losses.
Float64 CPU/CUDA raw outputs and gradients, including fitted-network outputs,
met the fixed1e-10 tolerance. Three short repeated captured fits reproduced
the same network and reached a stable allocation plateau. Caller CPU/CUDA
random streams were unchanged.

The optimizer phase took5.75–9.00 seconds directly and0.579–0.844 seconds with
graph replay in these small fixtures. This is only the optimizer phase; it
does not predict end-to-end poker-training speed, which also includes native
simulation, conditional targets, input preparation and saving.

Peak CUDA reservation was163,577,856 bytes. Evidence used5,798,404 logical bytes
and4,443,755 allocated bytes. The process has exited and the research lock is
released. Do not rerun this completed control.

The independent readback passed: it rehashed registered inputs and outputs,
recomputed the saved raw-array differences and checked exact equality of the
exported networks. Scalar losses, allocator plateau and RNG preservation remain
recorded runtime evidence, not independently re-executed operations.

All targets here were synthetic, applied to retained native inputs at the five
fitting depths. This is not an accuracy comparison, a trained policy for users,
or proof of better preflop ranges. No new scientific comparison, production
change or GitHub push occurred. Evidence prefix: `stack-context-fitter-control-v1`.
