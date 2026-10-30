//! Frozen E020 wide-turn holdout, separate from the primary evaluator.
//! Uses only adjacent fixture.json, DCFR/compressed/iso, target0.3% every20, max400.
//! Primary fixture/storage/profile environment overrides are rejected.
//! POSTFLOP_HOLDOUT_STATE must name a unique per-run raw CPU-store output file.
//! Full q/scale words are exported after timing; no profiling or duplicate plan.
#![cfg(feature = "gpu")]

use serde_json::{json, Value};
use solver::gpu::GpuSolver;
use solver::store::{Storage, Store};
use solver::{Algorithm, Solver, Spot, SpotConfig};
use std::io::{self, Write};
use std::sync::Arc;
use std::time::Instant;

const TARGET_PCT_POT: f64 = 0.3;
const CHECK_EVERY: u32 = 20;
const MAX_ITERATIONS: u32 = 400;
const FIXTURES: [(&str, &str, f64); 1] = [("wide-turn-full169", "Ks7h2dQh", 0.05)];

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


// Exact framed store bytes; this is after total_ms and fingerprinting.
// No dequantization, materialization, query mutation or unbounded temporary copy.
fn write_raw_state(solver: &Solver, exploit: f64, path: &std::path::Path) -> u64 {
    let file = std::fs::OpenOptions::new().write(true).create_new(true).open(path).unwrap();
    let mut out = std::io::BufWriter::with_capacity(1024 * 1024, file);
    out.write_all(b"GTO-WIDE-RAW-v1\0").unwrap();
    let metadata = serde_json::to_vec(&json!({"algorithm":solver.algo,"iteration":solver.iteration,
        "use_isomorphism":solver.use_isomorphism,"exploit_bits":exploit.to_bits()})).unwrap();
    out.write_all(&(metadata.len() as u64).to_le_bytes()).unwrap();
    out.write_all(&metadata).unwrap();
    for player in 0..2 {
        for (arena,store) in [(0u8,&solver.regrets[player]),(1u8,&solver.strat[player])] {
            let (kind,entries,scales) = match store {
                Store::F32(q) => (0u8,q.len(),0),
                Store::I16{q,scale} => (1,q.len(),scale.len()),
                Store::U16{q,scale} => (2,q.len(),scale.len()),
            };
            out.write_all(&[player as u8,arena,kind]).unwrap();
            out.write_all(&(entries as u64).to_le_bytes()).unwrap();
            out.write_all(&(scales as u64).to_le_bytes()).unwrap();
            match store {
                Store::F32(q) => for v in q.as_slice() {out.write_all(&v.to_bits().to_le_bytes()).unwrap();},
                Store::I16{q,scale} => {
                    for v in q.as_slice() {out.write_all(&v.to_le_bytes()).unwrap();}
                    for v in scale.as_slice() {out.write_all(&v.to_bits().to_le_bytes()).unwrap();}
                },
                Store::U16{q,scale} => {
                    for v in q.as_slice() {out.write_all(&v.to_le_bytes()).unwrap();}
                    for v in scale.as_slice() {out.write_all(&v.to_bits().to_le_bytes()).unwrap();}
                },
            }
        }
    }
    out.flush().unwrap();
    out.get_ref().sync_all().unwrap();
    out.get_ref().metadata().unwrap().len()
}

