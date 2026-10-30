//! Supplemental, immutable baseline/candidate controls for wide NA=3 dispatch.
//! No performance score. Run serially with an unused POSTFLOP_DIRECT3_CONTROL_DIR.
//! Eligibility is derived from the original public plan API so this same file
//! compiles on E004 and on the direct3 candidate, without candidate-only fields.
#![cfg(feature = "gpu")]

use serde_json::{json, Value};
use solver::gpu::{plan::GpuPlan, GpuSolver};
use solver::store::{Storage, Store};
use solver::tree::{KIND_ACTION, KIND_CHANCE, SENTINEL};
use solver::{parse_sizes, Algorithm, LockMode, PathStep, Solver, Spot, SpotConfig, StreetSizing, TreeConfig};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::sync::Arc;

const ELIGIBLE_LEVEL_SIZE: u32 = 4096;

struct Fingerprint(u64);
impl Fingerprint {
    fn new() -> Self { Self(0xcbf29ce484222325) }
    fn bytes(&mut self, bytes: &[u8]) {
        for &b in bytes { self.0 = (self.0 ^ u64::from(b)).wrapping_mul(0x100000001b3); }
    }
    fn finish(&self) -> String { format!("{:016x}", self.0) }
}

fn hash_bytes(bytes: &[u8]) -> String {
    let mut h = Fingerprint::new();
    h.bytes(bytes);
    h.finish()
}

fn hash_file(path: &Path) -> String {
    let mut file = std::fs::File::open(path).unwrap();
    let mut h = Fingerprint::new();
    let mut buf = [0u8; 65536];
    loop {
        let n = file.read(&mut buf).unwrap();
        if n == 0 { break; }
        h.bytes(&buf[..n]);
    }
    h.finish()
}

fn raw_state(s: &Solver) -> Value {
    let mut combined = Fingerprint::new();
    combined.bytes(b"postflop-direct3-control-v1");
    combined.bytes(&s.iteration.to_le_bytes());
    combined.bytes(&serde_json::to_vec(&s.algo).unwrap());
    combined.bytes(&[u8::from(s.use_isomorphism)]);
    let mut arenas = Vec::new();
    for p in 0..2 {
        for (name, store) in [("regrets", &s.regrets[p]), ("strategy", &s.strat[p])] {
            let mut h = Fingerprint::new();
            let mut feed = |bytes: &[u8]| { h.bytes(bytes); combined.bytes(bytes); };
            feed(&(p as u32).to_le_bytes());
            feed(name.as_bytes());
            let (kind, entries, scales) = match store {
                Store::F32(b) => {
                    feed(b"f32");
                    feed(&(b.len() as u64).to_le_bytes());
                    for v in b.as_slice() {
                        assert!(v.is_finite(), "nonfinite full arena value");
                        feed(&v.to_bits().to_le_bytes());
                    }
                    ("f32", b.len(), 0)
                }
                Store::I16 { q, scale } => {
                    feed(b"i16");
                    feed(&(q.len() as u64).to_le_bytes());
                    feed(&(scale.len() as u64).to_le_bytes());
                    for v in q.as_slice() { feed(&v.to_le_bytes()); }
                    for v in scale.as_slice() {
                        assert!(v.is_finite(), "nonfinite regret scale");
                        feed(&v.to_bits().to_le_bytes());
                    }
                    ("i16", q.len(), scale.len())
                }
                Store::U16 { q, scale } => {
                    feed(b"u16");
                    feed(&(q.len() as u64).to_le_bytes());
                    feed(&(scale.len() as u64).to_le_bytes());
                    for v in q.as_slice() { feed(&v.to_le_bytes()); }
                    for v in scale.as_slice() {
                        assert!(v.is_finite(), "nonfinite strategy scale");
                        feed(&v.to_bits().to_le_bytes());
                    }
                    ("u16", q.len(), scale.len())
                }
            };
            arenas.push(json!({"player":p,"arena":name,"kind":kind,"entries":entries,
                "scales":scales,"hash":h.finish()}));
        }
    }
    json!({"hash":combined.finish(),"arenas":arenas})
}

