# D021: direct-three-action compiler resources

Completed resource-only diagnostic on NVIDIA GeForce RTX 5090, `compute_120`, using one CUDA context and architecture-only/default NVRTC options identical to the original resource probe. **No kernels were launched, no solver was run, and no speed or numerical-correctness result is claimed.**

| Entry point | Registers/thread | Local bytes/thread | Static shared bytes | Blocks/SM at 128 threads | Warps/SM |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original dispatcher | 66 | 64 | 0 | 7 | 28 |
| Candidate dispatcher control | 66 | 64 | 0 | 7 | 28 |
| Direct `up_action_3` | 40 | 0 | 0 | 12 | 48 |

This is hypothesis evidence for a bounded direct3 candidate. The earlier direct2 resource improvement did not produce an accepted complete-cycle gain; resource counts alone do not establish benefit.

`baseline.cu` is the accepted E004 kernel source, SHA256 `8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0` (22,624 bytes). `candidate.cu` retains that complete prefix byte-for-byte, appending only a separate entry point. `direct3-wrapper.cu` contains the exact appended wrapper, with the original dispatcher signature, bounds guard, and original `up_action_impl<3>` argument list. No implementation math or compiler annotation changed. The baseline and candidate dispatcher PTX entries are also byte-identical; all PTX and extracted entries are preserved. Direct3 has 356 PTX entry lines versus the dispatcher's 2,407; line counts are not execution cost.

`probe.rs` derives from the copied E006 diagnostic and queries registers/local/shared memory and theoretical occupancy through the same cudarc APIs. `run.py` compiles it with standalone rustc against the existing cudarc/serde_json release dependencies; it never invokes Cargo. Before context creation it acquires the existing `gpu-run.lock`, performs the existing live-app status/refuse-active preflight, captures read-only telemetry, and sets the established NVRTC DLL path. The lock is released and the child has exited. No production source was written. CUDA source identity was checked again after execution.

Evidence: `report.json`, `manifest.json`, `commands.json`, `preflight.json`, `launch-preflight.json`, `probe.stdout.log`, `probe.stderr.log`, `baseline.ptx`, `candidate.ptx`, and three extracted PTX entry files. `artifact-index.json` seals all retained files, including the initial failed host link attempt.

The initial host link omitted thin LTO required by the cached release rlibs and failed before CUDA context creation. Its exact command/source/logs are retained under `attempt01-link-failed/`. The successful retry adds `-C lto=thin` to host compilation only; NVRTC options are unchanged. Reproduction command is `python run.py` in a fresh copy of this directory after removing only prior execution outputs in that fresh copy; the preserved directory refuses execution overwrite. Exact successful rustc and process commands are in `commands.json`.
