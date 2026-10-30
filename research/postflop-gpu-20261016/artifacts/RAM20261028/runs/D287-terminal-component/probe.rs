#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="gpu/mod.rs"]mod observed;
use cudarc::driver::{CudaSlice,CudaStream,DeviceRepr,DevicePtr};
use std::{fs::{File,OpenOptions},io::BufWriter,path::Path};
// Complete postflop CUDA lifecycle benchmark for the 2026-10-16 research pass.
// Freeze this evaluator and bench_spot.json before recording the first baseline.
// Run with --ignored --nocapture --test-threads=1. Every progress line is flushed.
// POSTFLOP_AUTORESEARCH_FIXTURE=rainbow|two-tone|river selects a smoke test only.
// POSTFLOP_AUTORESEARCH_STORAGE=f32 selects secondary coverage (default compressed).
// POSTFLOP_AUTORESEARCH_PROFILE=1 adds one diagnostic iteration AFTER scoring.
// No saved games or historical research artifacts are read or written.

use serde_json::{json, Value};
use observed::{GpuSolver, KERNEL_NAMES};
use solver::store::{Storage, Store};
use solver::{Algorithm, Solver, Spot, SpotConfig};
use std::io::{self, Write};
use std::sync::Arc;
use std::time::Instant;

const TARGET_PCT_POT: f64 = 0.3;
const CHECK_EVERY: u32 = 20;
const MAX_ITERATIONS: u32 = 400;
const FIXTURES: [(&str, &str, f64); 3] = [
    ("rainbow", "Ks7h2d", 0.0),
    ("two-tone", "Ks7s2d", 0.05),
    ("river", "Ks7h2dQhTc", 0.05),
];

fn emit_stage(value: Value) {
    println!("AUTORESEARCH_STAGE {value}");
    io::stdout().flush().expect("flush benchmark progress");
}

fn emit_result(value: Value) {
    println!("AUTORESEARCH_RESULT {value}");
    io::stdout().flush().expect("flush benchmark progress");
}

fn elapsed_ms(start: Instant) -> f64 {
    start.elapsed().as_secs_f64() * 1000.0
}

// Stream every byte without allocating a second copy of the multi-GB arenas.
// This is a deterministic equality fingerprint, not a cryptographic digest.
struct Fingerprint(u64);
impl Fingerprint {
    fn new() -> Self {
        Self(0xcbf29ce484222325)
    }

    fn bytes(&mut self, bytes: &[u8]) {
        for &byte in bytes {
            self.0 = (self.0 ^ u64::from(byte)).wrapping_mul(0x100000001b3);
        }
    }

    fn finish(&self) -> String {
        format!("{:016x}", self.0)
    }
}

fn fingerprint_store(store: &Store, combined: &mut Fingerprint) -> Value {
    let mut hash = Fingerprint::new();
    let mut feed = |bytes: &[u8]| {
        hash.bytes(bytes);
        combined.bytes(bytes);
    };
    let (kind, entries, scales) = match store {
        Store::F32(values) => {
            feed(b"f32");
            feed(&(values.len() as u64).to_le_bytes());
            for value in values.as_slice() {
                feed(&value.to_bits().to_le_bytes());
            }
            ("f32", values.len(), 0)
        }
        Store::I16 { q, scale } => {
            feed(b"i16");
            feed(&(q.len() as u64).to_le_bytes());
            feed(&(scale.len() as u64).to_le_bytes());
            for value in q.as_slice() {
                feed(&value.to_le_bytes());
            }
            for value in scale.as_slice() {
                feed(&value.to_bits().to_le_bytes());
            }
            ("i16", q.len(), scale.len())
        }
        Store::U16 { q, scale } => {
            feed(b"u16");
            feed(&(q.len() as u64).to_le_bytes());
            feed(&(scale.len() as u64).to_le_bytes());
            for value in q.as_slice() {
                feed(&value.to_le_bytes());
            }
            for value in scale.as_slice() {
                feed(&value.to_bits().to_le_bytes());
            }
            ("u16", q.len(), scale.len())
        }
    };
    json!({
        "kind": kind, "entries": entries, "scale_entries": scales,
        "bytes": store.bytes(), "hash": hash.finish(),
    })
}

