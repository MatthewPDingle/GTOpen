"""D110: freeze substage profile of accepted CPU GpuPlan construction."""
import sys,json,difflib,ast,shutil
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>66*1024**3
H=ROOT/'runs/D110-plan-stage-profile';H.mkdir();prior=ROOT/'runs/D099-plan-posting-scratch'
base=(old.REPO/'crates/solver/src/gpu/plan.rs').read_bytes();text=base.decode().replace('\r\n','\n')
extra='''thread_local! { static D110_TIMES: std::cell::Cell<[f64; 8]> = const { std::cell::Cell::new([0.0; 8]) }; }
pub fn d110_times() -> [f64; 8] { D110_TIMES.with(|v| v.get()) }
'''
marks=[('        let n = spot.tree.nodes.len();','        let d110_start = std::time::Instant::now();\n        let mut d110_times = [0.0; 8];\n'),('        // Terminal CFVs stay resident','        d110_times[0] = d110_start.elapsed().as_secs_f64() * 1000.0;\n'),('        // --- Level-ordered work lists','        d110_times[1] = d110_start.elapsed().as_secs_f64() * 1000.0;\n'),('        // --- River slot assignment','        d110_times[2] = d110_start.elapsed().as_secs_f64() * 1000.0;\n'),('        // --- Per-node scalar arrays','        d110_times[3] = d110_start.elapsed().as_secs_f64() * 1000.0;\n'),('        // --- Per-hand arrays','        d110_times[4] = d110_start.elapsed().as_secs_f64() * 1000.0;\n'),('        // Node IDs describe ownership','        d110_times[5] = d110_start.elapsed().as_secs_f64() * 1000.0;\n'),('        GpuPlan {','        d110_times[6] = d110_start.elapsed().as_secs_f64() * 1000.0;\n        D110_TIMES.with(|v| v.set(d110_times));\n')]
profile=text
for marker,insert in marks:
 assert profile.count(marker)==1,marker
 profile=profile.replace(marker,insert+marker)
