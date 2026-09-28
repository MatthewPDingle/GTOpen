# Two-arm training throughput control v1

Implements the fixed comparison in TWO-ARM-TRAINING-THROUGHPUT-DESIGN.md.
Freeze this plan and all imported research sources before execution. Default CLI
mode checks source readiness without starting training or acquiring a lock.

Run a serial A-baseline update, then serial A-river, then both concurrently. Each
restores immutable boundary 78 and replays update 79 with the already qualified
preparation pipelines. Eight physical workers and four board workers per arm;
all seeds, 512 fit steps, batch identifiers, and original oracle checks preserved.

Every child completes source loading and CUDA setup before publishing ready.
The parent releases ready children together. Measure the same update function
externally with the process-shared Windows performance counter. Include the
initial update guard and final CUDA synchronization in every interval. Report
serial sum against concurrent makespan, call overlap, start skew, pipeline times,
GPU guard waits, resource snapshots, and whole invocation. Both concurrent updates
must finish before either child starts CPU-heavy verification. Do not label
observed guard waits as external-only: the other owned arm may cause them.

Require every result to equal its original archived checkpoint, restored state,
fitted networks/scales/numeric fit metrics, ordered reservoirs, source deal/action
streams and subbatch artifacts. No fresh learning or evaluation sample. One
descriptive timing pair, fixed serial-first order; caching, system load and
contention can affect timing. No accuracy or production latency claim.

One parent owns the existing research lock. New hidden children are assigned to
an unnamed Windows job before a permit allows workers or CUDA initialization.
Closing the job, including parent process termination, ends only its associated
process tree. Lifecycle control v2 verifies normal exit, descendant cleanup and
unrelated test-process survival. V1's count-of-two assertion failed because
Windows also created hidden console hosts; its failed evidence is preserved.
No production process is added to this job.

At most two coordinators, each capped at 2GB Torch CUDA allocation/reservation,
for a combined 4GB cap. Preserve existing GPU idle checks (under 65% utilization),
2GB external headroom, single-thread Torch/BLAS, production priority, minimum
24GB available RAM and 40GB free S: storage. Parent polls production and its own
children throughout waits. Child guard retains the qualified conservative GPU
sharing behavior. Record sampled whole-machine CPU/GPU and owned-process RSS;
sampled RSS sums are not guaranteed peak memory measurements.

Maximum invocation 60 minutes, each child 20 minutes including setup and readback.
Reserve 12GB new logical evidence plus 2GB follow-up against the 800GB global
allocated research cap, verified by fresh inventory at admission. Preserve all
completed and partial evidence. No automatic retry or overwrite. Re-inventory
at completion. Parent failures cancel/terminate only owned children; a hard
parent termination may leave a stale lock requiring identity-checked recovery.

Do not substitute this scheduler into scientific training until parity and
measured throughput pass review. No deployment, push, production UI or model
change. After this control, return to evaluation precision and stack/context
coverage rather than optimizing resource utilization for its own sake.