fn fixture() -> Arc<Spot> {
    let sizing = || StreetSizing { bet:parse_sizes("33 75").unwrap(), raise:vec![], donk:vec![] };
    Arc::new(Spot::new(SpotConfig {
        board:"KsQs2d".into(), range_oop:"AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
        range_ip:"AA,QQ,TT,77,AQs,KQs,AQo".into(),
        tree:TreeConfig { starting_pot:10.0, effective_stack:100.0, rake_pct:0.05, rake_cap:1.0,
            oop:[sizing(),sizing(),sizing()], ip:[sizing(),sizing(),sizing()],
            max_raises:0, add_allin:false, allin_threshold:0.85,
            carry_aggressor_through_checks:Some(false) },
    }).unwrap())
}

struct Coverage {
    ids: [u32; 2],
    paths: [Vec<PathStep>; 2],
    evidence: Value,
}

// Derive paths from real edges, never from plan ordering or presumed bet menus.
fn parents(spot: &Spot) -> Vec<Option<(u32, PathStep)>> {
    let mut parent = vec![None; spot.tree.nodes.len()];
    for (id, node) in spot.tree.nodes.iter().enumerate() {
        let edges = match node.kind {
            KIND_ACTION => node.num_children as usize,
            KIND_CHANCE => 52,
            _ => continue,
        };
        for edge in 0..edges {
            let child = spot.tree.children[node.children_start as usize + edge];
            if child == SENTINEL { continue; }
            let step = if node.kind == KIND_ACTION { PathStep::Action { index:edge } }
                else { PathStep::Card { card:solver::card_to_string(edge as u8) } };
            assert!(parent[child as usize].replace((id as u32, step)).is_none(),
                "control assumes one original-tree parent per node");
        }
    }
    parent
}

fn path_to(parent: &[Option<(u32, PathStep)>], mut id: u32) -> Vec<PathStep> {
    let mut path = Vec::new();
    while id != 0 {
        let (up, step) = parent[id as usize].as_ref().expect("reachable original-tree node");
        path.push(step.clone());
        id = *up;
    }
    path.reverse();
    path
}

fn coverage(s: &Solver) -> Coverage {
    let plan = GpuPlan::build(&s.spot, s.use_isomorphism);
    assert_eq!(plan.iso_active, s.use_isomorphism, "fixture must exercise compact isomorphism");
    let parent = parents(&s.spot);
    let mut eligible = [0usize; 2];
    let mut levels = Vec::new();
    let mut selected = None;
    for (level, span) in plan.action_spans.iter().enumerate() {
        let mut count = [0usize; 2];
        let mut ids = [u32::MAX; 2];
        if span.count >= ELIGIBLE_LEVEL_SIZE {
            for &id in &plan.action_nodes[span.start as usize..(span.start + span.count) as usize] {
                let node = &s.spot.tree.nodes[id as usize];
                if node.num_children == 3 {
                    let actor = node.player as usize;
                    count[actor] += 1;
                    ids[actor] = ids[actor].min(id);
                }
            }
            for p in 0..2 { eligible[p] += count[p]; }
        }
        levels.push(json!({"level":level,"action_count":span.count,"eligible_na3":count}));
        // Deepest common wide level: small query subtrees, both lock owners,
        // and at least one additional unlocked NA3 node of each actor.
        if count.iter().all(|&n| n > 1) {
            let paths = [path_to(&parent, ids[0]), path_to(&parent, ids[1])];
            if paths.iter().all(|path| path.iter().filter(|s| matches!(s, PathStep::Card { .. })).count() == 2) {
                selected = Some((level, ids, paths));
            }
        }
    }
    assert!(eligible.iter().all(|&n| n > 1), "fixture misses eligible NA3 for one actor: {levels:?}");
    let (level, ids, paths) = selected.expect("fixture requires both actors on one wide river level");
    for p in 0..2 {
        assert_eq!(serde_json::to_vec(&paths[p]).unwrap(), serde_json::to_vec(&s.canonical_path(&paths[p])).unwrap(),
            "selected path must address its active orbit representative");
        assert_ne!(plan.cfv_slot[ids[p] as usize], u32::MAX);
    }
    let evidence = json!({"minimum_level_actions":ELIGIBLE_LEVEL_SIZE,"iso_active":plan.iso_active,
        "eligible_by_actor":eligible,"levels":levels,"selected_level":level,"selected_ids":ids,"paths":paths});
    Coverage { ids, paths, evidence }
}