#[test]
#[ignore = "manual frozen wide-turn holdout; serialized root runner only"]
fn postflop_wide_turn_holdout() {
    let filter: Option<String> = None;
    let storage = Storage::Compressed;
    let storage_name = "compressed";
    let profile = false;
    let state_path = std::env::var_os("POSTFLOP_HOLDOUT_STATE").expect("unique raw state path required");
    for variable in ["POSTFLOP_AUTORESEARCH_FIXTURE", "POSTFLOP_AUTORESEARCH_STORAGE", "POSTFLOP_AUTORESEARCH_PROFILE"] {
        assert!(std::env::var_os(variable).is_none(), "holdout rejects primary overrides");
    }
    emit_stage(json!({
        "schema_version": 1, "stage": "suite_start", "storage": storage_name,
        "fixture_filter": filter, "smoke_only": filter.is_some(),
        "primary_suite": false, "wide_holdout": true,
        "target_pct": TARGET_PCT_POT, "check_every": CHECK_EVERY,
        "max_iterations": MAX_ITERATIONS, "profile_after_timing": profile,
        "timing_scope": "tree build and CPU allocation through full GPU readback; excludes cargo compilation, fingerprinting and optional diagnostic profiling",
        "runtime_nvrtc_jit_included": true, "flushed_progress_logging_included": true,
        "initialization_note": "one fresh wide-turn process; runtime NVRTC/JIT included; persistent driver cache retained without reset or selective warmup",
    }));

    let mut completed = 0;
    for (fixture_index, &(name, board, rake)) in FIXTURES.iter().enumerate() {
        if filter.as_ref().is_some_and(|filter| filter.as_str() != name) {
            continue;
        }
        let mut config: SpotConfig =
            serde_json::from_str(include_str!("fixture.json")).unwrap();
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
        let spot = Spot::new_with_limit(config, Some(20_000)).unwrap();
        assert_eq!(spot.hands.each_ref().map(|h| h.len()), [1128,1128]);
        assert!(spot.tree.nodes.len() <= 11_691);
        let vram_estimate = spot.vram_estimate_bytes();
        assert!(vram_estimate <= 2 * 1024u64.pow(3));
        let mut river_cards = 0;
        let mut river_max = [0usize;2];
        for card in 0u8..52 {
            if spot.board_mask & (1u64 << card) != 0 { continue; }
            let river = spot.river.get(&solver::game::Dealt { cards: [card,0], len:1 });
            for p in 0..2 {
                assert_eq!(river.sorted[p].len(),1081);
                river_max[p] = river_max[p].max(river.sorted[p].len());
            }
            river_cards += 1;
        }
        assert_eq!(river_cards,48);
        emit_stage(json!({"stage":"holdout_admission","fixture_id":name,
            "hands":[1128,1128],"river_cards":river_cards,"river_max":river_max,
            "baseline_dynamic_shared_bytes":[13160,13160],"candidate_dynamic_shared_bytes":[21808,21808],
            "nodes":spot.tree.nodes.len(),"tree_bytes":spot.tree_bytes(),
            "cpu_arena_bytes_expected":spot.arena_bytes_for(storage),
            "public_vram_estimate_bytes":vram_estimate,"gpu_budget_bytes":2*1024u64.pow(3),
            "duplicate_plan_built":false}));
        let mut host = Solver::with_storage(Arc::new(spot), storage);
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
        let mut gpu = GpuSolver::new_with_budget(&host, 2 * 1024u64.pow(3)).expect("holdout requires admitted CUDA");
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

        let raw = write_raw_state(&host, exploit, std::path::Path::new(&state_path));
        emit_stage(json!({"stage":"raw_state_complete","fixture_id":name,
            "bytes":raw,"arenas":4,"excluded_from_score":true,"schema":"gtopen-wide-raw-v1"}));
        // Read the still-live solver context after timing; do not create or retain
        // another context owner. This is device-wide usage, not a solver-only delta.
        let mut current = std::ptr::null_mut();
        let mut free = 0usize;
        let mut total = 0usize;
        unsafe {
            assert_eq!(cudarc::driver::sys::cuCtxGetCurrent(&mut current), cudarc::driver::sys::CUresult::CUDA_SUCCESS);
            assert!(!current.is_null());
            assert_eq!(cudarc::driver::sys::cuMemGetInfo_v2(&mut free, &mut total), cudarc::driver::sys::CUresult::CUDA_SUCCESS);
        }
        emit_stage(json!({"stage":"postscore_device_memory","fixture_id":name,
            "free_bytes":free,"total_bytes":total,"device_wide_used_bytes":total-free,
            "scope":"device-wide residency while this solver is live; not attributable solely to solver",
            "excluded_from_score":true,"new_context_created":false}));
        completed += 1;
    }
    emit_stage(json!({
        "stage": "suite_complete", "fixtures_completed": completed,
        "full_fixture_suite": completed == FIXTURES.len(),
        "primary_suite": false, "wide_holdout": true,
        "storage": storage_name,
    }));
}