profile=profile.replace('impl GpuPlan {',extra+'impl GpuPlan {',1)
undo=profile.replace(extra,'',1)
for marker,insert in reversed(marks):assert undo.count(insert)==1;undo=undo.replace(insert,'',1)
assert undo==text
(H/'accepted-plan.rs').write_bytes(base);(H/'profiled-plan.rs').write_text(profile,encoding='utf-8',newline='\n')
(H/'profile.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),profile.splitlines(True),fromfile='accepted-E051/plan.rs',tofile='D110/profiled-plan.rs')),encoding='utf-8',newline='')
for n in ['game.rs','field-schema.json','fixture-0.json','fixture-1.json','fixture-2.json']:(H/n).write_bytes((prior/n).read_bytes())
assert (H/'game.rs').read_bytes()==(old.REPO/'crates/solver/src/game.rs').read_bytes()
probe=(prior/'probe-r2.rs').read_text().replace('candidate-plan.rs','profiled-plan.rs').replace('D099','D110')
a=probe.index('let mut baseline_samples=');b=probe.index('let a=a.unwrap();let b=b.unwrap();',a)
replacement=r'''let mut baseline_samples=Vec::new();let mut profile_samples=Vec::new();let mut stages=Vec::new();
let orders=[false,true,false];
// Exactly one warmup pair; no measurements pooled with previous diagnostics.
for arm in [false,true] { if arm { let mut p=candidate::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}std::hint::black_box(&p);drop(p); } else {let mut p=accepted::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}std::hint::black_box(&p);drop(p);} }
for &profile_first in &orders {for arm in [profile_first,!profile_first] {
 let t=Instant::now();
 if arm {let mut p=candidate::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}let ms=t.elapsed().as_secs_f64()*1000.0;std::hint::black_box(&p);let cumulative=candidate::d110_times();let mut spans=Vec::new();let mut last=0.0;for &v in &cumulative[..7]{assert!(v>=last);spans.push(v-last);last=v;}assert!(ms>=last);spans.push(ms-last);stages.push(spans);profile_samples.push(ms);drop(p);}
 else {let mut p=accepted::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}let ms=t.elapsed().as_secs_f64()*1000.0;std::hint::black_box(&p);baseline_samples.push(ms);drop(p);}
}}
fn median(x:&[f64])->f64{let mut v=x.to_vec();v.sort_by(f64::total_cmp);v[v.len()/2]}
ams=median(&baseline_samples);bms=median(&profile_samples);
// Exactly one additional untimed full plan pair for raw field/capacity controls.
let mut pa=accepted::GpuPlan::build(&spot,iso);if full{pa.use_full_action_arenas(&spot);}a=Some(pa);
let mut pb=candidate::GpuPlan::build(&spot,iso);if full{pb.use_full_action_arenas(&spot);}b=Some(pb);
'''
probe=probe[:a]+replacement+probe[b:]
a=probe.index('// Separate untimed allocator-mechanism audit');b=probe.index('let v=serde_json::json!(',a);probe=probe[:a]+probe[b:]
probe=probe.replace('"candidate_plan_ms":bms','"profile_plan_ms":bms').replace('"candidate_samples_ms":candidate_samples','"profile_samples_ms":profile_samples,"stage_spans_ms":stages')
probe=probe.replace('"warmup_pairs":2,"measured_pairs":9,"posting_mechanism":mechanism','"warmup_pairs":1,"measured_pairs":3')
assert 'candidate_samples' not in probe and 'mechanism' not in probe and 'stages.push' in probe
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
command=old.read(prior/'protocol-r2.json')['command'];command=[str(H/'probe.rs') if x==str(prior/'probe-r2.rs') else ('d110_probe' if x=='d099_probe' else (str(H/'build/probe.exe') if x==str(prior/'build/probe.exe') else x)) for x in command]
inputs={str(p):old.sha(p) for p in H.iterdir() if p.is_file()}
for p,h in old.read(prior/'protocol-r2.json')['input_sha256'].items():
 if '\\build-e051-final-primary\\' in p:old.pin(p,h);inputs[p]=h
for p in [Path(__file__),old.REPO/'crates/solver/src/gpu/plan.rs',old.REPO/'crates/solver/src/game.rs',prior/'probe-r2.rs',prior/'protocol-r2.json']:inputs[str(p)]=old.sha(p)
p={'id':'D110','at':old.now(),'status':'frozen_before_compile_native','command':command,'cases':list(range(12)),'timed_pair_order':['baseline/profile','profile/baseline','baseline/profile'],'warmup_pairs':1,'extra_untimed_raw_pairs':1,'stage_names':['allocation_and_representative_DFS','CFV_slot_assignment','level_worklists','river_slots_and_flat_tables','node_scalars_and_arena_offsets','hand_and_permutation_arrays','dense_reach_slots','final_struct_full_arena_override_and_return'],'input_sha256':inputs,'source_math_statements_reversible_exact':True,'accepted_source':old.BASE,'observer_rule':'Per case absolute median profile-baseline difference <=max(10 percent of baseline median,0.05ms). No exclusions/extensions/optimizer/gain inference if fails.','correctness_rule':'All53fieldvalues/f32bits/nestedVec lengths and capacities and struct size equal, full raw files retained; root replay. Diagnostic only, not full solver state.','scope':'CPU-only component, same held Spot per process, warmed allocation; not actual full GPU initialization/app teardown or complete-solve/cold performance. No solver/learning arenas/context/kernels/native GPU work.','new_candidate':False,'reserve_free_bytes':66*1024**3,'expected_max_raw_bytes':6*1024**3}
old.save(H/'protocol.json',p)
print(json.dumps({'directory':str(H),'protocol_sha256':old.sha(H/'protocol.json'),'source_sha256':old.sha(H/'profiled-plan.rs'),'free_GiB':shutil.disk_usage(ROOT).free/1024**3,'cases':12}),flush=True)