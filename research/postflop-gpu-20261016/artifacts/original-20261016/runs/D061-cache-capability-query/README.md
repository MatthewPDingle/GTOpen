# D061 getter-only capability query (unexecuted)

One isolated 64-bit Python child reads device 0 identity, driver version, compute capability, L2 size, maximum persisting-L2 capacity, maximum access-policy window and the child context current persisting-L2 limit. `query.py` is not imported or run during preparation.

The root owns the existing ar lock/live-idle/51 GiB reserve/60-second timeout wrapper and separate execution authorization; the exact command and requirements are in `protocol.json`. The wrapper captures the single `D061_CAPABILITY` JSON line, stderr and exit without a retry. All CUDA return codes remain explicit. Unsupported values are null, with their code, and produce exit 2; successful zero is distinct.

Only retaining, binding, restoring and releasing the child process primary context are permitted lifecycle operations. All context symbols are resolved before retain; both cleanup calls are attempted even on errors. This cannot inspect the live server context. Driver internal initialization is not claimed to be free of resource effects. No application streams/events/modules/device buffers/copies, kernels or solver calls are made.

`api-pins.json` binds installed cudarc 0.19.7 signatures/enums to official CUDA 12.9.1 documentation. The UUID buffer preserves all 16 bytes including zero. No cache policy, window or performance conclusion is selected by this query.

Validation before sealing: Python AST only, getter allowlist and fixed enums checked from source; no script import, DLL load, native query, compilation or GPU execution.