fn state_fingerprint(solver: &Solver, exploit: f64) -> Value {
    let mut combined = Fingerprint::new();
    combined.bytes(b"postflop-autoresearch-state-v1");
    let algorithm = serde_json::to_vec(&solver.algo).unwrap();
    combined.bytes(&(algorithm.len() as u64).to_le_bytes());
    combined.bytes(&algorithm);
    combined.bytes(&solver.iteration.to_le_bytes());
    combined.bytes(&[u8::from(solver.use_isomorphism)]);
    combined.bytes(&exploit.to_bits().to_le_bytes());
    let mut arenas = Vec::new();
    for player in 0..2 {
        for (name, store) in [
            ("regrets", &solver.regrets[player]),
            ("strategy_sums", &solver.strat[player]),
        ] {
            combined.bytes(&(player as u64).to_le_bytes());
            combined.bytes(name.as_bytes());
            let mut arena = fingerprint_store(store, &mut combined);
            arena["player"] = json!(player);
            arena["arena"] = json!(name);
            arenas.push(arena);
        }
    }
    // Root strategy is cheap and does not materialize inactive suit branches.
    let root_strategy_bits: Vec<u32> = solver
        .average_strategy(0, &solver.spot.tree.nodes[0])
        .iter()
        .map(|value| value.to_bits())
        .collect();
    json!({
        "method": "fnv1a64-little-endian-v1", "hash": combined.finish(),
        "algorithm": solver.algo, "iteration": solver.iteration,
        "iteration_le_bytes": solver.iteration.to_le_bytes(),
        "exploit_bits": exploit.to_bits(), "arenas": arenas,
        "root_strategy_bits": root_strategy_bits,
        "scope": "all CPU regret and strategy entries and scales immediately after full GPU readback",
    })
}

