# Possible next preflop experiments

These are **speculative, unrun follow-ups**, not retained changes or a new research commitment. The completed pass remains frozen. Do not change samples, precision, betting menus or accuracy targets to obtain a gain.

## 1. Publish an early strategy preview independently of accuracy checks

**Evidence:** The [real API pair](api-first-strategy-eight-a.json) first served strategy at 269.42 seconds in the optimized version, almost immediately after its default 50-iteration checkpoint at 269.39 seconds. The [fresh-game controls](fresh-eight-comparisons.json) separately measure the earlier 10-iteration checkpoint. This identifies publication cadence as a responsiveness question distinct from iteration throughput; it does not prove how cheaply an early preview can be produced.

**Hypothesis:** Publish a consistent strategy snapshot after the first complete iteration, explicitly marked provisional, while retaining the existing accuracy-check schedule. This could shorten the blank-grid interval without performing an expensive early best-response check. Measure snapshot transfer, CPU synchronization and API/render overhead before deciding whether a full snapshot or bounded node preview is preferable.

**Workload and metrics:** Repeat the frozen fresh eight-seat real-server scenario and a modeled six-seat scenario. Measure solve acknowledgementâ†’first usable strategy separately from median iteration time, time to the unchanged accuracy target, transfer bytes and peak memory. Preserve polling intervals rather than reporting false timestamp precision.

**Correctness gate:** Exact complete arenas and checkpoint trajectories at equal iterations; no learning updates caused by viewing; no partial-iteration snapshot, stale-player-model response or spurious convergence label. Verify stop/resume, frozen/locked policies and node navigation against an independently produced snapshot. Reject a responsiveness gain that materially harms the measured solve trajectory without a deliberate product tradeoff.

## 2. Reuse identical opponent-equity work within one frozen accuracy check

**Evidence:** [Static key instrumentation](raw/key-stats-eight.log) found 243,716 duplicate tasks among 2,362,251 live tasks across traversers (10.3%), but **zero duplicates within a traverser**. This supports investigating cross-seat reuse only during a frozen average-strategy check. Earlier [eager phase measurements](phase-eight-summary.json) attributed about 5.09 seconds per check to coupled terminals; they are diagnostic timings from an earlier retained stage, not final graph-runtime measurements.

**Hypothesis:** Cache only repeated ordered-opponent equity sums during that one check, applying each terminal's own probability, pot and investment afterward. Preserve original particle-batch boundaries and arithmetic order. Start with a storage/launch-cost model; caching every duplicate at every batch can consume gigabytes and may outweigh the avoided work.

**Workload and metrics:** Use frozen eight-seat and modeled six-seat checks. Measure complete accuracy-check latency, added storage, launch overhead and end-to-end target time. Include sparse and zero-reach states; static duplicates alone do not establish runtime savings.

**Correctness gate:** Exact per-terminal outputs and complete native arenas at the preserved literal batch/cache choice, including zero own/folded/live-opponent reach and repeated checks after learning changes. Invalidate reuse between learning sweeps. Reject if storage changes numerical grouping or if complete-check time does not improve.

The rejected grouped-opponent kernels and shared CDF staging are not proposed again: their lower resource counts did not improve throughput. [Recorded rejections](findings.md).
