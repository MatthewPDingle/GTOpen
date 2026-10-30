# D032: obtain captured-graph kernel timings

Recommendation: one **Nsight Systems CUDA node-level trace of the preserved accepted E015 binary**, filtered to the rainbow fixture, after a compatible Windows tool installation and an authorized elevated execution context are available. This directly answers which kernels dominate the graph execution now used in normal solves. It requires no evaluator or production source change. This is a proposed diagnostic only; nothing was profiled, built, installed or executed on the GPU during this audit.

## Local inventory and prerequisite

Read-only PATH, uninstall-registry and usual installation/tool-root scans found no nsys, ncu, nvprof, CUPTI or NVPerf binary. The scan is bounded, not a full-drive proof of absence. Registry reports NVIDIA driver610.88; nvcuda.dll file version is32.0.16.1088; the repo supplies NVRTC12.9.86 through its pip-wheel directory rather than a detected CUDA Toolkit. Preserved D029/D031 evidence identifies the RTX5090, compute120. This was not re-queried with a GPU API. Current process token is **not elevated**.

NVIDIA documents local Windows CLI collection and requires the Windows Nsight Systems CLI to run as administrator. Disabling CPU sampling does not waive that stated prerequisite. No privilege change or workaround was attempted. Tool version is therefore **not installed/verified**, not zero or assumed current. Before capture, pin the Windows Workstation release, its executable/CUPTI hashes and supported driver range against610.88; no driver upgrade is part of this design. Version-specific archive pages redirected to a site unavailable to the web tool, so this audit does not claim a particular downloaded release is compatible. [NVIDIA CLI guide](https://docs.nvidia.com/nsight-systems/UserGuide/index.html#installing-the-cli-on-your-target), [installation requirements](https://docs.nvidia.com/nsight-systems/InstallationGuide/index.html).

## Why this instead of the current eager profile

Accepted E015 mod.rs:403-446 runs an eager first iteration, captures two fixed player sweeps, then launches those graphs; evaluation has separate captured graphs. `iterate_profiled` instead performs eager launches and synchronizes after every launch. D029's profile is useful for hypotheses but includes host dispatch/synchronization costs and cannot establish the kernel duration distribution of graph replay.

Nsight Systems can report each captured graph as one activity or trace individual nodes. Node tracing is necessary for kernel attribution and can add substantial overhead. Current supported releases may use Blackwell hardware tracing; record the actual method and fallbacks from the Diagnostics Summary rather than assuming HES is active. [CUDA graph tracing and trace methods](https://docs.nvidia.com/nsight-systems/UserGuide/index.html#cuda-graph-trace).

## One bounded capture

`proposed-command.json` contains a non-executed argv/environment template. Use the immutable E015-postflop_autoresearch.exe, SHA25637e09be0b3d2ec66db6b49e13e09aa468a487218bd0215306f025bf7ca226eda, whose build manifest and frozen evaluator identity were verified. Use the usual NVRTC PATH and RAYON_NUM_THREADS=16; set fixture=rainbow, storage=compressed, PROFILE=0. PROFILE=1 would append the distorted eager diagnostic and confuse attribution. CLI collection requests only CUDA, node-level graphs, no CPU samples/context-switch trace, a unique non-overwriting output directory and the existing exact ignored test. Do not attach to the live server.

Root should reserve a new diagnostic ID, hold the same exclusive GPU lock and inspect the same read-only live preflight used by the existing runner. No parallel build, GPU or profiling jobs. Launch the unchanged binary to normal completion so final exactness output is retained; avoid duration-limited collection that terminates its child. Any bounded watchdog must explicitly clean up both child/profiler, preserve partial output and label it invalid rather than report timings. Do not promote profiler-reported complete-cycle fields into qualification results.

Capture tool/version/help, executable and bundled-library hashes, driver/NVRTC identity, argv/environment/cwd, baseline binary/build-manifest/source/evaluator identities, start/end timestamps, read-only preflight, stdout/stderr/exit/test-count and native profiler artifacts. Preserve the nsys-rep, optional SQLite export, exact extraction SQL/schema version, CSVs and all checksums. Never replace D029 or an existing closed report.

Validity requires actual CUDA graph-node activities, completed test, no missing/invalid-duration records or diagnostic buffer losses, and unchanged configuration, target, iteration, exploit bits and state fingerprint against the preserved E015 result. Profiler-induced timing changes are expected, so these are diagnostic durations only.

Analyze the report offline. Inspect SQLite schema before writing queries. Classify training graph IDs by their up_action nodes; evaluation graphs use up_action_eval. Exclude graphId0 eager/JIT work and evaluation graphs when ranking training replay. Preserve separate p0/p1 graphs, identify their order from graph launches, and report kernel name/grid, count, total GPU duration, median/p90 and per-graph intervals. Keep eager startup, evaluation, memory transfers, CPU API gaps and readback as separate diagnostic groups. Do not infer a level solely from a repeated grid size. The resulting ranking is specific to the traced run and is not a native time-share or end-to-end speed claim.

## Alternatives considered

| Option | What it measures | Decision |
|---|---|---|
| Nsight Systems node tracing | Device intervals for actual captured kernel nodes plus CPU/graph context | First choice; install/elevation prerequisites remain. |
| Nsight Compute | Selected-kernel hardware counters and deeper bottleneck evidence | Follow only after Systems identifies a kernel. Replay can save/restore memory, purge caches and change scheduling/clocks; expensive for large mutable CFR arenas. Not a throughput benchmark. |
| Custom CUPTI activity collector | Per-node kernel activities with graphId/graphNodeId | Technically suitable, but needs a supported library plus collector/buffer/correlation integration. More implementation and validation than the packaged tracer. |
| CUDA events | Stream/device elapsed time between event records | Useful fallback for whole captured sweep/batch timing, not per-kernel attribution without changing graph instrumentation. Requires a separately built diagnostic, not frozen-primary edits. |

Nsight Compute's replay and reproducibility behavior is documented in its [Profiling Guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html). CUPTI documents per-node graph identifiers and HES in [CUDA Graphs tracing](https://docs.nvidia.com/cupti/main/main.html#cuda-graphs). CUDA events measure elapsed device time between recorded events; completion handling is required ([driver API](https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__EVENT.html)).

The installed cudarc0.19.7 source exposes `new_event`, `record`, and `elapsed_ms`; `new_event(None)` explicitly disables timing, so any future event diagnostic must request timing-enabled flags. Record events outside capture around whole launches and resolve them only after completion. Inserting events between every node would change the graph and is not a transparent replacement for a graph-node trace. Its Profiler wrapper merely starts/stops an attached profiler; it is not a collector by itself.

No performance conclusion follows from this design. It identifies the most useful missing evidence and the exact operational prerequisites; root remains responsible for whether and when to provision or execute it.
