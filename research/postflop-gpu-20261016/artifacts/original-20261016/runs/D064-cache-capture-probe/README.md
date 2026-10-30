# D064 captured policy metadata probe

Prepared only; root must authorize the single execution after independent review. Run the command in `protocol.json` through the existing root lock/live-idle/reserve/timeout wrapper. No additional runner is introduced.

One 128-byte policy window is set on an owned 256-byte allocation. The only integer-copy launch is guarded by an immediately preceding ACTIVE capture query. Capture ends, the graph is immediately instantiated with cudarc's flag1, then the retained kernel-node policy is compared to the exact stream readback. No graph replay or eager kernel execution is available. Cleanup disables the policy and releases every owned object, recording each result.

The allocation is never initialized because its contents are never accessed. Module loading may invoke the driver's PTX JIT during authorized execution. There is no NVRTC call. Any unsupported API, alignment/readback mismatch, error or cleanup failure is a terminal failed attempt, with no variant or retry.

The [CUDA12.9 stream API](https://docs.nvidia.com/cuda/archive/12.9.1/cuda-driver-api/group__CUDA__STREAM.html) specifies capture recording and subsequent-work attributes. The [node getter](https://docs.nvidia.com/cuda/archive/12.9.1/cuda-driver-api/group__CUDA__GRAPH.html) exposes retained graph metadata; the [window definition](https://docs.nvidia.com/cuda/archive/12.9.1/cuda-driver-api/structCUaccessPolicyWindow__v1.html) permits driver alignment, which this fixed probe treats as a recorded mismatch. Installed cudarc bindings provide the versioned ABI pins in `api-pins.json`.

A pass establishes only this synthetic retained-node attribute result after capture/instantiation. It establishes no solver-graph, replay, physical-cache, numerical or speed result.
