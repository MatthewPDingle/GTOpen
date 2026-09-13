# R01: qualify memory-aware selection before production integration

Keep the public/default GPU constructor and port 56708 unchanged. Add a research
entry point for eventual rollout qualification, returning the selected mode and
the reason for fallback. This is not another measured speed improvement.

Try the retained C01+C07+C09 combination with an optional cohort memory limit
derived from current CUDA free memory, minus 512 MiB, and the caller's configured
budget. Keep the existing 20,500 MB cohort ceiling and 256 MiB planning reserve.
Crucially, use the original configured budget to select the baseline particle
batch and heads-up cache; the smaller cohort limit must not change that plan.
Do not accept all-singleton sharing plans merely to say optimization is enabled.

If free-memory probing fails, the optimized plan does not fit, or optimized
construction fails, let its owned allocations drop and construct the normal GPU
engine with the original budget. Report the actual fallback reason. Do not
continue with partially initialized storage. If normal construction also fails,
return both errors. Existing server CPU handling stays outside this research path.

Qualify pure budget/error selection, high-memory success, low-memory and failed
probe fallback, unsupported multiway contexts, frozen/locked seats, captured
iterations/checks and stop. Compare complete arenas and root results bit for bit
to the default solver. Then use immutable small and large saved fixtures for
load, continue, save and reload checks. Never mutate the user's sessions.

Full native GPU and default solver regressions remain required before promotion.
The extra planning path needs complete-work timing before claiming that it
preserves the measured gain. No server integration, deployment, or completion of
the broader convergence goal is implied by these preparatory checks.

All GPU/build/test commands use run07 serial ownership and port56708 idle guards.
Use immutable output IDs, cap initial build/tests at 300 seconds, and wait on the
same process after an observation timeout. Do not edit source during workloads.
