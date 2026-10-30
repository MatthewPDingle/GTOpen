#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
#[path="baseline/mod.rs"]mod observed;
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
        "runtime_nvrtc_jit_included": true, "flushed_progress_logging_included": true,
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
            "runtime_nvrtc_jit_included": true, "flushed_progress_logging_included": true,
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
        assert!(!profile, "resource/lifecycle control forbids optional profiler");
        d156_after(gpu,host,name);
        completed += 1;
    }
    emit_stage(json!({
        "stage": "suite_complete", "fixtures_completed": completed,
        "full_fixture_suite": completed == FIXTURES.len(),
        "primary_suite": filter.is_none() && storage == Storage::Compressed,
        "storage": storage_name,
    }));
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
fn d156_stage(g:&GpuSolver,s:&Solver,out:&std::path::Path,name:&str,stage:&str,ev:Option<u64>) -> Value {
    d156_cpu(&out.join(format!("{name}-{stage}.cpu.bin")),s);
    let info=g.d156_snapshot(&out.join(format!("{name}-{stage}.cfv.u32")));
    json!({"stage":stage,"iteration":s.iteration,"ev_bits":ev,"info":info})
}
fn d156_query(out:&std::path::Path,name:&str,stage:&str,s:&mut Solver) {
    s.ensure_symmetric();let q=serde_json::to_vec(&s.node_view(&[]).unwrap()).unwrap();
    let mut f=std::fs::OpenOptions::new().create_new(true).write(true).open(out.join(format!("{name}-{stage}.query.json"))).unwrap();f.write_all(&q).unwrap();f.sync_all().unwrap();
}
fn d156_after(mut g:GpuSolver,mut s:Solver,name:&str) {
    let out=std::path::PathBuf::from(std::env::var("D156_OUTPUT").unwrap());
    assert_eq!(s.algo,Algorithm::Dcfr);assert!(s.use_isomorphism);
    let mut stages=vec![d156_stage(&g,&s,&out,name,"converged",None)];
    g.iterate().unwrap();let e=g.exploitability(&s).unwrap();assert!(e.is_finite());g.sync_to_cpu(&mut s).unwrap();
    stages.push(d156_stage(&g,&s,&out,name,"continued",Some(e.to_bits())));
    s.ensure_symmetric();s.lock_node(&[],solver::LockMode::Freeze,"D156".into()).unwrap();g.update_locks(&s).unwrap();
    g.iterate().unwrap();let e=g.exploitability(&s).unwrap();assert!(e.is_finite());g.sync_to_cpu(&mut s).unwrap();
    stages.push(d156_stage(&g,&s,&out,name,"locked",Some(e.to_bits())));d156_query(&out,name,"locked",&mut s);
    let save=out.join(format!("{name}.save"));s.save(save.to_str().unwrap()).unwrap();drop(g);drop(s);
    let mut s=Solver::load_with_storage(save.to_str().unwrap(),Storage::Compressed).unwrap();assert_eq!(s.algo,Algorithm::Dcfr);assert!(s.use_isomorphism);
    let mut g=GpuSolver::new(&s).unwrap();g.iterate().unwrap();let e=g.exploitability(&s).unwrap();assert!(e.is_finite());g.sync_to_cpu(&mut s).unwrap();
    stages.push(d156_stage(&g,&s,&out,name,"resumed",Some(e.to_bits())));d156_query(&out,name,"resumed",&mut s);
    drop(g);drop(s);
    println!("D156_CONTROL {}",json!({"fixture_id":name,"stages":stages,"all_GPU_and_CPU_objects_dropped":true,"performance_measurement":false}));std::io::stdout().flush().unwrap();
}
