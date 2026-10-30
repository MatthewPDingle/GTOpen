"""Frozen two-phase E090 build. Accepted source is restored before any native run."""
import sys,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/E090-build-plan';P=h.read(H/'protocol.json');BASE=P['accepted_source_sha256'];OUT=ROOT/'runs/E090-final-build'
def verify():
 h.pin(H/'protocol.json',sys.argv[1])
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
def candidate_guard():
 assert h.ar.source_identity()['source_sha256']==BASE|P['candidate_owned_sha256']
 m=h.read(h.EPOCH/'protected-main.json');main=Path(m['root'])
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=main,text=True).strip()==m['git_head']
 for n,digest in m['source_sha256'].items():h.pin(main/n,digest)
 for n in m['absent_research_paths']:assert not(main/n).exists()
 h.pin(m['live_path'],m['live_sha256'])
 for n,v in h.read(h.EPOCH/'preexisting-target-artifacts.json').items():h.pin(h.REPO/n,v['sha256'])
 assert set(subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=h.REPO,text=True).splitlines())==set(P['owned'])
verify();h.custody();OUT.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status())
 for phase in P['phases']:
  assert not Path(phase['target']).exists()
  for stem in phase['outputs'].values():
   assert not(ROOT/'binaries'/(stem+'.exe')).exists() and not(ROOT/'binaries'/(stem+'.manifest.json')).exists()
 for phase in P['phases']:
  verify();h.custody();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
  out=OUT/phase['id'];out.mkdir();target=Path(phase['target']);target.mkdir()
  env=h.env();forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET','CARGO_TARGET_DIR'}
  assert not{k:v for k,v in env.items()if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_')or(k.startswith('CARGO_TARGET_')and k.endswith('_RUSTFLAGS'))}
  cmd=['cargo','test','--release','--locked','--offline','--target-dir',str(target),'-p','solver','--features',phase['features'],'--lib']
  if phase['integration']:cmd+=['--test','postflop_autoresearch']
  cmd+=['--no-run','--message-format=json'];fault=None
  try:
   for n,v in P['owned'].items():shutil.copyfile(v['candidate'],h.REPO/n);shutil.copyfile(v['candidate'],out/Path(n).name)
   candidate_guard();h.child(cmd,out,'cargo',1800);verify();candidate_guard()
   records=[json.loads(x)for x in(out/'cargo.stdout.log').read_text(encoding='utf-8').splitlines()]
   assert any(x.get('reason')=='build-finished'and x.get('success')is True for x in records)
   artifacts=[x for x in records if x.get('reason')=='compiler-artifact']
   for x in artifacts:
    for f in x.get('filenames',[])+([x['executable']]if x.get('executable')else[]):assert Path(f).resolve().is_relative_to(target.resolve())
   deps={f:h.sha(f)for x in artifacts for f in x.get('filenames',[])if Path(f).is_file()and Path(f).suffix in['.rlib','.rmeta','.lib','.dll']}
   tests=[x for x in artifacts if x.get('profile',{}).get('test')and x.get('executable')and x['target']['name']in phase['outputs']]
   assert len(tests)==len(phase['outputs'])and{x['target']['name']for x in tests}==set(phase['outputs']);pins={}
   for x in tests:
    assert x['fresh']is False and x['features']==phase['expected_features']
    name=x['target']['name'];binary=ROOT/'binaries'/(phase['outputs'][name]+'.exe')
    expected=h.REPO/('crates/solver/src/lib.rs'if name=='solver'else'crates/solver/tests/postflop_autoresearch.rs')
    assert Path(x['target']['src_path']).resolve()==expected.resolve()
    assert(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes()in Path(x['executable']).read_bytes()
    shutil.copyfile(x['executable'],binary)
    manifest={**h.ar.source_identity(),'candidate':'E090','measurement_epoch':'RAM20261028','phase':phase['id'],'binary_sha256':h.sha(binary),'built_at':h.now(),'build_command':cmd,'cargo_artifact':x,'dependency_artifact_sha256':deps,'source_copies':{n:{'path':str(out/Path(n).name),'sha256':v['candidate_sha256']}for n,v in P['owned'].items()},'build_log_sha256':h.sha(out/'cargo.stdout.log'),'build_protocol_sha256':sys.argv[1],'build_script_sha256':h.sha(__file__),'candidate_accepted':False,'control_only':phase['id']=='feature'}
    h.save(binary.with_suffix('.manifest.json'),manifest)
    for p in[binary,binary.with_suffix('.manifest.json')]:pins[str(p)]=h.sha(p)
   h.save(out/'complete.json',{'at':h.now(),'source_sha256':BASE|P['candidate_owned_sha256'],'command':cmd,'returncode':0,'artifact_sha256':pins,'dependency_sha256':deps,'stdout_sha256':h.sha(out/'cargo.stdout.log'),'stderr_sha256':h.sha(out/'cargo.stderr.log'),'native_executions':0})
  except BaseException as exc:
   fault=repr(exc);h.save(out/'failure.json',{'at':h.now(),'error':fault,'native_executions':0});raise
  finally:
   for n,v in P['owned'].items():
    assert h.sha(h.REPO/n)in[v['base_sha256'],v['candidate_sha256']];shutil.copyfile(v['base'],h.REPO/n)
   h.custody();h.save(out/'restoration.json',{'at':h.now(),'accepted_source_restored':True,'main_live_ptx_unchanged':True,'error':fault})
  print(phase['id'],'terminal; accepted E080 restored.',flush=True)
 h.save(OUT/'complete.json',{'at':h.now(),'all_compilers_terminal':True,'native_executions':0,'build_protocol_sha256':sys.argv[1],'evidence_sha256':{str(p):h.sha(p)for p in OUT.rglob('*.json')}})
print('E090 fresh builds complete; no ordinary tests or speed measurements yet.',flush=True)
