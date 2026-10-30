#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="baseline/mod.rs"]mod reference;
#[path="candidate/mod.rs"]mod changed;
// Complete postflop CUDA lifecycle benchmark for the 2026-10-16 research pass.
// Freeze this evaluator and bench_spot.json before recording the first baseline.
// Run with --ignored --nocapture --test-threads=1. Every progress line is flushed.
// POSTFLOP_AUTORESEARCH_FIXTURE=rainbow|two-tone|river selects a smoke test only.
// POSTFLOP_AUTORESEARCH_STORAGE=f32 selects secondary coverage (default compressed).
// POSTFLOP_AUTORESEARCH_PROFILE=1 adds one diagnostic iteration AFTER scoring.
// No saved games or historical research artifacts are read or written.

use serde_json::{json, Value};
use solver::gpu::{GpuSolver, KERNEL_NAMES};
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


use std::ffi::c_void;
use std::sync::Mutex;
static D174_EVENTS:Mutex<Vec<serde_json::Value>>=Mutex::new(Vec::new());
pub fn d174_mark(role:&'static str,label:&'static str) {
 D174_EVENTS.lock().unwrap().push(serde_json::json!({"role":role,"label":label,"thread":format!("{:?}",std::thread::current().id())}));
}
#[repr(C)]#[derive(Default)]struct D174FileTime{lo:u32,hi:u32}
impl D174FileTime{fn ticks(&self)->u64{self.lo as u64|((self.hi as u64)<<32)}}
#[link(name="kernel32")]
extern "system" {
 fn GetCurrentProcess()->*mut c_void;
 fn GetProcessTimes(process:*mut c_void,created:*mut D174FileTime,exit:*mut D174FileTime,kernel:*mut D174FileTime,user:*mut D174FileTime)->i32;
 fn GetModuleHandleW(name:*const u16)->*mut c_void;
}
fn d174_cpu()->u64 {
 let(mut c,mut e,mut k,mut u)=(D174FileTime::default(),D174FileTime::default(),D174FileTime::default(),D174FileTime::default());
 assert_ne!(unsafe{GetProcessTimes(GetCurrentProcess(),&mut c,&mut e,&mut k,&mut u)},0);k.ticks()+u.ticks()
}
fn d174_driver_loaded()->bool{let dll:Vec<u16>="nvcuda.dll\0".encode_utf16().collect();!unsafe{GetModuleHandleW(dll.as_ptr())}.is_null()}

#[test]
fn d174_budget_failure_costs() {
 assert!(!d174_driver_loaded());
 let order=[["baseline","candidate"],["candidate","baseline"],["baseline","candidate"]];
 for (fixture,board,rake) in FIXTURES {
  let mut config:SpotConfig=serde_json::from_str(include_str!("bench_spot.json")).unwrap();config.board=board.into();config.tree.rake_pct=*rake;config.tree.rake_cap=3.;
  let host=Solver::with_storage(Arc::new(Spot::new(config).unwrap()),Storage::Compressed);
  for (pair,arms) in order.iter().enumerate(){
   let mut errors=Vec::new();
   for role in arms {
    let before=state_fingerprint(&host,0.);D174_EVENTS.lock().unwrap().clear();
    let cpu_start=d174_cpu();let clock=Instant::now();
    let outcome=match *role {"baseline"=>reference::GpuSolver::new_with_budget(&host,0).err().unwrap(),"candidate"=>changed::GpuSolver::new_with_budget(&host,0).err().unwrap(),_=>unreachable!()};
    let wall_ms=clock.elapsed().as_secs_f64()*1000.;let cpu_ms=(d174_cpu()-cpu_start) as f64/10000.;
    let events=D174_EVENTS.lock().unwrap().clone();assert!(!d174_driver_loaded());
    let after=state_fingerprint(&host,0.);assert_eq!(before,after);assert!(outcome.contains("budget 0 MB"));errors.push(outcome.clone());
    println!("D174_RESULT {}",serde_json::json!({"fixture":fixture,"board":board,"nodes":host.spot.tree.nodes.len(),"pair":pair,"role":role,"budget_bytes":0,"error":outcome,"wall_ms":wall_ms,"CPU_ms":cpu_ms,"events":events,"before_CPU_fingerprint":before,"after_CPU_fingerprint":after,"nvcuda_loaded":false,"application_kernels":0,"performance_qualification_sample":false}));
   }
   assert_eq!(errors[0],errors[1]);
  }
 }
 // Unsupported algorithms reject before planning/scans/CUDA, including the moved setup.
 let mut config:SpotConfig=serde_json::from_str(include_str!("bench_spot.json")).unwrap();config.board="Ks7h2dQhTc".into();
 let mut host=Solver::with_storage(Arc::new(Spot::new(config).unwrap()),Storage::Compressed);host.algo=Algorithm::PcfrPlus;
 for role in ["baseline","candidate"] {
  D174_EVENTS.lock().unwrap().clear();let before=state_fingerprint(&host,0.);
  let error=if role=="baseline" {reference::GpuSolver::new_with_budget(&host,u64::MAX).err().unwrap()} else {changed::GpuSolver::new_with_budget(&host,u64::MAX).err().unwrap()};
  assert_eq!(error,"GPU solver supports dcfr/cfr+ only");assert_eq!(before,state_fingerprint(&host,0.));assert!(!d174_driver_loaded());
  println!("D174_UNSUPPORTED {}",serde_json::json!({"role":role,"error":error,"events":D174_EVENTS.lock().unwrap().clone(),"nvcuda_loaded":false,"CPU_fingerprint":before}));
 }
 println!("D174_COMPLETE {}",serde_json::json!({"budget_calls":18,"unsupported_calls":2,"CPU_immutability_checks":20,"nvcuda_loaded":false,"application_kernels":0,"all_constructor_calls_returned":true}));
}
