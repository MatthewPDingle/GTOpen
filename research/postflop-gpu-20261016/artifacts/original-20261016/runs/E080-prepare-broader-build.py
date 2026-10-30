"""Freeze exact broader harnesses and a large warm compressed constructor control."""
from pathlib import Path
import ast,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=106*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
Q=R/'comparisons/E080-fresh16-confirmation/report.json';X=R/'comparisons/E080-fresh16-root-check/report.json';assert old.read(Q)['status']=='pass_fresh16_timing_only'and old.read(X)['status']=='pass_timing_only'
H=R/'runs/E080-broader-build-plan';assert not H.exists();H.mkdir()
shutil.copyfile(R/'runs/D131-zero-check-setup-overlap/fixture-1.json',H/'warm-fixture.json')
warm=r'''use solver::{Solver,Spot,SpotConfig,PathStep};
use solver::{gpu::{GpuSolver,plan::GpuPlan},store::{Store,Storage}};
use std::{sync::Arc,path::Path,io::{Write,BufWriter},fs::OpenOptions};
use serde_json::{json,Value};
fn emit(value:Value){let mut f=std::io::stdout().lock();writeln!(f,"E080_WARM {value}").unwrap();f.flush().unwrap();}
fn q_bytes(s:&Solver)->usize{s.regrets.iter().chain(&s.strat).map(|store|match store{Store::I16{q,..}|Store::U16{q,..}=>q.len()*2,Store::F32(_)=>0}).sum()}
fn raw(s:&Solver,out:&Path,stage:&str)->Value{
 let path=out.join(format!("{stage}.bin"));let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(&path).unwrap());
 f.write_all(b"E080-WARM-RAW1\0\0").unwrap();f.write_all(&s.iteration.to_le_bytes()).unwrap();f.write_all(&4u32.to_le_bytes()).unwrap();let mut stores=Vec::new();
 for store in s.regrets.iter().chain(&s.strat){
  let(tag,n,scale)=match store{Store::I16{q,scale}=>(1u32,q.len(),scale.as_slice()),Store::U16{q,scale}=>(2,q.len(),scale.as_slice()),Store::F32(_)=>panic!("compressed control required")};
  f.write_all(&tag.to_le_bytes()).unwrap();f.write_all(&(n as u64).to_le_bytes()).unwrap();f.write_all(&(scale.len()as u64).to_le_bytes()).unwrap();
  match store{Store::I16{q,..}=>for c in q.as_slice().chunks(8192){let b:Vec<u8>=c.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();},Store::U16{q,..}=>for c in q.as_slice().chunks(8192){let b:Vec<u8>=c.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();},_=>unreachable!()}
  for c in scale.chunks(8192){let b:Vec<u8>=c.iter().flat_map(|x|x.to_bits().to_le_bytes()).collect();f.write_all(&b).unwrap();}
  stores.push(json!({"tag":tag,"q_len":n,"scale_len":scale.len(),"nonzero_scale_words":scale.iter().filter(|x|x.to_bits()!=0).count()}));
 }
 f.flush().unwrap();f.get_ref().sync_all().unwrap();let bytes=f.get_ref().metadata().unwrap().len();
 json!({"stage":stage,"iteration":s.iteration,"stores":stores,"raw_bytes":bytes,"raw_file":path})
}
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);let out=Path::new(&args[1]);std::fs::create_dir(out).unwrap();
 let cfg:SpotConfig=serde_json::from_str(include_str!("warm-fixture.json")).unwrap();let mut s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),Storage::Compressed);s.use_isomorphism=false;
 let bytes=q_bytes(&s);assert!(bytes>=64*1024*1024);assert_eq!(bytes,1369522280);let mut g=GpuSolver::new(&s).unwrap();for _ in 0..3{g.iterate().unwrap();}g.sync_to_cpu(&mut s).unwrap();drop(g);
 s.use_isomorphism=true;let first=raw(&s,out,"warm_full");assert!(first["stores"].as_array().unwrap().iter().all(|x|x["nonzero_scale_words"].as_u64().unwrap()>0));emit(first);
 let plan=GpuPlan::build(&s.spot,true);let budget=plan.staging_bytes()+(plan.arena_elements[0]+plan.arena_elements[1])as u64*8+512*1024*1024;assert!(GpuSolver::new_with_budget(&s,budget-1).is_err());
 let mut g=GpuSolver::new_with_budget(&s,budget).unwrap();g.sync_to_cpu(&mut s).unwrap();emit(raw(&s,out,"compact_initial_sync"));for _ in 0..2{g.iterate().unwrap();}g.sync_to_cpu(&mut s).unwrap();emit(raw(&s,out,"compact_trained"));
 s.ensure_symmetric();let query=s.node_view(&[] as &[PathStep]).unwrap();emit(json!({"stage":"root_query","value":serde_json::to_value(query).unwrap()}));g.sync_strategy(&mut s).unwrap();g.sync_to_cpu(&mut s).unwrap();emit(raw(&s,out,"materialized_resync"));
 let save=out.join("large-warm.gto");s.save(save.to_str().unwrap()).unwrap();drop(g);drop(s);
 let mut loaded=Solver::load_with_storage(save.to_str().unwrap(),Storage::Compressed).unwrap();loaded.use_isomorphism=true;emit(raw(&loaded,out,"loaded"));let mut g=GpuSolver::new_with_budget(&loaded,budget).unwrap();for _ in 0..2{g.iterate().unwrap();}g.sync_to_cpu(&mut loaded).unwrap();emit(raw(&loaded,out,"resumed"));
 emit(json!({"stage":"complete","snapshots":6,"GPU_constructor_calls":4,"iterations_executed":7,"q_bytes":bytes,"overlap_eligibility_condition_verified":true,"all_four_warm_scale_predicates_false":true,"budget_rejection_pass":true,"performance_measured":false,"worker_observed_by_thread_trace":false}));
}
'''
# The two typed q buffers have different element types, so keep their match arms separate.
warm=warm.replace('Store::I16{q,..}|Store::U16{q,..}=>q.len()*2','Store::I16{q,..}=>q.len()*2,Store::U16{q,..}=>q.len()*2')
(H/'large-warm.rs').write_text(warm,encoding='utf-8',newline='\n')
code=(R/'runs/E051-broader-build-plan/build.py').read_text(encoding='utf-8').replace('E051','E080').replace('E020','E051').replace("H.parent/'small-gain-confirmation-plan'","H.parent/'accepted-E051-live-20261018'").replace('import common as old','import common_e051_live as old')
code=code.replace("m['absent_research_paths']","m['absent_research_paths']")
code=code.replace("assert cuda.read_bytes() in data and opposite.read_bytes() not in data","assert cuda.read_bytes() in data and opposite.read_bytes()==cuda.read_bytes()")
code=code.replace("assert Path(P['arms']['candidate']['cuda']).read_bytes() in data and Path(P['arms']['baseline']['cuda']).read_bytes() not in data","assert Path(P['arms']['candidate']['cuda']).read_bytes() in data and Path(P['arms']['baseline']['cuda']).read_bytes()==Path(P['arms']['candidate']['cuda']).read_bytes()")
code=code.replace("'opposite_cuda_absent':True","'CUDA_source_identical_both_arms':True")
code=code.replace("assert shutil.disk_usage(ROOT).free>=54*1024**3 and shutil.disk_usage(REPO).free>=54*1024**3","assert shutil.disk_usage(ROOT).free>=106*1024**3 and shutil.disk_usage('T:\\\\').free>=53687091200")
code=code.replace("env['CARGO_MANIFEST_DIR']=arm['io_root']","env['CARGO_MANIFEST_DIR']=arm['io_root']")
code=code.replace("'Exact tracked integration-test source, pinned measured solver rlib and dependencies. Only harness compile-time save-path environment relocated toS. Checkout source unchanged.'","row['relationship']")
ast.parse(code);(H/'build.py').write_text(code,encoding='utf-8',newline='\n')
S=old.read(R/'runs/E080-source/manifest.json');B=old.read(R/'runs/E080-build-plan/build-protocol.json')
P={'id':'E080-broader-build','at':old.now(),'status':'FROZEN_PRE_COMPILER','owned':B['owned'],'accepted_source_sha256':old.BASE,'protected_main':B['protected_main'],'protected_ptx':B['protected_ptx'],'arms':{},'native_before_compilers_terminal':False,'performance_claim':False,'capacity_reservation_bytes':40*1024**3,'warm_scope':'One fixed large two-tone compressed fixture, six full raw q/scale snapshots, actual GPU warm initialization, iso false-to-true, tight-budget rejection, sync/materialized root query, complete save/load and resume. Same harness/inputs in both arms, no timing score. Eligibility verified from real byte lengths; no external worker-thread trace claimed.'}
paths=[Path(__file__),H/'build.py',H/'large-warm.rs',H/'warm-fixture.json',Q,X,R/'runs/E080-confirmation-closure/decision.json',R/'runs/E080-source/manifest.json',R/'runs/E080-source/source-review.json',C/'common_e051_live.py',C/'protected-main.json',old.REPO/'tools/postflop_autoresearch.py',old.REPO/'tools/postflop_validate_controls.py']
for arm,stem in [('baseline','E051-postflop_autoresearch'),('candidate','E080-postflop_autoresearch')]:
    mp=R/'binaries'/(stem+'.manifest.json');m=old.read(mp);old.pin(R/'binaries'/(stem+'.exe'),m['binary_sha256']);assert m['source_sha256']==old.BASE|(S['candidate_owned_sha256']if arm=='candidate'else{})
    deps={n:h for n,h in m['dependency_artifact_sha256'].items()if Path(n).suffix in['.rlib','.rmeta','.lib','.dll']}
    libs={}
    for name in['solver','serde_json']:
        found=[n for n in deps if Path(n).name.startswith('lib'+name+'-')and Path(n).suffix=='.rlib'];assert len(found)==1;libs[name]=found[0]
    rows=[];io=R/'runs/E080-broader-scratch'/arm
    for name in['postflop_state_perf','postflop_action_menus','postflop_resume_state','gpu','preflop_gpu','large-warm']:
        src=H/'large-warm.rs'if name=='large-warm'else old.REPO/'crates/solver/tests'/(name+'.rs');dest=R/'binaries'/('E080-broader-'+arm+'-'+name+'.exe')
        cmd=['rustc','--edition=2021',str(src),'--crate-name','e080_'+arm+'_'+name.replace('-','_'),'--cfg','feature="gpu"','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1']
        if name!='large-warm':cmd+=['--test']
        for lib,path in libs.items():cmd+=['--extern',lib+'='+path]
        cmd+=['-L','dependency='+str(Path(libs['solver']).parent),'-o',str(dest)]
        rows.append({'test_target':name,'source':str(src),'binary':str(dest),'command':cmd,'relationship':'Exact tracked fixed integration harness with isolated compile-time save path.'if name!='large-warm'else'Frozen large warm compressed state-control harness and fixed canonical fixture; no performance score.'});paths.append(src)
    P['arms'][arm]={'solver_library':libs['solver'],'dependencies':deps,'primary_manifest':str(mp),'cuda':str(old.REPO/'crates/solver/src/gpu/kernels.cu'),'io_root':str(io),'standalone':rows};paths.extend([mp,R/'binaries'/(stem+'.exe')])
