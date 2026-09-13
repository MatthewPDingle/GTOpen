# C11 registered protocol: terminal L1-cache preference, using retained C09

Stop increasing unroll factors: C10's median large gain was only 1.47%.
The actual C09 alias-aware terminal kernels use 54 registers, zero local memory
and 84 bytes of static shared memory. Their emitted code uses read-only global
loads for the CDF data. A small, independent next experiment can ask the driver
to favor L1 cache for those terminal functions, without changing PTX or arithmetic.

Use the existing cudarc `CudaFunction::set_function_cache_config` with
`CU_FUNC_CACHE_PREFER_L1`, only for C01's exact terminal and C07's cohort terminal.
Set it once on a fresh C09 research instance before any graph capture or launch.
Keep the production constructor, CDF producer, group planner, allocations,
1,024 samples, register limits, unroll factor and math unchanged. Do not also
set a shared-memory carveout attribute or context-wide preference: one mechanism.
Require successful API results and preserve normal error propagation.

NVIDIA describes this as a preference, not proof of actual cache allocation;
the driver may choose otherwise. Switching preferences between kernel launches
can also cause synchronization. Complete-work timing must include those effects.
Source: [CUDA Driver API, cuFuncSetCacheConfig](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__EXEC.html).
Do not claim that a successful API call proves more L1 cache or a hit-rate gain.

Before implementation register a protocol. Validate original/C01/C07/C09/
candidate full solver/terminal/prefix bits, zero recovery, locked/frozen seats,
batches 5/32 and capture/replay. Prove unchanged source PTX and global allocations;
record requested configuration and loaded function resources outside timing.
Then run the same frozen six-sweep first large pair, rejecting ratio >=0.99;
passing screens require three alternating pairs per fixture, >=3% median large
gain, <=3% median small regression and required GPU/default correctness suites.
Use run07 guards and immutable provenance. No CPU performance, concurrent GPU
work or source edits during timing; no writes/restarts/deployment on port 56708.

This has not been implemented or measured. If there is no repeatable gain,
remove it rather than stack more cache hints. The broader speed/convergence
objective remains open.

Registered before C11 implementation: five expanded cohort tests (original/C01/C07/C09/C11), four C01 reuse tests, unchanged helper parity test, one actual-function/PTX/cache-request diagnostic, unchanged small/large global layout audits, then six-sweep first large pair. Reject complete ratio >=0.99; passing screens run three alternating pairs per fixture, median large <=0.97 and all large pairs improve, small median <=1.03, 19 native GPU and 181 default correctness regressions. API success proves only that the preference was accepted. Freeze and hash the binary and sources; archive rejected source.