fn output_dir(name: &str) -> PathBuf {
    let root = PathBuf::from(std::env::var_os("POSTFLOP_DIRECT3_CONTROL_DIR")
        .expect("set POSTFLOP_DIRECT3_CONTROL_DIR to a unique evidence directory"));
    assert!(root.is_absolute(), "evidence directory must be absolute");
    std::fs::create_dir_all(&root).unwrap();
    let dir = root.join(name);
    std::fs::create_dir(&dir).expect("control output directory must not already exist");
    dir
}

fn emit(value: Value) {
    println!("METRIC_JSON {value}");
    std::io::stdout().flush().unwrap();
}

fn run_iterations(gpu: &mut GpuSolver, n: u32) {
    for _ in 0..n { gpu.iterate().unwrap(); }
}

fn lock_owner(s: &mut Solver, gpu: &mut GpuSolver, c: &Coverage, owner: usize) {
    s.ensure_symmetric();
    s.clear_locks();
    s.lock_node(&c.paths[owner], LockMode::Freeze, format!("direct3 owner {owner}")).unwrap();
    assert_eq!(s.locks.len(), 1);
    assert!(s.locks.contains_key(&c.ids[owner]), "API lock must land on the selected eligible node");
    gpu.update_locks(s).unwrap();
}

// Save one lock at a time: Header serializes HashMaps in iteration order, so
// multiple simultaneous locks would make raw saved-file hashes nondeterministic.
fn snapshot(s: &mut Solver, gpu: &mut GpuSolver, c: &Coverage, stage: &str, file: &Path) -> Value {
    gpu.sync_to_cpu(s).unwrap();
    assert_eq!(s.iteration, gpu.iteration);
    let raw = raw_state(s);
    let mut exploit_bits = Vec::new();
    for _ in 0..3 {
        let value = gpu.exploitability(s).unwrap();
        assert!(value.is_finite(), "nonfinite exploitability");
        exploit_bits.push(value.to_bits());
    }
    assert!(exploit_bits.windows(2).all(|pair| pair[0] == pair[1]), "eager/captured/replayed evaluation differs");
    let root_strategy_bits: Vec<u32> = s.average_strategy(0, &s.spot.tree.nodes[0]).iter().map(|v| v.to_bits()).collect();
    s.ensure_symmetric();
    let queries: Vec<Value> = c.paths.iter().map(|path| {
        let view = s.node_view(path).unwrap();
        json!({"path":path,"view_hash":hash_bytes(&serde_json::to_vec(&view).unwrap()),"view":view})
    }).collect();
    let materialized = raw_state(s);
    // Query materialization must not change authoritative device state; a full
    // download restores the compact inactive initial blocks exactly.
    gpu.sync_to_cpu(s).unwrap();
    assert_eq!(raw_state(s), raw, "full resync after queries changed raw arenas");
    s.save(file.to_str().unwrap()).unwrap();
    let mut locks: Vec<_> = s.locks.iter().map(|(&id, sigma)| {
        (id, sigma.iter().map(|v| v.to_bits()).collect::<Vec<_>>())
    }).collect();
    locks.sort_by_key(|(id, _)| *id);
    json!({"stage":stage,"iteration":s.iteration,"raw":raw,"materialized":materialized,
        "save_hash":hash_file(file),"save_bytes":std::fs::metadata(file).unwrap().len(),
        "exploit_bits":exploit_bits,"root_strategy_bits":root_strategy_bits,"locks":locks,"queries":queries})
}