target=R/'build-e080-broader-feature';command=['cargo','test','--release','--locked','--offline','-p','solver','--features','preflop-research','--test','continuation_paging','--test','continuation_symmetry','--no-run','--message-format=json']
P['feature']={'target':str(target),'command':command,'outputs':{'continuation_paging':'E080-broader-continuation_paging','continuation_symmetry':'E080-broader-continuation_symmetry'}}
for v in P['owned'].values():paths.extend([Path(v['base']),Path(v['candidate'])])
for name in['continuation_paging.rs','continuation_symmetry.rs']:paths.append(old.REPO/'crates/solver/tests'/name)
for stem in['E051-broader-continuation_paging','E051-broader-continuation_symmetry','E051-feature-solver']:
    mp=R/'binaries'/(stem+'.manifest.json');m=old.read(mp);old.pin(mp.with_suffix('.exe'),m['binary_sha256']);assert m['source_sha256']==old.BASE;paths.extend([mp,mp.with_suffix('.exe')])
P['input_sha256']={str(p):old.sha(p)for p in paths}
for arm in P['arms'].values():P['input_sha256'].update(arm['dependencies'])
old.save(H/'protocol.json',P)
for p in H.iterdir():
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-build-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080');e.update(status='running',stage='Broader correctness harness builds',reason='Fresh16 timing passed at 1.714816%, all 16 pairs improved and 96 results/736 checkpoints are exact. Compile matched state/menu/resume, postflop/preflop GPU, continuation and large warm compressed controls. No adoption yet.');e['evidence'].append({'label':'Frozen broader build protocol','url':'evidence/E080-broader-build-plan/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080',stage='E080 broader correctness builds',activity='Build fixed broader harnesses against exact accepted and candidate libraries, plus fresh candidate continuation integrations. All bulk and save outputs stay on S:. Accepted live E051 is unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print('E080 broader build protocol',old.sha(H/'protocol.json'),flush=True)