#[test]
#[ignore = "manual complete-cycle postflop CUDA performance and state fingerprints"]
fn postflop_complete_cycle() {
    let filter = std::env::var("POSTFLOP_AUTORESEARCH_FIXTURE").ok();
    if let Some(filter) = &filter {
        assert!(
            FIXTURES.iter().any(|(name, _, _)| *name == filter.as_str()),
            "unknown POSTFLOP_AUTORESEARCH_FIXTURE {filter:?}"
        );
    }
    let storage = match std::env::var("POSTFLOP_AUTORESEARCH_STORAGE").as_deref() {
        Ok("f32") => Storage::F32,
        Ok("compressed") | Err(_) => Storage::Compressed,
        Ok(other) => panic!("unknown POSTFLOP_AUTORESEARCH_STORAGE {other:?}"),
    };
    let storage_name = if storage == Storage::Compressed { "compressed" } else { "f32" };
    let profile = match std::env::var("POSTFLOP_AUTORESEARCH_PROFILE").as_deref() {
        Ok("1") => true,
        Ok("0") | Err(_) => false,
        Ok(other) => panic!("unknown POSTFLOP_AUTORESEARCH_PROFILE {other:?}"),
    };
    emit_stage(json!({
        "schema_version": 1, "stage": "suite_start", "storage": storage_name,
        "fixture_filter": filter, "smoke_only": filter.is_some(),
        "primary_suite": filter.is_none() && storage == Storage::Compressed,
        "target_pct": TARGET_PCT_POT, "check_every": CHECK_EVERY,
        "max_iterations": MAX_ITERATIONS, "profile_after_timing": profile,
        "timing_scope": "tree build and CPU allocation through full GPU readback; excludes cargo compilation, fingerprinting and optional diagnostic profiling",
        "runtime_nvrtc_jit_included": false, "flushed_progress_logging_included": true,
        "initialization_note": "fixed fixture order; first GPU initialization includes runtime NVRTC/JIT work; device compiler/module caches may be warm after the first fixture",
    }));

    let mut completed = 0;
    for (fixture_index, &(name, board, rake)) in FIXTURES.iter().enumerate() {
        if filter.as_ref().is_some_and(|filter| filter.as_str() != name) {
            continue;
        }
        let mut config: SpotConfig =
            serde_json::from_str(include_str!("bench_spot.json")).unwrap();
        config.board = board.into();
        config.tree.rake_pct = rake;
        config.tree.rake_cap = 3.0;
        let config_json = serde_json::to_value(&config).unwrap();
        emit_stage(json!({
            "stage": "fixture_start", "fixture_id": name, "fixture_index": fixture_index,
            "board": board, "storage": storage_name, "config": config_json,
        }));

        let total_start = Instant::now();
        let stage_start = Instant::now();
        let mut host = Solver::with_storage(Arc::new(Spot::new(config).unwrap()), storage);
        let build_cpu_alloc_ms = elapsed_ms(stage_start);
        assert_eq!(host.algo, Algorithm::Dcfr, "frozen evaluator expects default DCFR");
        assert!(host.use_isomorphism, "frozen evaluator expects default suit isomorphism");
        emit_stage(json!({
            "stage": "build_complete", "fixture_id": name,
            "build_ms": build_cpu_alloc_ms,
            "nodes": host.spot.tree.nodes.len(), "hands": host.spot.hands.each_ref().map(|hands| hands.len()),
            "cpu_arena_bytes": host.arena_bytes(),
        }));

        let stage_start = Instant::now();
        let mut gpu = GpuSolver::new(&host).expect("benchmark requires CUDA");
        gpu.synchronize().unwrap();
        let gpu_init_ms = elapsed_ms(stage_start);
        emit_stage(json!({"stage": "gpu_ready", "fixture_id": name, "init_ms": gpu_init_ms}));

        let solve_start = Instant::now();
        let (exploit, exploit_pct_pot) = loop {
            for _ in 0..CHECK_EVERY {
                gpu.iterate().unwrap();
            }
            let exploit = gpu.exploitability(&host).unwrap();
            let pct = exploit / host.spot.tree.config.starting_pot * 100.0;
            assert!(exploit.is_finite() && pct.is_finite(), "nonfinite exploitability");
            emit_stage(json!({
                "stage": "convergence_check", "fixture_id": name, "iteration": gpu.iteration,
                "exploit_chips": exploit, "exploit_pct_pot": pct,
                "exploit_bits": exploit.to_bits(), "solve_checks_elapsed_ms": elapsed_ms(solve_start),
            }));
            if pct <= TARGET_PCT_POT || gpu.iteration >= MAX_ITERATIONS {
                break (exploit, pct);
            }
        };
        gpu.synchronize().unwrap();
        let solve_checks_ms = elapsed_ms(solve_start);

        let stage_start = Instant::now();
        gpu.sync_to_cpu(&mut host).unwrap();
        gpu.synchronize().unwrap();
        let full_readback_ms = elapsed_ms(stage_start);
        let total_ms = elapsed_ms(total_start);
        assert_eq!(host.iteration, gpu.iteration);
        let target_met = exploit_pct_pot <= TARGET_PCT_POT;
        emit_stage(json!({
            "stage": "timing_complete", "fixture_id": name, "storage": storage_name,
            "build_ms": build_cpu_alloc_ms, "init_ms": gpu_init_ms,
            "solve_ms": solve_checks_ms, "readback_ms": full_readback_ms,
            "full_cycle_ms": total_ms, "iteration": host.iteration,
            "exploit_chips": exploit, "exploit_pct_pot": exploit_pct_pot,
            "exploit_bits": exploit.to_bits(), "target_met": target_met,
        }));

        // The score stops above. Fingerprinting touches all stores without a save
        // file, a giant temporary byte vector, or a mutating query/materialization.
        let fingerprint_start = Instant::now();
        let fingerprint = state_fingerprint(&host, exploit);
        emit_result(json!({
            "schema_version": 1, "stage": "fixture_complete", "fixture_id": name,
            "fixture_index": fixture_index, "board": board,
            "storage": storage_name, "config": config_json, "algorithm": host.algo,
            "use_isomorphism": host.use_isomorphism, "nodes": host.spot.tree.nodes.len(),
            "cpu_arena_bytes": host.arena_bytes(), "iteration": host.iteration,
            "target_pct": TARGET_PCT_POT, "check_every": CHECK_EVERY,
            "max_iterations": MAX_ITERATIONS, "target_met": target_met,
            "exploit_chips": exploit, "exploit_pct_pot": exploit_pct_pot,
            "exploit_bits": exploit.to_bits(), "fingerprint": fingerprint["hash"],
            "state_fingerprint": fingerprint,
            "fingerprint_ms_excluded": elapsed_ms(fingerprint_start),
            "build_ms": build_cpu_alloc_ms, "init_ms": gpu_init_ms,
            "solve_ms": solve_checks_ms, "readback_ms": full_readback_ms,
            "full_cycle_ms": total_ms,
            "runtime_nvrtc_jit_included": false, "flushed_progress_logging_included": true,
        }));
        assert!(target_met, "{name} did not reach the frozen target within {MAX_ITERATIONS} iterations");

        if profile {
            let diagnostic = gpu.iterate_profiled().unwrap();
            emit_stage(json!({
                "stage": "diagnostic_profile", "fixture_id": name,
                "iteration": gpu.iteration, "kernel_names": KERNEL_NAMES,
                "profile_ms": diagnostic.ms, "launches": diagnostic.launches,
                "excluded_from_score": true,
                "note": "one additional iteration with synchronization after each launch; absolute timing includes synchronization overhead",
            }));
        }
        assert!(!profile,"D287no profiling");
        d287_after(gpu,host,name,exploit);
        completed += 1;
    }
    emit_stage(json!({
        "stage": "suite_complete", "fixtures_completed": completed,
        "full_fixture_suite": completed == FIXTURES.len(),
        "primary_suite": filter.is_none() && storage == Storage::Compressed,
        "storage": storage_name,
    }));
}

