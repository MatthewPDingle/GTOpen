# Research pipeline hardware use, 25 September 2026

The user observed low resource use on the Ryzen 5950X / 128 GB / RTX 3090
machine. Live inspection confirms substantial unused capacity. This concerns
the experimental training and validation pipeline, not production solver speed.

## Observed audit behavior

During the action-integrated replication audit, PID 43712 consumed 4.9375 CPU
seconds over a five-second wall-clock sample: approximately one CPU core. Its
resident memory was 0.993 GB; available host memory was 109.764 GB. Two GPU
snapshots showed 7-8% overall utilization and approximately 1.98-1.99 GiB used.
These are short observations, not an integrated GPU utilization trace.

The audit source explicitly sets OpenBLAS, OpenMP and Torch to one thread and
disables CUDA. The sequence launcher requests two CPU threads, but the audit
overrides it. The earlier user-facing statement of two audit threads was
corrected. A first PowerShell process-object delta returned zero and was not
used; the CPU figure above uses two explicit psutil CPU-time snapshots.

## Completed replication training timings

Source: `action-integrated-replication-v1-result.json`, SHA-256
`89ecbe362966aca54f842e31004e4ce6525f7ed962e2161dc30bb1d5f4e13af0`,
and all 78 immutable `iteration-XXXX/metrics.json` files in its recorded store.

| Recorded phase | Seconds | Minutes |
| --- | ---: | ---: |
| Total worker execution | 12647.859 | 210.798 |
| Both players' fit setup, summed | 2989.964 | 49.833 |
| Both players' CUDA optimizer phases, summed | 4180.307 | 69.672 |
| Native integrated-root evaluation, summed | 776.776 | 12.946 |
| Unattributed remainder | 4700.812 | 78.347 |

The remainder is subtraction, not a profile proving an I/O bottleneck. It
includes traversal, inference, ingestion, serialization, hashing, checkpointing
and other overhead. The CUDA optimizer phase includes Python dispatch and
checks; its duration is not proof of continuous GPU saturation. No speedup
factor has been measured yet.

The last update's prepared tensor payloads were approximately 304 MB and 150 MB
for the two players. Network fitting uses a small 302/64/64/4 network and 4096-row
chunks; these observations justify profiling batch/dispatch overhead, not
automatically changing the numerical training protocol.

## Follow-up after the frozen comparison

Finish the registered audit and all endpoint/range comparisons unchanged.
Then profile a bounded, saved-data workload without resampling or fitting a
new scientific candidate. Separate preparation, native traversal, inference,
GPU fitting, checkpoint serialization and audit reconstruction costs.

Candidate optimizations, selected only after measurement:

- Parallelize independent per-batch checks and preparation across CPU workers;
  preserve deterministic ordering of reservoir and accumulated-regret updates.
- Cache immutable parsed data in RAM and reduce redundant serialization and
  reads. Retain authenticated evidence and storage/resource guards.
- Batch GPU work and reduce dispatch overhead; preserve the declared loss,
  gradient accumulation and seeded behavior, or explicitly version and test
  any numerical change rather than silently changing a matched experiment.

Use a new version and compare against saved outputs before adopting changes.
Do not edit registered source bytes, replace the active audit, reduce its checks,
run a competing GPU job, or modify production 56708. More occupied memory by
itself is not a performance result; measure end-to-end elapsed time and output
agreement. This work supports faster research toward accurate ranges and does
not replace the outstanding call/raise accuracy and broader-scenario studies.
