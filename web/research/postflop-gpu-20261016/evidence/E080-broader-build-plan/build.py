import json,os,shutil,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
ROOT,REPO=old.ROOT,old.REPO;OUT=ROOT/'runs/E080-broader-build'
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for path,h in P['input_sha256'].items():old.pin(path,h)
def reserve():
 assert shutil.disk_usage(ROOT).free>=106*1024**3 and shutil.disk_usage('T:\\').free>=53687091200
def sources(arm):return old.BASE|({n:v['candidate_sha256'] for n,v in P['owned'].items()} if arm=='candidate' else {})
def candidate_guard():
 assert old.ar.source_identity()['source_sha256']==sources('candidate')
 m=old.read(P['protected_main']);mp=Path(m['root'])
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=mp,text=True).strip()==m['git_head']
 for n,h in m['source_sha256'].items():old.pin(mp/n,h)
 for n in m['absent_research_paths']:assert not (mp/n).exists()
 old.pin(m['live_path'],m['live_sha256'])
 for n,v in P['protected_ptx'].items():old.pin(REPO/n,v['sha256'])
 assert set(subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=REPO,text=True).splitlines())==set(P['owned'])
def freeze(binary,manifest):
 manifest.update(binary_sha256=old.sha(binary),build_protocol_sha256=sys.argv[1],build_script_sha256=old.sha(H/'build.py'),built_at=old.now(),candidate_accepted=False,scope='Broader correctness only; no primary timing or adoption from these builds.')
 old.save(binary.with_suffix('.manifest.json'),manifest)
 return {str(binary):old.sha(binary),str(binary.with_suffix('.manifest.json')):old.sha(binary.with_suffix('.manifest.json'))}
