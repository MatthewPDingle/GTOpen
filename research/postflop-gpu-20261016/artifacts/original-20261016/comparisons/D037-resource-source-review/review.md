# D037 no-launch resource probe source review

PASS_SOURCE_ONLY. No actionable source/provenance defect remains in the frozen probe, runner and protocol. This permits root-owned execution of this diagnostic only; it does not establish compiled success, resource feasibility, numerical equivalence or speed. No build, GPU operation or production edit was performed by this reviewer.

Prepared manifest783bce1a84f29c90ef77175e9028898247e9ee4b7f9c8ec76da99c28e6eadf63; protocolb01e259bec2381fa36f505044e1a80edf3d4761499ff1ef6f469bd86364c34a7; probe7afba5dacb96db6ee860966dfd6e13f1e033e8a06aee4e7be5e0c4e46b891d08; runner1fa7b65d9205095292f68850ec51e20a13836745b343bd55e1f2f64ba0449fe3. All sealed artifacts, both rlibs and protected accepted-source hashes independently verify. CUDA and host copies match the separately reviewed two-file candidate.

## API and no-launch scope

The Rust program creates one context, compiles two complete modules under architecture-only production defaults, loads up_show, queries device/function attributes and theoretical occupancy, saves PTX, then drops function/module references and checks recorded drop errors. It contains no launch/graph/stream, memory-copy, or explicit device-buffer allocation path. Module/context loading consumes driver resources but is not a solver or kernel execution. Output/I/O/driver errors panic to a nonzero process exit and are retained; there is no optional std::error::Error conversion assumption.

Installed cudarc0.19.7 source confirms shared_size_bytes, num_regs, local_size_bytes, max_threads_per_block and CudaContext::attribute return Result<i32,DriverError>; ctx.check_err returns Result<(),DriverError>. Thus static_shared+dynamic_shared as i32 is type-consistent. The declared largest dynamic size26520 is safely representable. occupancy_max_active_blocks_per_multiprocessor accepts(u32,usize,Option<CUoccupancy_flags_enum>) and returns Result<u32,DriverError>;128,dynamic as usize,None matches it. All four queried device attribute enum variants exist in the cuda12050/cuda12060 selected binding block. unwrap requires Debug, which is unconditional; it avoids the D036R2 Error-trait issue. These are source checks, not a compilation claim.

## Fixed resources and limits

The14 rows cover two sources times seven shapes: two observed rainbow launch allocations; two final-river allocations derived from frozen233/280 hands and game.rs eval_board(&[]) retaining every hand; full1326 conservative capacity; empty/single synthetic counts. Sizes independently recompute. Two-tone actual occupancy is explicitly unqueried, and derived/synthetic cases are not presented as native measurements. No shared opt-in attribute is changed.

The runner records fits/default limits and occupancy rather than automatically accepting them. Root's post-run resource authorization must check nonzero occupancy, support for128 threads, static+dynamic default shared fit, code generation and any register/local/shared changes. A completed diagnostic with a false fit field is not a resource pass. The theoretical rows do not establish launch success, latency, DRAM savings or complete-cycle improvement.

The accompanying eight-case host-only invariant check covers0/1/2/31/257/319/1326 and trailing-empty lists at nonzero global offsets. Flattened metadata has exactly2*m_o entries; all relative lookups preserve integer values; the128-lane copy covers each entry once; the four regions are contiguous/disjoint/aligned. This small algebra check is not a new solver/GPU harness or numerical oracle.

## Runner custody

Execution requires --execute and unique execution-started/output files. Sealed source/rlib/protected-checkout hashes are checked outside/inside the GPU lock, after rustc and after the probe. Both stages use fixed600-second bounds and file-backed output; the50GiB reserve includes an additional1GiB output reservation. Live-session preflight is GET-only and telemetry is before/after the probe. All owned child cleanup on timeout, interrupt or heartbeat/status failure occurs before lock release. Heartbeat failure may invalidate this one-shot diagnostic but cannot release a live child; failures remain preserved rather than overwritten/retried.

Expected ordered markers are one device row,14 source/shape rows and one complete row. Source FNV/length, dimensions, dynamic sizes and zero-launch labels are cross-checked; full/entry PTX and other-entry equality remain inspectable. Other-entry equality is reported, so the independent runtime review must assess it before authorization. Root must observe native and wrapper terminal success. No performance or numerical claim follows from host process duration.

