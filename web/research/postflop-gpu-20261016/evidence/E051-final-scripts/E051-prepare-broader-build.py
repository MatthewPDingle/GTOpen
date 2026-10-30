"""Freeze isolated correctness harness builds after complete fresh16 confirmation."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();ar.refuse_active(ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
CONF=ROOT/'comparisons/E051-fresh16-confirmation/report.json';CROSS=ROOT/'comparisons/E051-fresh16-root-check/report.json'
assert old.read(CONF)['status']=='pass_fresh16_timing_only' and old.read(CROSS)['status']=='pass_timing_only'
H=ROOT/'runs/E051-broader-build-plan';H.mkdir()
build=r'''import json,os,shutil,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
ROOT,REPO=old.ROOT,old.REPO;OUT=ROOT/'runs/E051-broader-build'
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for path,h in P['input_sha256'].items():old.pin(path,h)
def reserve():
 assert shutil.disk_usage(ROOT).free>=54*1024**3 and shutil.disk_usage(REPO).free>=54*1024**3
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
   old.custody();verify();data=dest.read_bytes();assert cuda.read_bytes() in data and opposite.read_bytes() not in data
   manifest={'source_sha256':sources(arm_name),'candidate':'E020' if arm_name=='baseline' else 'E051','arm':arm_name,'binary_source_relationship':'Exact tracked integration-test source, pinned measured solver rlib and dependencies. Only harness compile-time save-path environment relocated toS. Checkout source unchanged.','harness_source':row['source'],'harness_source_sha256':old.sha(row['source']),'solver_library':arm['solver_library'],'solver_library_sha256':old.sha(arm['solver_library']),'dependency_artifact_sha256':arm['dependencies'],'build_command':row['command'],'compile_environment':{'CARGO_MANIFEST_DIR':arm['io_root']},'expected_cuda_sha256':old.sha(cuda),'expected_cuda_embedded':True,'opposite_cuda_absent':True,'build_stdout_sha256':old.sha(stage/'rustc.stdout.log'),'build_stderr_sha256':old.sha(stage/'rustc.stderr.log'),'native_tests_executed':0}
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
   data=Path(x['executable']).read_bytes();assert Path(P['arms']['candidate']['cuda']).read_bytes() in data and Path(P['arms']['baseline']['cuda']).read_bytes() not in data
   dest=ROOT/'binaries'/(feature['outputs'][x['target']['name']]+'.exe');shutil.copyfile(x['executable'],dest)
   manifest={**old.ar.source_identity(),'candidate':'E051','arm':'candidate','binary_source_relationship':'Fresh Cargo feature integration binary from exact owned candidate source, isolated target and unchanged harness.','cargo_artifact':x,'dependency_artifact_sha256':deps,'build_command':feature['command'],'build_stdout_sha256':old.sha(stage/'cargo.stdout.log'),'build_stderr_sha256':old.sha(stage/'cargo.stderr.log'),'expected_cuda_sha256':old.sha(Path(P['arms']['candidate']['cuda'])),'expected_cuda_embedded':True,'opposite_cuda_absent':True,'native_tests_executed':0}
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
print('E051 broader builds terminal; all source restored; no native tests ran.',flush=True)
'''
(H/'build.py').write_text(build,encoding='utf-8');ast.parse(build)
prototype=old.read(ROOT/'runs/E051-build-plan/build-protocol.json')
p={'id':'E051-broader-build','at':old.now(),'status':'FROZEN_PRE_COMPILE','owned':prototype['owned'],'accepted_source_sha256':old.BASE,'protected_main':prototype['protected_main'],'protected_ptx':prototype['protected_ptx'],'arms':{},'native_before_compilers_terminal':False,'performance_claim':False}
targets=['postflop_state_perf','postflop_action_menus','postflop_resume_state','gpu']
paths=[H/'build.py',CONF,CROSS,ROOT/'runs/E051-confirmation-plan/confirmation-publication.json',ROOT/'runs/E051-source/manifest.json',ROOT/'runs/E051-source/source-review.json',ROOT/'runs/E051-broader-scout/report.json',Path(p['protected_main']),ROOT/'runs/small-gain-confirmation-plan/common.py',ar.REPO/'tools/postflop_autoresearch.py',ar.REPO/'tools/postflop_validate_controls.py']
for arm,stem,cuda in [('baseline','SG-E020-postflop_autoresearch','baseline.cu'),('candidate','E051-postflop_autoresearch','candidate.cu')]:
 mp=ROOT/'binaries'/(stem+'.manifest.json');m=old.read(mp);old.pin(ROOT/'binaries'/(stem+'.exe'),m['binary_sha256'])
 expected=old.BASE|({n:v['candidate_sha256'] for n,v in p['owned'].items()} if arm=='candidate' else {})
 assert m['source_sha256']==expected
 deps={n:h for n,h in m['dependency_artifact_sha256'].items() if Path(n).suffix in ['.rlib','.rmeta','.lib','.dll']}
 for n,h in deps.items():old.pin(n,h)
 solver=[n for n in deps if Path(n).name.startswith('libsolver-') and Path(n).suffix=='.rlib'];jsonlib=[n for n in deps if Path(n).name.startswith('libserde_json-') and Path(n).suffix=='.rlib'];assert len(solver)==len(jsonlib)==1
 io=ROOT/'runs/E051-broader-scratch'/arm;rows=[]
 for name in targets:
  src=old.REPO/'crates/solver/tests'/(name+'.rs');dest=ROOT/'binaries'/('E051-broader-'+arm+'-'+name+'.exe')
  assert 'include_' not in src.read_text(encoding='utf-8')
  cmd=['rustc','--edition=2021','--test',str(src),'--crate-name','e051_'+arm+'_'+name,'--cfg','feature="gpu"','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1','--extern','solver='+solver[0],'--extern','serde_json='+jsonlib[0],'-L','dependency='+str(Path(solver[0]).parent),'-o',str(dest)]
  rows.append({'test_target':name,'source':str(src),'binary':str(dest),'command':cmd});paths.append(src)
 p['arms'][arm]={'solver_library':solver[0],'dependencies':deps,'primary_manifest':str(mp),'cuda':str(ROOT/'runs/E051-source'/cuda),'io_root':str(io),'standalone':rows};paths.extend([mp,ROOT/'binaries'/(stem+'.exe'),ROOT/'runs/E051-source'/cuda])
target=ROOT/'build-e051-broader-feature';command=['cargo','test','--release','--locked','--offline','-p','solver','--features','preflop-research','--test','continuation_paging','--test','continuation_symmetry','--no-run','--message-format=json']
p['feature']={'target':str(target),'command':command,'outputs':{'continuation_paging':'E051-broader-continuation_paging','continuation_symmetry':'E051-broader-continuation_symmetry'}}
for v in p['owned'].values():paths.extend([Path(v['base']),Path(v['candidate'])])
for name in ['continuation_paging.rs','continuation_symmetry.rs']:paths.append(old.REPO/'crates/solver/tests'/name)
p['input_sha256']={str(x):old.sha(x) for x in paths}
for arm in p['arms'].values():p['input_sha256'].update(arm['dependencies'])
old.save(H/'protocol.json',p)
published={}
for src in H.rglob('*'):
 if not src.is_file():continue
 key=H.name+'/'+src.relative_to(H).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
 published[key]=old.sha(src)
old.save(H/'pre-build-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'native_executions':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(status='preparing',stage='Fresh16 passed; isolated broader builds next',reason='Fresh16all16pairs improve,aggregate2.1751731507%,96results/736checks exact. Compile exact fixed correctness harnesses with isolatedSsavepaths plus fresh continuation integrations. No source adoption.');e['evidence'].append({'label':'E051 broader build protocol','url':'evidence/E051-broader-build-plan/protocol.json'});st.update(state='running',stage='E051 broader build preparation',activity='One frozen broader build batch after confirmation; no new benchmark samples or accepted gain.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'standalone_binaries':8,'feature_integration_binaries':2,'published':len(published)}),flush=True)