verify()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());reserve();assert not OUT.exists();OUT.mkdir()
 for arm in P['arms'].values():
  assert not Path(arm['io_root']).exists()
  for x in arm['standalone']:
   assert not Path(x['binary']).exists() and not Path(x['binary']).with_suffix('.manifest.json').exists()
 feature=P['feature'];assert not Path(feature['target']).exists()
 for stem in feature['outputs'].values():assert not (ROOT/'binaries'/(stem+'.exe')).exists()
 artifacts={}
 for arm_name in ['baseline','candidate']:
  arm=P['arms'][arm_name];cuda=Path(arm['cuda']);opposite=Path(P['arms']['candidate' if arm_name=='baseline' else 'baseline']['cuda'])
  for row in arm['standalone']:
   verify();old.custody();old.ar.refuse_active(old.ar.live_status());reserve()
   dest=Path(row['binary']);stage=OUT/(arm_name+'-'+row['test_target']);stage.mkdir()
   env=old.env();env['CARGO_MANIFEST_DIR']=arm['io_root']
   forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER'}
   assert not {k:v for k,v in env.items() if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_')}
   old.child(row['command'],stage,'rustc',env,600)
   old.custody();verify();data=dest.read_bytes();assert cuda.read_bytes() in data and opposite.read_bytes()==cuda.read_bytes()
   manifest={'source_sha256':sources(arm_name),'candidate':'E051' if arm_name=='baseline' else 'E080','arm':arm_name,'binary_source_relationship':row['relationship'],'harness_source':row['source'],'harness_source_sha256':old.sha(row['source']),'solver_library':arm['solver_library'],'solver_library_sha256':old.sha(arm['solver_library']),'dependency_artifact_sha256':arm['dependencies'],'build_command':row['command'],'compile_environment':{'CARGO_MANIFEST_DIR':arm['io_root']},'expected_cuda_sha256':old.sha(cuda),'expected_cuda_embedded':True,'CUDA_source_identical_both_arms':True,'build_stdout_sha256':old.sha(stage/'rustc.stdout.log'),'build_stderr_sha256':old.sha(stage/'rustc.stderr.log'),'native_tests_executed':0}
   artifacts.update(freeze(dest,manifest));old.save(stage/'complete.json',{'at':old.now(),'returncode':0,'binary_sha256':old.sha(dest),'native_executions':0,'accepted162_unchanged':True});print(arm_name,row['test_target'],'compiled; no native execution.',flush=True)
 stage=OUT/'candidate-feature';stage.mkdir();env=old.env();env['CARGO_TARGET_DIR']=feature['target'];fault=None
 try:
  for n,v in P['owned'].items():shutil.copyfile(v['candidate'],REPO/n)
  verify();candidate_guard();old.ar.refuse_active(old.ar.live_status());reserve()
  old.child(feature['command'],stage,'cargo',env,1800)
  verify();candidate_guard()
  records=[json.loads(x) for x in (stage/'cargo.stdout.log').read_text(encoding='utf-8').splitlines()]
  assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in records)
  compiled=[x for x in records if x.get('reason')=='compiler-artifact']
  target=Path(feature['target']).resolve()
  for x in compiled:
   for f in x.get('filenames',[])+([x['executable']] if x.get('executable') else []):assert Path(f).resolve().is_relative_to(target)
  deps={f:old.sha(f) for x in compiled for f in x.get('filenames',[]) if Path(f).is_file() and Path(f).suffix in ['.rlib','.rmeta','.lib','.dll']}
  tests=[x for x in compiled if x.get('profile',{}).get('test') and x.get('executable') and x['target']['name'] in feature['outputs']]
  assert len(tests)==2 and {x['target']['name'] for x in tests}==set(feature['outputs'])
  for x in tests:
   assert x['fresh'] is False and x['features']==['gpu','preflop-research']
   assert Path(x['target']['src_path']).resolve()==(REPO/'crates/solver/tests'/(x['target']['name']+'.rs')).resolve()
   data=Path(x['executable']).read_bytes();assert Path(P['arms']['candidate']['cuda']).read_bytes() in data and Path(P['arms']['baseline']['cuda']).read_bytes()==Path(P['arms']['candidate']['cuda']).read_bytes()
   dest=ROOT/'binaries'/(feature['outputs'][x['target']['name']]+'.exe');shutil.copyfile(x['executable'],dest)
   manifest={**old.ar.source_identity(),'candidate':'E080','arm':'candidate','binary_source_relationship':'Fresh Cargo feature integration binary from exact owned candidate source, isolated target and unchanged harness.','cargo_artifact':x,'dependency_artifact_sha256':deps,'build_command':feature['command'],'build_stdout_sha256':old.sha(stage/'cargo.stdout.log'),'build_stderr_sha256':old.sha(stage/'cargo.stderr.log'),'expected_cuda_sha256':old.sha(Path(P['arms']['candidate']['cuda'])),'expected_cuda_embedded':True,'CUDA_source_identical_both_arms':True,'native_tests_executed':0}
   artifacts.update(freeze(dest,manifest))
  old.save(stage/'complete.json',{'at':old.now(),'returncode':0,'all_artifacts_fresh':True,'native_executions':0,'source_sha256':sources('candidate')})
 except BaseException as exc:
  fault=repr(exc);old.save(stage/'failure.json',{'at':old.now(),'error':fault,'native_executions':0});raise
 finally:
  for n,v in P['owned'].items():
   assert old.sha(REPO/n) in [v['base_sha256'],v['candidate_sha256']]
   shutil.copyfile(v['base'],REPO/n)
  old.custody();old.save(stage/'restoration.json',{'at':old.now(),'accepted162_main_live_ptx_unchanged':True,'error':fault})
 verify();old.custody();old.save(OUT/'complete.json',{'at':old.now(),'build_protocol_sha256':sys.argv[1],'all_compilers_terminal':True,'native_executions':0,'artifact_sha256':artifacts,'evidence_sha256':{str(x):old.sha(x) for x in OUT.rglob('*.json')},'accepted162_main_live_ptx_unchanged':True})
print('E080 broader builds terminal; all source restored; no native tests ran.',flush=True)
