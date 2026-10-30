"""Prepare isolated immutable holdout inputs only; never build or execute CUDA."""
from pathlib import Path
import ast, difflib, hashlib, json, re, subprocess

HERE=Path(__file__).resolve().parent
RAW=HERE.parent.parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
PLAN=RAW/'runs/E020-wide-turn-holdout-plan'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,data):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(data if isinstance(data,bytes) else data.encode())
def save(name,value):put(name,json.dumps(value,indent=2,allow_nan=False)+'\n')
assert sha(PLAN/'manifest.json')=='5396d60a0cf14b51ed91c4f53de574db5d8c9d6d065ed43e34594338f33d823a'
assert sha(PLAN/'protocol.json')=='33d4a047f67d1b23bd125cbfc8c31b564b6cf6a8417da768023beb8389c71510'
for name in ['fixture.json','protocol.json','manifest.json','frozen-primary.rs','source-derived-bounds.json']:
    put('plan-'+name,(PLAN/name).read_bytes())
put('fixture.json',(PLAN/'fixture.json').read_bytes())
for role in ['E015','E020']:
    put(role+'-kernels.cu',(PLAN/(role+'-kernels.cu')).read_bytes())

base=(PLAN/'frozen-primary.rs').read_text(encoding='utf-8')
src=base.replace('fn postflop_complete_cycle()', 'fn postflop_wide_turn_holdout()')
src=src.replace('const FIXTURES: [(&str, &str, f64); 3] = [\n    ("rainbow", "Ks7h2d", 0.0),\n    ("two-tone", "Ks7s2d", 0.05),\n    ("river", "Ks7h2dQhTc", 0.05),\n];',
                'const FIXTURES: [(&str, &str, f64); 1] = [("wide-turn-full169", "Ks7h2dQh", 0.05)];')
assert 'const FIXTURES: [(&str, &str, f64); 1]' in src
start=src.index('    let filter = std::env::var(')
end=src.index('    emit_stage(json!({',start)
src=src[:start]+'''    let filter: Option<String> = None;
    let storage = Storage::Compressed;
    let storage_name = "compressed";
    let profile = false;
    let state_path = std::env::var_os("POSTFLOP_HOLDOUT_STATE").expect("unique raw state path required");
    for variable in ["POSTFLOP_AUTORESEARCH_FIXTURE", "POSTFLOP_AUTORESEARCH_STORAGE", "POSTFLOP_AUTORESEARCH_PROFILE"] {
        assert!(std::env::var_os(variable).is_none(), "holdout rejects primary overrides");
    }
'''+src[end:]
src=src.replace('include_str!("../../../bench_spot.json")','include_str!("fixture.json")')
old='        let mut host = Solver::with_storage(Arc::new(Spot::new(config).unwrap()), storage);'
new='''        let spot = Spot::new_with_limit(config, Some(20_000)).unwrap();
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
        let mut host = Solver::with_storage(Arc::new(spot), storage);'''
assert src.count(old)==1;src=src.replace(old,new)
src=src.replace('GpuSolver::new(&host).expect("benchmark requires CUDA")','GpuSolver::new_with_budget(&host, 2 * 1024u64.pow(3)).expect("holdout requires admitted CUDA")')
start=src.index('        if profile {')
end=src.index('        completed += 1;',start)
src=src[:start]+'''        let raw = write_raw_state(&host, exploit, std::path::Path::new(&state_path));
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
'''+src[end:]
src=src.replace('use solver::gpu::{GpuSolver, KERNEL_NAMES};','use solver::gpu::GpuSolver;')
src=src.replace('"primary_suite": filter.is_none() && storage == Storage::Compressed','"primary_suite": false, "wide_holdout": true')
src=src.replace('"initialization_note": "fixed fixture order; first GPU initialization includes runtime NVRTC/JIT work; device compiler/module caches may be warm after the first fixture"',
    '"initialization_note": "one fresh wide-turn process; runtime NVRTC/JIT included; persistent driver cache retained without reset or selective warmup"')
src=src.replace('//! Complete postflop CUDA lifecycle benchmark for the 2026-10-16 research pass.',
    '//! Fixed E020 wide-turn holdout; derivative of the sealed complete-cycle evaluator.')
helper='''
// Exact framed store bytes; this is after total_ms and fingerprinting.
// No dequantization, materialization, query mutation or unbounded temporary copy.
fn write_raw_state(solver: &Solver, exploit: f64, path: &std::path::Path) -> u64 {
    let file = std::fs::OpenOptions::new().write(true).create_new(true).open(path).unwrap();
    let mut out = std::io::BufWriter::with_capacity(1024 * 1024, file);
    out.write_all(b"GTO-WIDE-RAW-v1\\0").unwrap();
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
'''
src=src.replace('#[test]\n#[ignore',helper+'\n#[test]\n#[ignore',1)
src=src.replace('#[ignore = "manual complete-cycle postflop CUDA performance and state fingerprints"]',
                '#[ignore = "manual frozen wide-turn holdout; serialized root runner only"]')
