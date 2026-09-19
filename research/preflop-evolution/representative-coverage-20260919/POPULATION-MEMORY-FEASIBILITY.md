# Capacity to train the combined 164-board mixture

CPU-only planning completed 20 September 2026 using the existing, hash-verified planner. The panel is the unchanged `combined-population-164.json`, with the same supported entering hands, 50% postflop bets, pot-sized raises, one raise per street, configured rake, and both called preflop pots. This is a capacity measurement, not a new solve, selection rule, or strategic result. No CUDA buffers or solver strategy arrays were allocated.

The planner constructed all 328 continuations and recorded both full and future-card-orbit plans for each. Weights do not change how many separate continuation states must be retained.

| Quantity | Decimal GB |
|---|---:|
| Full F32 regret and average-strategy arrays for all continuations | 123.184 |
| Future-card-orbit packed arena plan | 89.481 |
| Largest individual unprojected continuation buffer plan | 1.486 |
| Machine physical RAM | 137.357 |
| Physical RAM after the registered 20 GB free-host reserve | 117.357 |

**The current all-board host allocation cannot safely train this panel.** Its strategy arrays alone exceed the absolute physical-RAM-minus-reserve ceiling by 5.827 GB. Trees, metadata, temporary arrays, the operating system and production app require additional memory. A smaller individual GPU workspace does not solve this host-capacity problem.

The packed arena plan is 27.36% smaller, but current compact GPU code still retains full host arrays and has an unresolved changing-range equivalence test. The packed number therefore does not authorize a run or establish that a future implementation would fit after overhead. The pending own-average-upload optimization changes transfer bytes, not these host allocations.

One-board-at-a-time frozen-policy evaluation remains feasible because it does not retain the connected training state for every board. Turning the validation panel into a new training set would also consume it as development data and require a newly reserved accuracy check; this memory plan does not change its present scientific role.

Planning took 24.031 seconds on two CPU threads concurrently with the separate evaluation queue. Sampled peak resident memory was 0.201 GB; sampling can miss transient peaks. These timings are not solve-time or isolated performance benchmarks. The process exited 0, preserved its frozen input hashes, and produced all 656 expected plan rows. It stayed within the five-minute limit and 20 GB free-host reserve.

Evidence: `population164-memory-freeze.json`, `population164-memory-plan.json`, `population164-memory-status.json`, `population164-memory-plan.log`; runner: `tools/research/population_memory_plan_20260920.py`. Continue the registered evaluation unchanged and qualify storage separately before broader connected training.
