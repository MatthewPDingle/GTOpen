# D08: bounded hardware profiling of retained C09

After C12's instruction simplification tied complete performance, obtain
hardware evidence before another kernel rewrite. This is diagnostic, not a
candidate speed measurement. C09 remains unchanged.

Fetch only the portable Nsight Compute component of NVIDIA's CUDA13.1.1
redistribution manifest. Pin version2025.4.1.2 and verify published SHA256 and
size; extract inside LAB/target/research-tools with zip path containment checks.
Do not install a driver/service, edit PATH globally, enable profiling permissions
or use elevation. Record manifest, hashes, version and extraction path.
https://developer.download.nvidia.com/compute/cuda/redist/redistrib_13.1.1.json

First use ncu --version/help and a bounded single-kernel counter smoke against
an already qualified frozen test executable. If counter access fails, preserve
the error and investigate non-counter diagnostics; do not change driver security
settings. No repeated identical denied attempts.

If available, profile one probability-construction and one terminal-evaluation
launch from the retained C09 frozen benchmark, on the large immutable save.
Start with basic throughput/launch statistics; collect memory/scheduler/warp
stall sections only if the initial observation is valid and supports the next
question. Limit launch selection and report exact kernel/grid/block/invocation
scope. Preserve default math, particles and all solver results. Use clock-control
none and cache-control none; no driver clock adjustment or explicit cache flush.
Replay affects timing and cache behavior; never compare profiled wall time to
ordinary benchmark wall time or add a GPU progress-graph speed point.
https://docs.nvidia.com/nsight-compute/ProfilingGuide/

Use run07 ownership/idle guards, serially, with immutable input/source/executable
hashes and output IDs. Initial smoke cap120s; large diagnostic cap240s. If
profiling completes the benchmark, verify checkpoints and arena fingerprint
against C09. If it cannot complete within the cap, state that qualification is
incomplete and keep partial profiler data diagnostic only. No source changes
during workloads; port56708 stays read-only and no deployment occurs.

Counter smoke returned ERR_NVGPUCTRPERM and its test exited cleanly. Do not
retry the denied counter request. Next, download only the published nvdisasm
component and use cuLinkCreate/AddData/Complete to produce diagnostic cubins
from the archived C09/C12 PTX, without launching kernels. Disassemble these
driver-linked binaries and record static instructions/resources. Linking treats
PTX as relocatable input and is not proof of the exact binary emitted by the
earlier cuModuleLoadData path. State that limitation explicitly; static counts
are not execution counts, stall counters or speed results. Guarded cap120s.
