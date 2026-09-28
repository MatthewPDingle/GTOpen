# Use available CPU resources for the unchanged error decomposition

The GPU diagnostic v1 did not start: two direct attempts and a bounded admission
helper encountered busy-resource readings before creating any registration,
data directory or result. The helper subsequently observed GPU utilization
94-100% during other applications' activity. It was deliberately terminated
before study admission; a temporary exclusive research lock prevented a start
during that handoff. Helper PID95360 / session28722 is terminal. Its source and
v1 diagnostic remain preserved. No scientific fit or evaluation was interrupted.

Diagnostic v2 keeps the exact candidates, original validation set, fixed fitting
subset, contexts, labels, action rules and metrics from the original plan.
Only execution changes: dense float32 inference uses NumPy on CPU with at most
four BLAS threads and no CUDA allocations. The approach has already independently
replayed the complete learning-budget test (185,966,592 decisions) within
7.97e-6bb in context means. The diagnostic must still reproduce its own original
GPU validation means within the unchanged 1e-4bb tolerance before interpretation.

Admit only with CPU utilization below50%, at least28GB available RAM, no active
production solve/other study, and40GB free S:. During execution retain24GB RAM,
stop for CPU utilization75% or more, preserve the1800-second and32MB limits,
and retain global allocated accounting plus32MB reserve. A busy GPU alone does
not block this CPU-only analysis. All evidence remains under a separate v2 name.

No new training, board generation, model selection, final-test labels or excluded
depths enter this run. Do not interpret the execution change as a new model or
production CPU performance improvement. This is efficient use of available
hardware while respecting the user's heavier foreground work.
