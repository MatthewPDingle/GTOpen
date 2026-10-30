"""E040 draft compile only, restoring both accepted sources before release."""
import json,sys,os,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2;old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
ROOT=old.ROOT;REPO=old.REPO;BASE=P['accepted_source_sha256'];OUT=ROOT/'runs/E040-cpu-check-build';target=Path(P['target'])
for p,h in P['input_sha256'].items():old.pin(p,h)
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3
 assert not OUT.exists() and not target.exists();OUT.mkdir();target.mkdir();fault=None
 try:
  for name,v in P['owned'].items():shutil.copyfile(v['candidate'],REPO/name);shutil.copyfile(v['candidate'],OUT/Path(name).name)
  expected=BASE|{name:v['candidate_sha256'] for name,v in P['owned'].items()}
  assert old.ar.source_identity()['source_sha256']==expected
  e=old.env();e['CARGO_TARGET_DIR']=str(target)
  forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}
  assert not {k:v for k,v in e.items() if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_') or (k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
  cmd=['cargo','test','--release','--locked','--offline','-p','solver','--features','gpu','--lib','--no-run','--message-format=json']
  old.child(cmd,OUT,'cargo',e,1800)
  assert old.ar.source_identity()['source_sha256']==expected
  records=[json.loads(x) for x in (OUT/'cargo.stdout.log').read_text(encoding='utf-8').splitlines()]
  assert any(x.get('reason')=='build-finished' and x.get('success') for x in records)
  tests=[x for x in records if x.get('reason')=='compiler-artifact' and x.get('target',{}).get('name')=='solver' and x.get('profile',{}).get('test') and x.get('executable')]
  assert len(tests)==1 and tests[0]['features']==['gpu'] and tests[0]['fresh'] is False
  artifact=tests[0];original=Path(artifact['executable']);assert original.resolve().is_relative_to(target.resolve())
  binary=ROOT/'binaries/E040-cpu-check-solver.exe';assert not binary.exists();shutil.copyfile(original,binary)
  manifest={**old.ar.source_identity(),'candidate':'E040 CPU layout check draft','binary_sha256':old.sha(binary),'built_at':old.now(),'build_command':cmd,'cargo_artifact':artifact,'source_copies':{name:{'path':str(OUT/Path(name).name),'sha256':v['candidate_sha256']} for name,v in P['owned'].items()},'build_log_sha256':old.sha(OUT/'cargo.stdout.log'),'protocol_sha256':sys.argv[1],'draft_only':True,'not_a_performance_binary':True}
  old.save(binary.with_suffix('.manifest.json'),manifest)
  old.save(OUT/'complete.json',{'at':old.now(),'binary':str(binary),'binary_sha256':old.sha(binary),'manifest_sha256':old.sha(binary.with_suffix('.manifest.json')),'source_sha256':expected,'protocol_sha256':sys.argv[1],'native_executions':0})
 except BaseException as exc:fault=repr(exc);raise
 finally:
  for name,v in P['owned'].items():
   assert old.sha(REPO/name) in [v['base_sha256'],v['candidate_sha256']]
   shutil.copyfile(v['base'],REPO/name)
  old.custody();old.save(OUT/'restoration.json',{'at':old.now(),'accepted162_restored':True,'main_live_ptx_unchanged':True,'error':fault})
print('CPU-check compile terminal; both accepted files restored. No native test ran.',flush=True)
