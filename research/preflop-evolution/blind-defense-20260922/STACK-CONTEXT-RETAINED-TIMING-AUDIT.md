# Where the early training cycles spent their time

The six already-completed cycles spent **98.1%** of their recorded pipeline time collecting targets. The recorded GPU optimizer accounted for **0.53%**. This supports prioritizing concurrent target preparation over further optimizer-kernel work. It does not yet establish the parallel speedup.

| Run | Cycle | Pipeline | Collection | Optimizer |
|---|---:|---:|---:|---:|
| A-baseline | 1 | 479.9s | 471.8s | 1.99s |
| A-baseline | 2 | 483.2s | 473.8s | 2.62s |
| A-relative | 1 | 458.0s | 450.4s | 2.47s |
| B-baseline | 1 | 378.7s | 372.6s | 1.64s |
| B-relative | 1 | 479.7s | 471.4s | 2.24s |
| A-relative | 2 | 542.9s | 527.8s | 3.98s |

In the complete but not-yet-published A-relative cycle 2, river target construction occupied **95.6% of summed worker elapsed time**. The four-worker pools had approximately 2.6–3.0 overlapping worker intervals on average per context. That measure includes worker waits and I/O; it is not measured CPU utilization. Board work already overlapped river work.

Even the impossible case of eliminating every recorded optimizer second would improve this early pipeline by only **1.005×**. Running four independent arms together can instead overlap their CPU-heavy preparation. Actual gains must come from completed-cycle throughput and resource telemetry, including any contention or sibling-GPU waits.

These are early-cycle observations. Reservoir growth can change later timings. Collection includes inference, native work, serialization, I/O and resource waits. Pipeline timers exclude the outer archiving/publication stage, so they do not give end-to-end run duration. GPU optimizer time is not the same as total GPU use.

All five published cycles and the complete unpublished A-relative cycle 2 were included; no result-dependent timing selection was made. Archived metric bytes and raw worker reports were authenticated against their recorded identities. No new hands, fits, benchmarks or production changes were performed.

Machine-readable inputs, formulas, details and limitations: `stack-context-retained-timing-audit-v1.json`.