#[test]
#[ignore = "manual serialized GPU wide-NA3 lock, graph and saved-resume controls"]
fn postflop_direct3_controls() {
    let dir = output_dir("graph-resume");
    let spot = fixture();
    for storage in [Storage::F32, Storage::Compressed] {
        for iso in [false, true] {
            for algo in [Algorithm::Dcfr, Algorithm::CfrPlus] {
                let case = format!("{storage:?}-iso{iso}-{algo:?}");
                let file = dir.join(format!("{case}.gto"));
                let mut s = Solver::with_storage(spot.clone(), storage);
                s.algo = algo;
                s.use_isomorphism = iso;
                let c = coverage(&s);
                emit(json!({"metrics":{},"event":"coverage","case":case,"coverage":c.evidence}));
                let mut gpu = GpuSolver::new(&s).unwrap();
                run_iterations(&mut gpu, 3); // eager, capture+launch, replay
                let mut states = vec![snapshot(&mut s, &mut gpu, &c, "ordinary", &file)];
                for owner in 0..2 {
                    lock_owner(&mut s, &mut gpu, &c, owner);
                    run_iterations(&mut gpu, 3); // invalidated graph capture + replay
                    states.push(snapshot(&mut s, &mut gpu, &c, &format!("locked_{owner}"), &file));
                    let iteration = s.iteration;
                    let lock_bits: Vec<u32> = s.locks[&c.ids[owner]].iter().map(|v| v.to_bits()).collect();
                    drop(gpu);
                    let mut loaded = Solver::load_with_storage(file.to_str().unwrap(), storage).unwrap();
                    // These two runtime choices are not saved by GTOSOLVE2.
                    loaded.algo = algo;
                    loaded.use_isomorphism = iso;
                    assert_eq!(loaded.iteration, iteration);
                    assert_eq!(loaded.locks.len(), 1);
                    assert_eq!(loaded.locks[&c.ids[owner]].iter().map(|v| v.to_bits()).collect::<Vec<_>>(), lock_bits);
                    assert_eq!(serde_json::to_value(&loaded.spot.config).unwrap(), serde_json::to_value(&spot.config).unwrap());
                    s = loaded;
                    states.push(json!({"stage":format!("loaded_{owner}"),"iteration":s.iteration,"raw":raw_state(&s)}));
                    gpu = GpuSolver::new(&s).unwrap();
                    run_iterations(&mut gpu, 3); // first resumed iteration captures immediately
                    states.push(snapshot(&mut s, &mut gpu, &c, &format!("resumed_{owner}"), &file));
                }
                s.clear_locks();
                gpu.update_locks(&s).unwrap();
                run_iterations(&mut gpu, 3);
                states.push(snapshot(&mut s, &mut gpu, &c, "unlocked", &file));
                emit(json!({"metrics":{},"event":"complete","case":case,"config":spot.config,
                    "storage":format!("{storage:?}"),"iso":iso,"algorithm":algo,"coverage":c.evidence,
                    "states":states,"scope":"exact supplemental correctness, no performance score"}));
            }
        }
    }
}

#[cfg(feature = "preflop-research")]
#[test]
#[ignore = "manual serialized wide-NA3 eager continuation coverage; no exploitability with custom reaches"]
fn postflop_direct3_continuation_control() {
    let dir = output_dir("continuation");
    let mut s = Solver::new(fixture());
    s.algo = Algorithm::CfrPlus;
    s.use_isomorphism = false;
    let c = coverage(&s);
    let reaches: [Vec<f32>; 2] = std::array::from_fn(|p| s.spot.weights[p].iter().enumerate()
        .map(|(i, &w)| w * (0.5 + ((i + 2 * p) % 5) as f32 * 0.125)).collect());
    let mut gpu = GpuSolver::new(&s).unwrap();
    let mut states = Vec::new();
    for phase in 0..3 {
        if phase > 0 { lock_owner(&mut s, &mut gpu, &c, phase - 1); }
        let mut roots = Vec::new();
        for t in (1 + phase as u32 * 3)..=(3 + phase as u32 * 3) {
            for p in 0..2 {
                let cfv = gpu.research_continuation_sweep(p, t, &reaches[p], &reaches[1 - p]).unwrap();
                assert!(cfv.iter().all(|v| v.is_finite()));
                roots.push(json!({"iteration":t,"traverser":p,"root_cfv_bits":cfv.iter().map(|v| v.to_bits()).collect::<Vec<_>>()}));
            }
        }
        gpu.sync_to_cpu(&mut s).unwrap();
        let file = dir.join(format!("phase-{phase}.gto"));
        s.save(file.to_str().unwrap()).unwrap();
        states.push(json!({"phase":phase,"iteration":s.iteration,"raw":raw_state(&s),"save_hash":hash_file(&file),"roots":roots}));
    }
    emit(json!({"metrics":{},"event":"complete","case":"continuation-f32-explicit-cfrplus",
        "config":s.spot.config,"coverage":c.evidence,"states":states,
        "scope":"shared eager continuation sweep; excludes storage swap and paging; no performance score"}));
}
