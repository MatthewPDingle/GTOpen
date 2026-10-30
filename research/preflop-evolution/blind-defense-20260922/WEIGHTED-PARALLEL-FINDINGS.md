# Weighted training CPU pipeline: equivalent and faster

The generation-two reference took 51.45 seconds in the serial weighted pilot.
The bounded CPU pipeline reproduced its checkpoint, learned model, all native
artifact hashes, retained rows/weights, RNG states and fit diagnostics exactly.
Sampling, GPU inference, real reservoir insertion and final reductions retain
their original order; CPU workers complete independent frozen-policy batches.

| Worker limit | Workers that handled tasks | Total generation | CPU pipeline wall time |
|---|---:|---:|---:|
| 1 | 1 | 37.78 s | 34.44 s |
| 2 | 2 | 21.84 s | 20.78 s |
| 4 | 3 | 20.64 s | 19.47 s |
| 4, repeat | 3 | 22.58 s | 19.13 s |

An earlier two-worker development smoke took 23.47 seconds and also reproduced
the serial result exactly. These measurements establish roughly a 2.2–2.5x
end-to-end speedup for this particular generation, not an order-of-magnitude gain
or faster strategic convergence. The one-worker version can overlap coordinator
work with a worker, so it is already a pipeline rather than the old serial loop.

The repeat ran in a new coordinator process after the reporting issue below. Its
filesystem caches were warm, but its first optimizer setup was cold: fitting took
2.75 seconds versus 0.51 in the preceding four-worker run. It is therefore not a
pure fully-warm repeat. Startup/shutdown, serialization and compression remain in
the reported total times; no time was subtracted to manufacture a speedup.

## Why the original controller stopped

The original registered controller finished runs one, two and three, and all its
numerical/artifact comparisons passed. It then asserted that every worker allowed
by the pool limit must have processed a task. Only three of four did, because the
coordinator did not supply enough concurrent work to require the fourth.

The original source and registration remain unchanged and have no success result.
A separately registered completion run revalidated the three completed states
and their native files, corrected the reporting rule to one through the configured
maximum task-executing workers, then performed the planned repeat. Queue bounds,
numerical equivalence and checkpoint checks were unchanged. The authoritative
success record is `weighted-parallel-completion-v1-result.json`, with its ordinary
and recovery registration files; it is not a retroactive pass for the first runner.

## Resources and next use

The queue never exceeded twice the worker limit. Each task-executing worker used
about 119–122 MiB at its largest sampled RSS. Pools were shut down and joined;
no worker remains running. Registered benchmark evidence plus the completion run
occupies approximately 1.20GB logical / 490MB allocated file bytes at measurement;
the separate development smoke adds about 302MB logical / 202MB allocated. New
directories inherited NTFS compression. No old evidence was recompressed/deleted,
no production service was changed, and no concurrent GPU fitting was introduced.

Two workers capture most of the benefit and are a sensible default when the
computer has other work. A four-worker ceiling offers a modest pipeline gain when
resources are free. More workers alone are unlikely to help much: coordinator
inference still takes about nine seconds. Resource availability must be checked
again for subsequent runs rather than inferred from this benchmark.

Before the accuracy study, qualify full-length weighted CUDA fitting: this pilot
used eight steps per fit while the established study setting uses 512. Retain the
complete weighting and validation checks. The longer baseline-versus-stratified
comparison and independent poker evaluation are still outstanding.