pub trait Word:DeviceRepr+Clone+Default{fn append(&self,out:&mut Vec<u32>);}
impl Word for u32{fn append(&self,out:&mut Vec<u32>){out.push(*self);}}
impl Word for i32{fn append(&self,out:&mut Vec<u32>){out.push(*self as u32);}}
impl Word for f32{fn append(&self,out:&mut Vec<u32>){out.push(self.to_bits());}}
impl Word for u64{fn append(&self,out:&mut Vec<u32>){out.push(*self as u32);out.push((*self>>32)as u32);}}
impl Word for i64{fn append(&self,out:&mut Vec<u32>){(*self as u64).append(out);}}
fn words<T:Word>(values:&[T])->Vec<u32>{let mut out=Vec::with_capacity(values.len()*std::mem::size_of::<T>()/4);for v in values{v.append(&mut out);}out}
fn write_words(out:&mut BufWriter<File>,values:&[u32]){for v in values{out.write_all(&v.to_le_bytes()).unwrap();}}
fn frame_header(out:&mut BufWriter<File>,kind:u32,name:&str,count:usize){out.write_all(&kind.to_le_bytes()).unwrap();out.write_all(&(name.len()as u32).to_le_bytes()).unwrap();out.write_all(name.as_bytes()).unwrap();out.write_all(&(count as u64).to_le_bytes()).unwrap();}
fn host_field(out:&mut BufWriter<File>,name:&str,v:&[u32]){
    if v.iter().fold(0u32,|a,&b|a|b)==0{frame_header(out,0,name,v.len());out.write_all(&0u32.to_le_bytes()).unwrap();}
    else{frame_header(out,2,name,v.len());write_words(out,v);}
}
pub fn d166_field<T:Word>(s:&Arc<CudaStream>,name:&str,d:&CudaSlice<T>,out:&mut BufWriter<File>)->Value{
 let bytes=d.len().checked_mul(std::mem::size_of::<T>()).unwrap();assert!(bytes<=8*1024usize.pow(3));
 let values=s.clone_dtoh(d).unwrap();s.synchronize().unwrap();assert_eq!(values.len(),d.len());
 let bits=words(&values);assert_eq!(bits.len()*4,bytes);host_field(out,name,&bits);
 let(address,guard)=d.device_ptr(s);drop(guard);
 json!({"name":name,"elements":d.len(),"element_bytes":std::mem::size_of::<T>(),"words":bits.len(),"raw_bytes":bytes,"address":address})
}

fn d156_cpu(path:&std::path::Path,s:&Solver) {
    let mut f=std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(path).unwrap());
    f.write_all(b"D156-CPU-RAW1\0\0\0").unwrap();
    for v in [s.iteration,s.use_isomorphism as u32,s.locks.len()as u32,s.preds.is_some()as u32] {f.write_all(&v.to_le_bytes()).unwrap();}
    for stores in [&s.regrets,&s.strat] {for store in stores {
        match store {
            Store::I16{q,scale}=>{f.write_all(&1u32.to_le_bytes()).unwrap();f.write_all(&(q.len()as u64).to_le_bytes()).unwrap();f.write_all(&(scale.len()as u64).to_le_bytes()).unwrap();for v in q.as_slice(){f.write_all(&v.to_le_bytes()).unwrap();}for v in scale.as_slice(){f.write_all(&v.to_bits().to_le_bytes()).unwrap();}},
            Store::U16{q,scale}=>{f.write_all(&2u32.to_le_bytes()).unwrap();f.write_all(&(q.len()as u64).to_le_bytes()).unwrap();f.write_all(&(scale.len()as u64).to_le_bytes()).unwrap();for v in q.as_slice(){f.write_all(&v.to_le_bytes()).unwrap();}for v in scale.as_slice(){f.write_all(&v.to_bits().to_le_bytes()).unwrap();}},
            Store::F32(_)=>panic!("fixed compressed primary control"),
        }
    }}
    f.flush().unwrap();f.get_ref().sync_all().unwrap();
}

