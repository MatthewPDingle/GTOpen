"""Freeze fresh baseline feature library and exact capacity/holdout evaluators."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();ar.refuse_active(ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
assert old.read(ROOT/'comparisons/E051-broader-controls/report.json')['status']=='pass_broader_exact_controls_only'
H=ROOT/'runs/E051-remaining-build-plan';H.mkdir()
probe=r'''use solver::{Spot,SpotConfig,Solver,Algorithm,TreeConfig,StreetSizing,parse_sizes};
use solver::gpu::{GpuSolver,StoredContinuationGpu,StoredWorkspace};
use solver::store::Store;
use cudarc::driver::CudaContext;
use std::{sync::Arc,path::PathBuf,io::Write};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E051_CAPACITY {v}").unwrap();o.flush().unwrap();}
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);let root=PathBuf::from(&args[1]);std::fs::create_dir(&root).unwrap();
 // Retain one primary context for comparable unscored device-wide observations.
 // All owned-slice accounting below comes from the actual constructor method.
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let mut workspace=StoredWorkspace::default();let mut ram=u64::MAX;let mut cases=0;
 for board in ["KsQs2d","KsQs2s","KsQh2d"] {for (pot,stack) in [(39.5,80.),(93.5,155.)] {
  let z=StreetSizing{bet:parse_sizes("50").unwrap(),raise:vec![],donk:parse_sizes("50").unwrap()};
  let spot=Arc::new(Spot::new(SpotConfig{board:board.into(),range_oop:"AA,KK,AQs,KQo,88,76s".into(),range_ip:"AA,QQ,AKo,QJs,99".into(),tree:TreeConfig{starting_pot:pot,effective_stack:stack,rake_pct:0.04,rake_cap:6.,max_raises:0,oop:[z.clone(),z.clone(),z.clone()],ip:[z.clone(),z.clone(),z],..Default::default()}}).unwrap());
  let mut host=Solver::new(spot);host.algo=Algorithm::CfrPlus;host.use_isomorphism=false;assert!(host.regrets.iter().chain(&host.strat).all(|x|matches!(x,Store::F32(_))));
  let before=ctx.mem_get_info().unwrap();
  let gpu=StoredContinuationGpu::new(&host,&mut workspace,&root,cases,&mut ram).unwrap();ctx.synchronize().unwrap();
  let accounting=gpu.research_capacity_check();let after=ctx.mem_get_info().unwrap();
  emit(serde_json::json!({"stage":"case","id":cases,"board":board,"pot":pot,"stack":stack,"actual_metadata_assertions_passed":true,"capacity":accounting,"actual_workspace_bytes":workspace.bytes(),"remaining_ram_budget":ram,"host_type_bytes":{"GpuSolver":std::mem::size_of::<GpuSolver>(),"StoredContinuationGpu":std::mem::size_of::<StoredContinuationGpu>(),"StoredWorkspace":std::mem::size_of::<StoredWorkspace>()},"device_wide_observation":{"free_before":before.0,"free_with_entry":after.0,"total":after.1,"solver_only_delta":false},"solver_iterations":0}));
  drop(gpu);ctx.synchronize().unwrap();cases+=1;
 }}
 assert_eq!(cases,6);emit(serde_json::json!({"stage":"complete","cases":cases,"actual_workspace_bytes":workspace.bytes(),"solver_iterations":0,"performance_measured":false,"candidate_accepted":false}));ctx.check_err().unwrap();
}
'''
(H/'capacity.rs').write_text(probe,encoding='utf-8')
build=r'''import json,os,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');ROOT,REPO=old.ROOT,old.REPO;OUT=ROOT/'runs/E051-remaining-build'
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for path,h in P['input_sha256'].items():old.pin(path,h)
 old.custody()
def dependencies(artifacts):return {f:old.sha(f) for x in artifacts for f in x.get('filenames',[]) if Path(f).is_file() and Path(f).suffix in ['.rlib','.rmeta','.lib','.dll']}
def libs(deps):
 result={}
 for name in ['solver','serde_json','cudarc']:
  found=[p for p in deps if Path(p).name.startswith('lib'+name+'-') and Path(p).suffix=='.rlib'];assert len(found)==1,(name,found);result[name]=found[0]
 return result
verify()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3;assert not OUT.exists();OUT.mkdir();assert not Path(P['baseline_feature_target']).exists()
 stage=OUT/'baseline-feature-library';stage.mkdir();env=old.env();env['CARGO_TARGET_DIR']=P['baseline_feature_target']
 forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER'};assert not {k:v for k,v in env.items() if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_')}
 old.child(P['baseline_feature_command'],stage,'cargo',env,1800);verify()
 records=[json.loads(x) for x in (stage/'cargo.stdout.log').read_text(encoding='utf-8').splitlines()];assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in records)
 artifacts=[x for x in records if x.get('reason')=='compiler-artifact'];target=Path(P['baseline_feature_target']).resolve()
 for x in artifacts:
  for f in x.get('filenames',[]):assert Path(f).resolve().is_relative_to(target)
 solver=[x for x in artifacts if x['target']['name']=='solver' and 'lib' in x['target']['kind']];assert len(solver)==1 and solver[0]['fresh'] is False and solver[0]['features']==['gpu','preflop-research']
 assert Path(solver[0]['target']['src_path']).resolve()==(REPO/'crates/solver/src/lib.rs').resolve()
 before_deps=dependencies(artifacts);before_libs=libs(before_deps)
 old.save(stage/'complete.json',{'at':old.now(),'source_sha256':old.BASE,'command':P['baseline_feature_command'],'returncode':0,'artifact':solver[0],'dependency_artifact_sha256':before_deps,'solver_library_sha256':old.sha(before_libs['solver']),'native_executions':0})
 arms={'baseline':{'capacity_dependencies':before_deps,'capacity_libraries':before_libs},'candidate':{'capacity_dependencies':P['candidate_feature_dependencies'],'capacity_libraries':libs(P['candidate_feature_dependencies'])}}
 pins={}
 for arm in ['baseline','candidate']:
  for kind in ['capacity','holdout']:
   verify();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3
   data=P['arms'][arm];deps=arms[arm]['capacity_dependencies'] if kind=='capacity' else data['primary_dependencies'];binding=arms[arm]['capacity_libraries'] if kind=='capacity' else libs(deps)
   for p,h in deps.items():old.pin(p,h)
   src=Path(P['capacity_source'] if kind=='capacity' else P['holdout_source']);dest=ROOT/'binaries'/('E051-'+kind+'-'+arm+'.exe');assert not dest.exists() and not dest.with_suffix('.manifest.json').exists()
   out=OUT/(arm+'-'+kind);out.mkdir()
   cmd=['rustc','--edition=2021',str(src),'--crate-name','e051_'+kind+'_'+arm,'-C','opt-level=3','-C','lto=thin','-C','codegen-units=1']
   if kind=='holdout':cmd+=['--test','--cfg','feature="gpu"']
   for name,path in binding.items():cmd+=['--extern',name+'='+path]
   cmd+=['-L','dependency='+str(Path(binding['solver']).parent),'-o',str(dest)]
   old.child(cmd,out,'rustc',old.env(),600);verify()
   blob=dest.read_bytes();expected=Path(data['cuda']).read_bytes();opposite=Path(P['arms']['candidate' if arm=='baseline' else 'baseline']['cuda']).read_bytes();assert expected in blob and opposite not in blob
   manifest={'candidate':'E020' if arm=='baseline' else 'E051','arm':arm,'purpose':kind,'source_sha256':old.BASE|P['owned_candidate_sha256'] if arm=='candidate' else old.BASE,'binary_sha256':old.sha(dest),'built_at':old.now(),'build_command':cmd,'build_protocol_sha256':sys.argv[1],'build_script_sha256':old.sha(H/'build.py'),'harness_source':str(src),'harness_source_sha256':old.sha(src),'dependency_artifact_sha256':deps,'source_relationship':'Pinned exact solver library plus fixed standalone probe; identical unchanged historical evaluator/fixture for holdout.','expected_cuda_sha256':old.sha(data['cuda']),'own_cuda_embedded':True,'opposite_cuda_absent':True,'build_stdout_sha256':old.sha(out/'rustc.stdout.log'),'build_stderr_sha256':old.sha(out/'rustc.stderr.log'),'native_executions':0,'candidate_accepted':False}
   old.save(dest.with_suffix('.manifest.json'),manifest);pins[str(dest)]=old.sha(dest);pins[str(dest.with_suffix('.manifest.json'))]=old.sha(dest.with_suffix('.manifest.json'))
   old.save(out/'complete.json',{'at':old.now(),'returncode':0,'binary_sha256':old.sha(dest),'native_executions':0});print(arm,kind,'compiled; no native execution.',flush=True)
 verify();old.save(OUT/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'all_compilers_terminal':True,'native_executions':0,'artifact_sha256':pins,'evidence_sha256':{str(p):old.sha(p) for p in OUT.rglob('*.json')},'accepted162_main_live_ptx_unchanged':True})
print('E051 capacity/holdout builds terminal; no production edits or native tests.',flush=True)
'''
(H/'build.py').write_text(build,encoding='utf-8');ast.parse(build)
candidate_manifest=ROOT/'binaries/E051-broader-continuation_paging.manifest.json';cm=old.read(candidate_manifest);candidate_deps=cm['dependency_artifact_sha256'];assert cm['source_sha256']==old.BASE|{'crates/solver/src/gpu/kernels.cu':'a926bf0bc818a2ba808c862b59a552dfb7ade453ca18f347b4307784e47d9647'}
for name,h in candidate_deps.items():old.pin(name,h)
hold=ROOT/'runs/E020-wide-turn-holdout-implementation-r2'
p={'id':'E051-remaining-build','at':old.now(),'status':'FROZEN_PRE_COMPILE','baseline_feature_target':str(ROOT/'build-e051-capacity-baseline-feature'),'baseline_feature_command':['cargo','build','--release','--locked','--offline','-p','solver','--features','preflop-research','--lib','--message-format=json'],'candidate_feature_dependencies':candidate_deps,'capacity_source':str(H/'capacity.rs'),'holdout_source':str(hold/'evaluator.rs'),'holdout_fixture':str(hold/'fixture.json'),'owned_candidate_sha256':{'crates/solver/src/gpu/kernels.cu':'a926bf0bc818a2ba808c862b59a552dfb7ade453ca18f347b4307784e47d9647'},'arms':{},'native_before_all_compilers_terminal':False,'capacity_scope':'Actual constructor checks all retained CUDA metadata/wrapper/canonical state against plan, observed mutable workspace and host sizeof across6fixed stored-control cases. Device-wide free observations informational only; no solver iterations/performance/forced spill.','holdout_scope':'Exact unchanged historical evaluator/fixture and timing/quality boundaries, before/after libraries only. Fresh cohort protocol must be frozen before native runs.'}
paths=[H/'build.py',H/'capacity.rs',candidate_manifest,hold/'evaluator.rs',hold/'fixture.json',ROOT/'comparisons/E051-broader-controls/report.json',ROOT/'comparisons/E051-broader-root-check/report.json',ROOT/'comparisons/E051-broader-controls/publication.json',ROOT/'comparisons/E051-fresh16-confirmation/report.json',ROOT/'runs/E051-qualification-checkpoint/checkpoint.json',old.REPO/'crates/solver/src/gpu/continuation_storage.rs',old.REPO/'crates/solver/src/gpu/continuation_stored_device_tests.rs',ROOT/'runs/small-gain-confirmation-plan/common.py']
for arm,stem,cuda in [('baseline','SG-E020-postflop_autoresearch','baseline.cu'),('candidate','E051-postflop_autoresearch','candidate.cu')]:
 mp=ROOT/'binaries'/(stem+'.manifest.json');m=old.read(mp);old.pin(ROOT/'binaries'/(stem+'.exe'),m['binary_sha256']);assert m['source_sha256']==old.BASE|(p['owned_candidate_sha256'] if arm=='candidate' else {})
 deps=m['dependency_artifact_sha256']
 for path,h in deps.items():old.pin(path,h)
 p['arms'][arm]={'primary_dependencies':deps,'primary_manifest':str(mp),'cuda':str(ROOT/'runs/E051-source'/cuda)};paths.extend([mp,ROOT/'runs/E051-source'/cuda])
p['input_sha256']={str(x):old.sha(x) for x in paths};p['input_sha256'].update(candidate_deps)
for arm in p['arms'].values():p['input_sha256'].update(arm['primary_dependencies'])
old.save(H/'protocol.json',p)
published={}
for src in H.rglob('*'):
 if not src.is_file():continue
 key=H.name+'/'+src.relative_to(H).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
 published[key]=old.sha(src)
old.save(H/'pre-build-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'native_executions':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(status='preparing',stage='Capacity/holdout isolated build batch next',reason='Broad exact controls pass. Build one fresh accepted feature library, matched public-capacity probes and unchanged fixed wide-turn evaluators. No source promotion or new primary measurements.');e['evidence'].append({'label':'E051 capacity/holdout build protocol','url':'evidence/E051-remaining-build-plan/protocol.json'});st.update(state='running',stage='E051 remaining evaluator builds',activity='Serialized capacity and fixedholdout builds; broad and fresh16 results retained.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'published':len(published)}),flush=True)
