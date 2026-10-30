"""One CPU-only direct-initialization planner screen, with complete metadata proof."""
from pathlib import Path
import ast,difflib,json,re,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not (R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
H=R/'runs/D123-node-array-initialization';assert not H.exists();H.mkdir();A=R/'runs/D092-action-arity-order';previous=R/'runs/E076-plan-control'
name='crates/solver/src/gpu/plan.rs';original=(old.REPO/name).read_text(encoding='utf-8');old.pin(old.REPO/name,old.BASE[name])
candidate=original
declarations={'node_player':'0i32','node_na':'0i32','node_data_off':'u64::MAX','node_children_start':'0u32','node_twin':'0f32','node_tlose':'0f32','node_ttie':'0f32','node_cdiv':'0f32'}
types={'node_player':'i32','node_na':'i32','node_data_off':'u64','node_children_start':'u32','node_twin':'f32','node_tlose':'f32','node_ttie':'f32','node_cdiv':'f32'}
for field,value in declarations.items():
 oldline=f'let mut {field} = vec![{value}; n];';assert candidate.count(oldline)==1
 candidate=candidate.replace(oldline,f'let mut {field} = Vec::<{types[field]}>::with_capacity(n);')
for field,expr in [('node_player','node.player as i32'),('node_na','node.num_children as i32'),('node_children_start','node.children_start'),('node_twin','node.t_win as f32'),('node_tlose','node.t_lose as f32'),('node_ttie','node.t_tie as f32')]:
 oldline=f'{field}[ni] = {expr};';assert candidate.count(oldline)==1;candidate=candidate.replace(oldline,f'{field}.push({expr});')
oldoff='''            if node.kind == KIND_ACTION && reached[ni] {
                let p = node.player as usize;
                node_data_off[ni] = arena_elements[p] as u64;
                arena_elements[p] += node.num_children as usize * nh[p];
            }'''
newoff='''            let off = if node.kind == KIND_ACTION && reached[ni] {
                let p = node.player as usize;
                let off = arena_elements[p] as u64;
                arena_elements[p] += node.num_children as usize * nh[p];
                off
            } else { u64::MAX };
            node_data_off.push(off);'''
assert candidate.count(oldoff)==1;candidate=candidate.replace(oldoff,newoff)
olddiv='''            if node.kind == KIND_CHANCE {
                node_cdiv[ni] = 1.0 / (46 - node.street as i32) as f32;
            }'''
newdiv='''            node_cdiv.push(if node.kind == KIND_CHANCE {
                1.0 / (46 - node.street as i32) as f32
            } else { 0.0 });'''
assert candidate.count(olddiv)==1;candidate=candidate.replace(olddiv,newdiv)
start=original.index('        // --- Per-node scalar arrays');end=original.index('        // Packing adds host copy/restore work.',start)
assert candidate[:start]==original[:start]and candidate[candidate.index('        // Packing adds host copy/restore work.'):]==original[end:]
assert 'unsafe'not in candidate[start:candidate.index('        // Packing adds host copy/restore work.')]
(H/'accepted-plan.rs').write_text(original,encoding='utf-8',newline='\n');old.pin(H/'accepted-plan.rs',old.BASE[name])
(H/'candidate-plan.rs').write_text(candidate,encoding='utf-8',newline='\n')
(H/'candidate.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),candidate.splitlines(True),fromfile=name,tofile=name)),encoding='utf-8',newline='\n')
history=subprocess.run(['git','log','--all','--format=%H','-G','spare_capacity|node_player.*with_capacity|node_twin.*with_capacity|MaybeUninit','--',name],cwd=old.REPO,text=True,capture_output=True,check=True);assert not history.stdout.strip()
old.save(H/'source-review.json',{'id':'D123','at':old.now(),'scope':'Eight serial per-node scalar vectors only: reserve exact n and append each final value in original ascending node order. No unsafe/uninitialized read, field/schema/layout change, parallelism, SIMD helper, CFV alias, worklist reordering, zero-scan omission, encoder, CUDA or solve-quality change.','baseline_sha256':old.sha(H/'accepted-plan.rs'),'candidate_sha256':old.sha(H/'candidate-plan.rs'),'fully_initialized_fields':list(declarations),'reasoning':'Each loop visits exactly n nodes once, each reserved vector receives exactly one push on every iteration, all conditional offset/cdiv branches yield the original sentinel or positive-zero value, all float cast/divide expressions and serial per-player arena offsets stay ordered. Full raw53-field/capacity/struct and original-anchor controls are still required.','local_all_ref_query':history.args,'local_all_ref_matches':history.stdout.splitlines(),'distinct_from_closed_forms':'E071 parallel joined planner branches, E076 CFV lifetime/row layout, E065 subtree replication, D107 Store/ArenaBuf zero allocation, D090 wide OR, E049 zero provenance and encoder/readback variants remain closed. No timing rescue or historical samples pooled.','limits':'Bounded local novelty and source reasoning. Source initialization syntax does not prove allocator internal cost, emitted dead fills, CPU speed, material footprint or complete-solve improvement.'})
for n in ['game.rs','fixture-0.json','fixture-1.json','fixture-2.json','field-schema.json']:shutil.copyfile(A/n,H/n)
old.pin(H/'game.rs',old.BASE['crates/solver/src/game.rs'])
probe=(previous/'probe.rs').read_text(encoding='utf-8').replace('E076','D123')
probe=probe.replace('use std::{fs::{File,OpenOptions},io::{BufWriter,Write}};','use std::{fs::{File,OpenOptions},io::{BufWriter,Write},time::Instant};')
begin=probe.index('let(mut a,mut b) = if id%2==0');finish=probe.index('let mut f=BufWriter',begin)
builds=r'''for _ in 0..2 {
 let mut a=accepted::GpuPlan::build(&spot,iso);if full {a.use_full_action_arenas(&spot);}std::hint::black_box(&a);drop(a);
 let mut b=candidate::GpuPlan::build(&spot,iso);if full {b.use_full_action_arenas(&spot);}std::hint::black_box(&b);drop(b);
}
let mut measured=Vec::new();
for pair in 0..9 {
 let mut times=[0.0;2];let first=(id+pair)%2;
 for arm in [first,1-first] {
  if arm==0 {let t=Instant::now();let mut p=accepted::GpuPlan::build(&spot,iso);if full {p.use_full_action_arenas(&spot);}times[0]=t.elapsed().as_secs_f64()*1000.0;std::hint::black_box(&p);drop(p);}
  else {let t=Instant::now();let mut p=candidate::GpuPlan::build(&spot,iso);if full {p.use_full_action_arenas(&spot);}times[1]=t.elapsed().as_secs_f64()*1000.0;std::hint::black_box(&p);drop(p);}
 }
 measured.push(serde_json::json!({"pair":pair,"first":if first==0 {"baseline"}else{"candidate"},"baseline_ms":times[0],"candidate_ms":times[1]}));
}
let mut a=accepted::GpuPlan::build(&spot,iso);let mut b=candidate::GpuPlan::build(&spot,iso);
if full {a.use_full_action_arenas(&spot);b.use_full_action_arenas(&spot);}
'''
probe=probe[:begin]+builds+probe[finish:]
probe=probe.replace('"all_non_CFV_fields_bitwise_equal":true','"all53_fields_bitwise_equal":true,"measured_pairs":measured')
probe=probe.replace('"first":if id%2==1{"candidate"}else{"baseline"}','"raw_pair_first":"baseline"')
for field in [36,37]:
 line=next(l for l in probe.splitlines()if l.startswith(f'count+=field(&mut f,{field},'))
 assert line.endswith(',true);');probe=probe.replace(line,line[:-7]+',false);')
assert 'else1'not in probe and 'all53_fields_bitwise_equal'in probe
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
replay=r'''"""Full raw53-field/capacity/struct equality, independently matched to accepted data."""
from pathlib import Path
import array,struct
def vec(f):
 n,=struct.unpack('<Q',f.read(8));assert n<100000000
 v=array.array('Q');v.fromfile(f,n);assert len(v)==n;return v
def replay(path,case,reference):
 checks=0;words=0
 with Path(path).open('rb')as f,Path(reference).open('rb')as r:
  assert f.read(16)==b'D123-PLAN-RAW1\0\0'and r.read(16)==b'D092-PLAN-RAW1\0\0'
  assert f.read(8)==r.read(8)==struct.pack('<II',case,53)
  sizes=f.read(16);assert sizes==r.read(16)and sizes[:8]==sizes[8:];checks+=4
  for field in range(53):
   assert f.read(4)==r.read(4)==struct.pack('<I',field)
   ac,bc,av,bv=[vec(f)for _ in range(4)];rc1,rc2,rv1,rv2=[vec(r)for _ in range(4)]
   assert ac==bc==rc1==rc2 and av==bv==rv1;checks+=4;words+=len(av)
  for _ in range(2):assert vec(f)==vec(r);checks+=1
  assert f.read(1)==r.read(1)==b'';checks+=1
 return {'case':case,'fields':53,'all_values_capacities_structs_exact':True,'baseline_matches_retained_accepted_metadata':True,'baseline_words':words,'root_checks':checks,'raw_bytes':Path(path).stat().st_size}
'''
ast.parse(replay);(H/'replay.py').write_text(replay,encoding='utf-8',newline='\n')
execute=r'''"""One fixed CPU-only compiler/test/cohort; no variant, extension or GPU execution."""
from pathlib import Path
import json,shutil,statistics,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from replay import replay
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
 B=H/'build';E=H/'execution';assert not B.exists()and not E.exists();B.mkdir();E.mkdir()
 for label,cmd in P['compile_commands'].items():old.child(cmd,B,label,old.env(),600);verify()
 old.child([str(B/'tests.exe'),'--test-threads=1'],E,'unit',old.env(),300);verify()
 assert 'test result: ok. 2 passed;'in (E/'unit.stdout.log').read_text(encoding='utf-8')
 results=[];binary=old.sha(B/'probe.exe')
 for case in range(12):
  verify();old.ar.refuse_active(old.ar.live_status());old.pin(B/'probe.exe',binary)
  label=f'case-{case:02d}';raw=E/(label+'.bin');old.child([str(B/'probe.exe'),str(case),str(raw)],E,label,old.env(),240);verify()
  r=replay(raw,case,P['references'][case]['path']);r['raw_sha256']=old.sha(raw)
  markers=[json.loads(x.split('D123 ',1)[1])for x in (E/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines()if x.startswith('D123 ')]
  assert len(markers)==1;m=markers[0];assert m['id']==case and m['all53_fields_bitwise_equal']and m['all_vec_capacities_equal']and m['struct_size_equal']
  times=m['measured_pairs'];assert len(times)==9
  for i,t in enumerate(times):assert t['pair']==i and t['first']==('candidate'if(case+i)%2 else'baseline')and t['baseline_ms']>0 and t['candidate_ms']>0
  r.update(board=m['board'],iso_requested=m['iso_requested'],iso_active=m['iso_active'],full_arenas=m['full_arenas'],nodes=m['nodes'],measured_pairs=times,baseline_median_ms=statistics.median(t['baseline_ms']for t in times),candidate_median_ms=statistics.median(t['candidate_ms']for t in times),median_paired_saving_ms=statistics.median(t['baseline_ms']-t['candidate_ms']for t in times))
  r['saving_of_medians_ms']=r['baseline_median_ms']-r['candidate_median_ms'];results.append(r);old.save(E/(label+'.replay.json'),r)
  print(json.dumps({k:r[k]for k in ['case','board','iso_active','full_arenas','baseline_median_ms','candidate_median_ms','saving_of_medians_ms','median_paired_saving_ms']}),flush=True)
 canonical=[results[i]for i in [2,6,10]];saving=sum(c['saving_of_medians_ms']for c in canonical)
 admit=saving>=P['component_admission']['minimum_sum_canonical_saving_ms']and all(c['saving_of_medians_ms']>=0 and c['median_paired_saving_ms']>=0 for c in canonical)
 report={'id':'D123','at':old.now(),'status':'admit_one_integrated_trial_component_screen_only'if admit else'decline_CPU_component_saving_budget_not_met','protocol_sha256':sys.argv[1],'binary_sha256':binary,'cases':results,'canonical_case_ids':[2,6,10],'canonical_sum_CPU_plan_saving_ms':saving,'required_component_saving_ms':P['component_admission']['minimum_sum_canonical_saving_ms'],'admit_one_integrated_trial':admit,'original_and_candidate_plan_tests_pass':True,'all53_values_capacities_structs_match_retained_accepted':True,'all12_fixed_CPU_processes_completed':True,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'GPU_or_solver_executions':0,'complete_solve_performance_measured':False,'candidate_accepted':False,'excluded_samples':[],'extension_runs':0,'limits':'CPU planner component screen only. Predetermined saving budget is a screening heuristic, not a hardware/headroom bound, necessary condition, causal attribution, accepted speedup or complete-solve qualification. No allocator physical/temporary/driver peak or native GPU evidence. Fixed9 pairs per each12 cases retained. No source/layout/initialization/helper/threshold variants or extra samples after a failed control or component gate.'};old.save(H/'report.json',report);verify()
print(json.dumps({k:report[k]for k in ['status','canonical_sum_CPU_plan_saving_ms','required_component_saving_ms','admit_one_integrated_trial']}),flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
P0=old.read(previous/'protocol-r2.json');command=[x.replace(str(previous),str(H)).replace('e076_plan_probe','d123_plan_probe')for x in P0['compile_commands']['rustc']]
testcmd=command.copy();testcmd[testcmd.index('-o')+1]=str(H/'build/tests.exe');testcmd.insert(1,'--test')
deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
for p,h in deps.items():old.pin(p,h)
references=[{'case':i,'path':str(A/'execution'/f'case-{i:02d}.bin'),'sha256':old.read(A/'report.json')['cases'][i]['raw_sha256']}for i in range(12)]
paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],A/'protocol.json',A/'report.json',R/'runs/E076-initial-closure/decision.json',C/'common_e051_live.py',C/'protected-main.json',C/'preexisting-target-artifacts.json',*[Path(x['path'])for x in references]]
P={'id':'D123','at':old.now(),'status':'FROZEN_PRE_COMPILER_NATIVE','compile_commands':{'rustc':command,'rustc-tests':testcmd},'input_sha256':deps|{str(p):old.sha(p)for p in paths},'references':references,'component_admission':{'canonical_cases':[2,6,10],'minimum_sum_canonical_saving_ms':95.825124,'reference':'Fixed prospective screening budget:1% of the preserved9582.5124ms E051 cumulative suite. Historical timing is a budgeting constant only, never pooled as a new control or score.','guard':'Require both saving-of-medians and median paired savings >=0 in every canonical fixture. No epsilon.','limits':'Passing only admits one future integrated full-cycle test. Failing closes this exact safe direct-append initialization form; no native repeats/source/helper/initialization/threshold variants or sample extensions.'},'fixed_protocol':'One probe compiler, one test compiler, one two-test CPU plan invariant process; exactly12 native CPU-only fixture/iso/full cases, each2 warmup pairs +9 alternating measured pairs +1 untimed full raw53-field pair. All raw values/capacities/structs must match accepted D092 data, not just summaries. No production activation, CUDA/GPU kernels or solver/full-cycle timing.','candidate_accepted':False};old.save(H/'protocol.json',P)
pub=[]
for p in H.iterdir():
 if not p.is_file():continue
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified_artifacts':pub,'compiler_or_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='D123'for x in s['experiments']);s['experiments'].append({'id':'D123','at':old.now(),'title':'Directly build planner metadata arrays without clearing then overwriting','kind':'diagnostic','status':'running','correctness':'Frozen CPU full-metadata controls','fixture':'12 CPU fixture/iso/full cases','stage':'CPU-only planner component screen','reason':'Eight exact-capacity vectors append final values in original node order, using safe Rust. No CUDA, math, schema, field or layout change. Check every field and fixed CPU saving budget before considering an integrated trial.','accepted':False,'evidence':[{'label':'Source scope and novelty review','url':'evidence/D123-node-array-initialization/source-review.json'},{'label':'Frozen full metadata and CPU component screen','url':'evidence/D123-node-array-initialization/protocol.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D123',stage='D123 CPU metadata initialization screen',activity='E076 closed after exactness passed but0.5219% aggregate slowdown. New safe serial metadata initialization form: full53-field equality and fixed CPU-only component screen. No GPU/new complete-cycle speed result; accepted/live E051 gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'candidate_sha256':old.sha(H/'candidate-plan.rs'),'compiler_or_native_executions':0}),flush=True)