src='''//! Frozen E020 wide-turn holdout, separate from the primary evaluator.
//! Uses only adjacent fixture.json, DCFR/compressed/iso, target0.3% every20, max400.
//! Primary fixture/storage/profile environment overrides are rejected.
//! POSTFLOP_HOLDOUT_STATE must name a unique per-run raw CPU-store output file.
//! Full q/scale words are exported after timing; no profiling or duplicate plan.
'''+src[src.index('#![cfg(feature'):]
# Strong mechanical identities for reused math/state/timing logic.
helper_start=base.index('// Stream every byte')
helper_end=base.index('\n#[test]',helper_start)
assert base[helper_start:helper_end] in src
loop_start=base.index('        let solve_start = Instant::now();')
loop_end=base.index('        // The score stops above.',loop_start)
assert base[loop_start:loop_end] in src
assert 'iterate_profiled' not in src and 'GpuPlan::build' not in src
put('evaluator.rs',src)
put('evaluator.patch',''.join(difflib.unified_diff(base.splitlines(True),src.splitlines(True),fromfile='frozen-primary.rs',tofile='evaluator.rs')))
save('mechanical-checks.json',{'primary_helpers_byte_identical':True,'solve_readback_timing_body_byte_identical':True,
 'no_profile_or_duplicate_plan':True,'primary_source_sha256':sha(PLAN/'frozen-primary.rs'),
 'evaluator_sha256':sha(HERE/'evaluator.rs'),'executed_tests':0,'gpu_jobs':0})

after=json.loads((RAW/'binaries/E020-postflop_autoresearch.manifest.json').read_text(encoding='utf-8'))['source_sha256']
before=json.loads((RAW/'binaries/E015-postflop_autoresearch.manifest.json').read_text(encoding='utf-8'))['source_sha256']
owned={'crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/kernels.cu'}
assert set(before)==set(after) and {n for n in after if before[n]!=after[n]}==owned
for name,h in after.items():assert sha(REPO/name)==h,name
tracked=subprocess.check_output(['git','ls-files','crates/solver','crates/server'],cwd=REPO,text=True,encoding='utf-8').splitlines()
files=set(tracked)|set(after)|{'cache/contextual/ignition-nl10-reraise-v1.json',
 'research/preflop-evolution/behavior/pass3/evidence-metadata.json','research/ignition-reraise/examples.json'}
files={name for name in files if (REPO/name).is_file()}
assert all('/target/' not in n and not n.startswith('target/') for n in files)
maps={}
append='\n[[test]]\nname = "postflop_wide_turn_holdout"\npath = "../../../../evaluator.rs"\n\n[[test]]\nname = "postflop_wide_turn_resources"\npath = "../../../../resource.rs"\n'
for role in ['E015','E020']:
    mapping={}
    for name in sorted(files):
        data=(REPO/name).read_bytes()
        if role=='E015' and name in owned:
            data=(PLAN/('E015-'+Path(name).name)).read_bytes()
        original=hashlib.sha256(data).hexdigest()
        if name in before:assert original==(before if role=='E015' else after)[name]
        if name=='crates/solver/Cargo.toml':data+=append.encode()
        out=f'workspaces/{role}/{name}';put(out,data)
        mapping[name]={'copied_sha256':hashlib.sha256(data).hexdigest(),'production_sha256':original,
                       'manifest_test_target_append_only':name=='crates/solver/Cargo.toml'}
    maps[role]=mapping
save('workspace-source-maps.json',maps)
save('protected-checkout.json',after)
put('runner-primitives-source.py',(RAW/'runs/D037-showdown-cache-resource/runner-primitives-source.py').read_bytes())
save('input-identities.json',{'primary_protocol_sha256':sha(PLAN/'protocol.json'),
 'primary_plan_manifest_sha256':sha(PLAN/'manifest.json'),
 'E015_primary_build_manifest_sha256':sha(RAW/'binaries/E015-postflop_autoresearch.manifest.json'),
 'E020_primary_build_manifest_sha256':sha(RAW/'binaries/E020-postflop_autoresearch.manifest.json'),
 'source_map_difference_exactly':sorted(owned),'copied_files_per_workspace':len(files)})
print(json.dumps({'prepared':str(HERE),'source_files_per_workspace':len(files),'evaluator_sha256':sha(HERE/'evaluator.rs')}))
