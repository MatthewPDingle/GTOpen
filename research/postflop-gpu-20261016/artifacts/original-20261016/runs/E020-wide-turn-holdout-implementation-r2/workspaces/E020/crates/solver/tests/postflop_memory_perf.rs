//! Fixed cold/warm F32/compressed GPU lifecycle and host-memory measurements.
#![cfg(all(feature = "gpu", target_os = "windows"))]
use cudarc::driver::CudaContext;
use solver::{gpu::GpuSolver, store::Storage, Solver, Spot, SpotConfig};
use std::{sync::Arc, time::Instant};

// Same ABI as Windows PROCESS_MEMORY_COUNTERS_EX. Read-only process counters.
#[repr(C)]
#[derive(Default)]
struct MemoryCounters {
    cb: u32, faults: u32, peak_working: usize, working: usize,
    peak_paged: usize, paged: usize, peak_nonpaged: usize, nonpaged: usize,
    pagefile: usize, peak_pagefile: usize, private: usize,
}
#[link(name = "kernel32")]
unsafe extern "system" { fn GetCurrentProcess() -> *mut std::ffi::c_void; }
#[link(name = "psapi")]
unsafe extern "system" {
    fn GetProcessMemoryInfo(process: *mut std::ffi::c_void, counters: *mut MemoryCounters, size: u32) -> i32;
}
fn memory() -> MemoryCounters {
    let mut c = MemoryCounters::default();
    c.cb = std::mem::size_of::<MemoryCounters>() as u32;
    assert_ne!(unsafe { GetProcessMemoryInfo(GetCurrentProcess(), &mut c, std::mem::size_of::<MemoryCounters>() as u32) },0);
    c
}
fn median(mut v: Vec<f64>) -> f64 { v.sort_by(f64::total_cmp); v[v.len()/2] }

#[test]
#[ignore = "manual postflop GPU lifecycle memory and transfer benchmark"]
fn postflop_memory() {
    let mut cfg: SpotConfig=serde_json::from_str(include_str!("../../../bench_spot.json")).unwrap();
    cfg.board="Ks7s2d".into(); cfg.tree.rake_pct=0.05; cfg.tree.rake_cap=3.0;
    let spot=Arc::new(Spot::new(cfg).unwrap());
    let ctx=CudaContext::new(0).unwrap();
    for storage in [Storage::F32,Storage::Compressed] {
        for warm in [false,true] {
            let mut s=Solver::with_storage(spot.clone(),storage);
            if warm {
                let mut gpu=GpuSolver::new(&s).unwrap();
                for _ in 0..20 { gpu.iterate().unwrap(); }
                gpu.sync_to_cpu(&mut s).unwrap();
                s.ensure_symmetric();
                drop(gpu);
            }
            let prefix=format!("postflop.memory.{}.{}",if warm {"warm"}else{"cold"},if storage==Storage::F32 {"f32"}else{"compressed"});
            let mut init=Vec::new(); let mut sync=Vec::new(); let mut strategy_sync=Vec::new();
            let mut resident=Vec::new(); let mut private=Vec::new(); let mut vram=Vec::new();
            let mut checks=Vec::new();
            for _ in 0..3 {
                ctx.synchronize().unwrap();
                let free=ctx.mem_get_info().unwrap().0;
                let start=Instant::now();
                let mut gpu=GpuSolver::new(&s).unwrap();
                gpu.synchronize().unwrap();
                init.push(start.elapsed().as_secs_f64()*1000.0);
                vram.push(free.saturating_sub(ctx.mem_get_info().unwrap().0) as f64/1e6);
                for _ in 0..5 {gpu.iterate().unwrap();}
                gpu.synchronize().unwrap();
                let start=Instant::now();gpu.sync_to_cpu(&mut s).unwrap();
                sync.push(start.elapsed().as_secs_f64()*1000.0);
                let start=Instant::now();gpu.sync_strategy(&mut s).unwrap();
                strategy_sync.push(start.elapsed().as_secs_f64()*1000.0);
                let m=memory();resident.push(m.working as f64/1e6);private.push(m.private as f64/1e6);
                checks.push(serde_json::json!({"iteration":s.iteration,"exploit_bits":gpu.exploitability(&s).unwrap().to_bits()}));
                drop(gpu);
            }
            println!("METRIC_JSON {}",serde_json::json!({"metrics":{
                format!("{prefix}.init_ms"):median(init),format!("{prefix}.sync_ms"):median(sync),
                format!("{prefix}.strategy_sync_ms"):median(strategy_sync),
                format!("{prefix}.host_live_mb"):median(resident),
                format!("{prefix}.host_private_mb"):median(private),
                format!("{prefix}.allocated_vram_mb"):median(vram)
            },"storage":format!("{storage:?}"),"warm":warm,"memory_checks":checks}));
        }
    }
}
