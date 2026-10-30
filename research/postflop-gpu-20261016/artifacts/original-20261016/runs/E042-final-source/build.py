"""Frozen E042 final one-file build; restore accepted files before native work."""
import json,os,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2
old.pin(HERE/'build-protocol.json',sys.argv[1]);P=old.read(HERE/'build-protocol.json')
ROOT,REPO=old.ROOT,old.REPO
BASE=P['accepted_source_sha256'];OUT=ROOT/'runs/E042-final-build'

def verify():
 old.pin(HERE/'build-protocol.json',sys.argv[1])
 for path,h in P['input_sha256'].items():old.pin(path,h)

def candidate_guard():
 assert old.ar.source_identity()['source_sha256']==BASE|{n:v['candidate_sha256'] for n,v in P['owned'].items()}
 m=old.read(P['protected_main']);mp=Path(m['root'])
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=mp,text=True).strip()==m['git_head']
 for n,h in m['source_sha256'].items():old.pin(mp/n,h)
 for n in m['absent_research_paths']:assert not (mp/n).exists()
 old.pin(m['live_path'],m['live_sha256'])
 for n,v in P['protected_ptx'].items():old.pin(REPO/n,v['sha256'])
 assert set(subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=REPO,text=True).splitlines())==set(P['owned'])

verify()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status())
 assert not OUT.exists();OUT.mkdir()
 for phase in P['phases']:
  assert not Path(phase['target']).exists()
  for n in phase['outputs'].values():
   assert not (ROOT/'binaries'/f'{n}.exe').exists()
   assert not (ROOT/'binaries'/f'{n}.manifest.json').exists()
 for phase in P['phases']:
  verify();old.custody();old.ar.refuse_active(old.ar.live_status())
  assert shutil.disk_usage(ROOT).free>=54*1024**3
  out=OUT/phase['id'];out.mkdir();target=Path(phase['target']);target.mkdir()
  env=old.env();env['CARGO_TARGET_DIR']=str(target)
  forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}
  assert not {k:v for k,v in env.items() if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_') or (k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
  cmd=['cargo','test','--release','--locked','--offline','-p','solver','--features',phase['features'],'--lib']
  if phase['integration']:cmd+=['--test','postflop_autoresearch']
  cmd+=['--no-run','--message-format=json']
  fault=None
  try:
   for n,v in P['owned'].items():
    shutil.copyfile(v['candidate'],REPO/n);shutil.copyfile(v['candidate'],out/Path(n).name)
   candidate_guard()
   old.child(cmd,out,'cargo',env,1800)
   verify();candidate_guard()
   records=[json.loads(x) for x in (out/'cargo.stdout.log').read_text(encoding='utf-8').splitlines()]
   assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in records)
   artifacts=[x for x in records if x.get('reason')=='compiler-artifact']
   for x in artifacts:
    for f in x.get('filenames',[])+([x['executable']] if x.get('executable') else []):assert Path(f).resolve().is_relative_to(target.resolve())
   deps={f:old.sha(f) for x in artifacts for f in x.get('filenames',[]) if Path(f).is_file() and Path(f).suffix in ['.rlib','.rmeta','.lib','.dll']}
   tests=[x for x in artifacts if x.get('profile',{}).get('test') and x.get('executable') and x['target']['name'] in phase['outputs']]
   assert len(tests)==len(phase['outputs']) and {x['target']['name'] for x in tests}==set(phase['outputs'])
   pins={}
   for x in tests:
    assert x['fresh'] is False and x['features']==phase['expected_features']
    name=x['target']['name'];binary=ROOT/'binaries'/(phase['outputs'][name]+'.exe')
    expected_src=REPO/('crates/solver/src/lib.rs' if name=='solver' else 'crates/solver/tests/postflop_autoresearch.rs')
    assert Path(x['target']['src_path']).resolve()==expected_src.resolve()
    assert (REPO/'crates/solver/src/gpu/kernels.cu').read_bytes() in Path(x['executable']).read_bytes()
    shutil.copyfile(x['executable'],binary)
    manifest={**old.ar.source_identity(),'candidate':'E042','phase':phase['id'],'binary_sha256':old.sha(binary),'built_at':old.now(),'build_command':cmd,'cargo_artifact':x,'dependency_artifact_sha256':deps,'source_copies':{n:{'path':str(out/Path(n).name),'sha256':v['candidate_sha256']} for n,v in P['owned'].items()},'build_log_sha256':old.sha(out/'cargo.stdout.log'),'build_protocol_sha256':sys.argv[1],'build_script_sha256':old.sha(HERE/'build.py'),'candidate_accepted':False,'control_only':phase['id']=='feature'}
    old.save(binary.with_suffix('.manifest.json'),manifest)
    pins[str(binary)]=old.sha(binary);pins[str(binary.with_suffix('.manifest.json'))]=old.sha(binary.with_suffix('.manifest.json'))
   old.save(out/'complete.json',{'at':old.now(),'source_sha256':BASE|{n:v['candidate_sha256'] for n,v in P['owned'].items()},'command':cmd,'returncode':0,'artifact_sha256':pins,'dependency_sha256':deps,'stdout_sha256':old.sha(out/'cargo.stdout.log'),'stderr_sha256':old.sha(out/'cargo.stderr.log'),'native_executions':0})
  except BaseException as exc:
   fault=repr(exc)
   old.save(out/'failure.json',{'at':old.now(),'error':fault,'native_executions':0})
   raise
  finally:
   for n,v in P['owned'].items():
    assert old.sha(REPO/n) in [v['base_sha256'],v['candidate_sha256']]
    shutil.copyfile(v['base'],REPO/n)
   old.custody()
   old.save(out/'restoration.json',{'at':old.now(),'accepted162_restored':True,'main_live_ptx_unchanged':True,'error':fault})
  print(phase['id'],'terminal; accepted E020 restored.',flush=True)
 old.save(OUT/'complete.json',{'at':old.now(),'all_compilers_terminal':True,'native_executions':0,'build_protocol_sha256':sys.argv[1],'evidence_sha256':{str(p):old.sha(p) for p in OUT.rglob('*.json')}})
print('E042 final builds complete; no native work ran.',flush=True)
