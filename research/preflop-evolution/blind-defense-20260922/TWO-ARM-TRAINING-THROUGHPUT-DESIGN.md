# Next throughput experiment: two independent training arms

Design stage only. No runner is implemented or new benchmark running at this
checkpoint. The complete preparation control has finished and released its lock.

## Question

Can two independent training arms use otherwise idle CPU resources to finish a
research comparison sooner, while preserving the exact learning trajectory?
This concerns throughput across experiments, not the latency of a production
preflop solve or a change to poker strategy.

The completed preparation control reproduced every archived result. Its optimized
baseline update took 49.625 seconds and river update 171.250 seconds. River work
remains CPU dominated, with eight physical workers and four board workers. The
recorded physical-worker RSS sum was approximately 3.3 GB. The user's 5950X,
128 GB RAM and 24 GB GPU justify a bounded two-arm test; do not assume a speedup.

## Fixed comparison to implement and freeze before execution

Use A-baseline and A-river from the existing immutable completed-78 sources.
Replay update 79 with the already qualified preparation pipelines, eight physical
workers and four board workers per arm. Preserve all seeds, model identities,
action streams, fitting settings, checkpoint semantics and oracle comparisons.
No new training trajectory or evaluation stream is introduced.

Run one fresh serial pair and one concurrent pair. Four cases in total. Use
separate child processes and output directories so module globals, Torch state,
RNG state, reservoirs and progress files cannot cross-contaminate arms. Children
must never acquire or replace the parent research lock. Launch hidden/piped.

Finish each child's setup before its timed release. For the concurrent pair,
release both from a readiness barrier. Use the same externally measured update
call interval for serial and concurrent cases; report serial sum and concurrent
makespan, individual pipeline timers, release skew and total invocation time.
Do not compare a whole concurrent invocation with serial pipeline-only timers.
Retain all timings even if concurrency is slower.

Every case must match its original archived oracle, not merely its paired run.
Require exact checkpoints, fitted networks/scales/non-timing metrics, ordered
reservoirs, source deals, action streams, target artifacts, full restored state
and model-bank membership. This is one pair in one context, not universal parity
or an accuracy qualification.

## Resource and recovery requirements

- A single coordinator owns the existing research lock and an explicit registry
  of child PIDs and creation times. Default mode must only check readiness.
- Admit only when production is idle, external GPU activity is light, and fresh
  CPU/RAM/VRAM/storage checks pass. Active production solves retain priority.
- Allow at most two arm coordinators, each with eight physical and four board
  workers; limit BLAS/Torch CPU threading as in the qualified runtime.
- Cap each coordinator's CUDA allocations at 2 GB, for at most 4 GB across the
  pair, and retain the 2 GB external headroom requirement. Record peaks per child.
  Do not silently relax the established heavy-work guard to improve a benchmark.
- Existing utilization guards may conservatively wait on another owned child.
  Report that limitation and wait counters; do not call all recorded wait time
  external contention. Add a GPU lease only as a separately specified change if
  measured interference justifies it.
- Start with 12 GB logical evidence allowance plus 2 GB follow-up reserve within
  the global 800 GB allocated cap; re-inventory first. Preserve all old artifacts.
- Bound the invocation to 60 minutes and child work to a documented limit.
  Cancellation must preserve finished cases and partial evidence. A parent failure
  must not leave untracked GPU children running. Verify child identity before any
  cleanup action; never affect production or unrelated processes.
- No automatic retry, overwrite, deployment, new push or public UI changes.

## What follows

If equivalence passes and measured makespan improves materially, use this bounded
scheduler in a future prospectively frozen quality study. If it is slower or
unreliable, retain the serial scheduler. Avoid further standalone repetitions
without a specific unresolved issue.

This test does not resolve the uncertainty in the 16,384-deal quality comparison.
Before another expensive learning run, prepare a more precise prospective
evaluation, preserving the old findings. Broader stack/public-state inputs remain
required under STACK-CONTEXT-PLAN.md. Neither task should be replaced by hardware
utilization as an end in itself.
