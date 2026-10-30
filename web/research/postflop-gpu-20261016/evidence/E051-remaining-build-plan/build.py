import json,os,shutil,sys
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
