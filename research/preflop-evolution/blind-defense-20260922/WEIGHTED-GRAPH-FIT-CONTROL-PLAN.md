# Weighted CUDA graph fit control

The full accuracy study uses 512 optimizer steps, whereas the integration pilot
used eight. Avoid introducing a launch-overhead regression by checking the same
captured ordered-gradient method previously used by the unweighted fitter.

Use both actual final reservoirs from the weighted trainer pilot (BB capacity
8192, BTN 4009 retained visits). For each, fit the same fresh seeded network with
the ordinary weighted objective and with a captured ordered gradient, 512 Adam
steps, chunk size 2048 and learning rate 0.003. Adam remains outside the capture;
captured gradient buffers must be reset on every replay. No weighting, target,
feature, precision or optimizer change is allowed.

Require exactly identical exported network bytes and all fit diagnostics except
timing/runtime fields. Report complete fit time including grouping, setup and
capture, optimizer time separately, and peak allocated device memory. Check both
multi-chunk reservoir cases, not just a single small synthetic tensor. A
development run may precede registration; only the fixed registered run is
published as the control result.

Use the normal application-idle/closed and exclusive research-lock checks, GPU
below 20% and at least 4GB free before admission, 20GB host RAM headroom, and a
300-second limit. Write metadata only; reuse immutable existing reservoir files.
No production changes or claim of stronger poker ranges. Passing qualifies the
fit runtime; complete parallel-trainer integration must still reproduce a saved
serial checkpoint before a longer study uses it.