#[repr(C)]#[derive(Default)]struct D287FileTime{lo:u32,hi:u32}
#[repr(C)]#[derive(Default)]struct D287Memory{cb:u32,faults:u32,peak_ws:usize,ws:usize,peak_paged:usize,paged:usize,peak_nonpaged:usize,nonpaged:usize,pagefile:usize,peak_pagefile:usize,private:usize}
#[link(name="kernel32")]extern "system"{fn GetCurrentProcess()->*mut std::ffi::c_void;fn GetProcessTimes(h:*mut std::ffi::c_void,created:*mut D287FileTime,exited:*mut D287FileTime,kernel:*mut D287FileTime,user:*mut D287FileTime)->i32;fn K32GetProcessMemoryInfo(h:*mut std::ffi::c_void,p:*mut D287Memory,cb:u32)->i32;fn GetTickCount64()->u64;}
fn d287_os()->Value{
 assert_eq!(std::mem::size_of::<D287FileTime>(),8);assert_eq!(std::mem::size_of::<D287Memory>(),80);
 let(mut a,mut b,mut k,mut u)=(D287FileTime::default(),D287FileTime::default(),D287FileTime::default(),D287FileTime::default());let mut m=D287Memory::default();m.cb=80;
 unsafe{assert_ne!(GetProcessTimes(GetCurrentProcess(),&mut a,&mut b,&mut k,&mut u),0);assert_ne!(K32GetProcessMemoryInfo(GetCurrentProcess(),&mut m,80),0);}
 let q=|v:D287FileTime|u64::from(v.lo)|(u64::from(v.hi)<<32);json!({"tick_ms":unsafe{GetTickCount64()},"kernel_ticks100ns":q(k),"user_ticks100ns":q(u),"private_bytes":m.private,"working_set_bytes":m.ws,"reported_lifetime_peak_WS_bytes":m.peak_ws,"reported_lifetime_peak_commit_bytes":m.peak_pagefile})
}
fn d287_after(mut g:GpuSolver,s:Solver,name:&str,exploit:f64){
 let out=std::path::PathBuf::from(std::env::var("D156_OUTPUT").unwrap());let before_cpu=state_fingerprint(&s,exploit);d156_cpu(&out.join(format!("{name}-before.cpu.bin")),&s);let before=g.d166_snapshot(&out.join(format!("{name}-before.gpu.bin")));
 println!("D287_BEFORE {}",json!({"fixture":name,"info":before}));std::io::stdout().flush().unwrap();
 let cohort=[("W0B",false,false,0x4b123456),("W0C",true,false,0x4b123456),("W1C",true,false,0x80000000),("W1B",false,false,0x80000000),("B1",false,true,0x7fc12345),("C1",true,true,0x7fc12345),("C2",true,true,0x7f812345),("B2",false,true,0x7f812345),("B3",false,true,0x4b123456),("C3",true,true,0x4b123456)];
 for player in 0..2{for(tag,candidate,scored,poison)in cohort{
  let id=format!("{name}-p{player}-{tag}");g.d287_poison(poison).unwrap();let os_before=d287_os();println!("D287_CASE_START {}",json!({"id":id,"fixture":name,"player":player,"candidate":candidate,"scored":scored,"OS":os_before}));std::io::stdout().flush().unwrap();
  let replays=s.iteration;let stats=g.d287_component(player,candidate,replays).unwrap();let os_after=d287_os();let info=g.d166_snapshot(&out.join(format!("{id}.gpu.bin")));assert_eq!(info,before);
  println!("D287_CASE {}",json!({"id":id,"fixture":name,"player":player,"candidate":candidate,"scored":scored,"poison_bits":poison,"replays":replays,"stats":stats,"OS_before":os_before,"OS_after":os_after,"info":info}));std::io::stdout().flush().unwrap();
 }}
 let after_cpu=state_fingerprint(&s,exploit);assert_eq!(before_cpu,after_cpu);d156_cpu(&out.join(format!("{name}-after.cpu.bin")),&s);g.synchronize().unwrap();drop(g);drop(s);
 println!("D287_FIXTURE_COMPLETE {}",json!({"fixture":name,"component_cases":20,"CPU_state_fingerprint_unchanged":true,"all_owned_GPU_and_CPU_objects_dropped":true,"solver_accuracy_unchanged":true}));std::io::stdout().flush().unwrap();
}
