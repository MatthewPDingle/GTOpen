"""One frozen local-host configuration pair; no tracked file mutation."""
import json,os,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2

provided_hash=sys.argv[1];A=ROOT/'runs/E098-build-log-adapter';AP=h.read(A/'protocol.json');h.pin(A/'protocol.json',provided_hash)
for path,digest in AP['input_sha256'].items():h.pin(path,digest)
sys.argv[1]=AP['original_build_protocol_sha256']
H=ROOT/'runs/E098-build-plan';P=h.read(H/'protocol.json');O=ROOT/'runs/E098-final-build'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();assert O.is_dir()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
 for arm in P['arms']:
  target=Path(arm['target']);assert target.exists()==(arm['id']=='default')
  for stem in arm['outputs'].values():assert not(ROOT/'binaries'/(stem+'.exe')).exists()
 for arm in P['arms']:
  verify();h.ar.refuse_active(h.ar.live_status());out=O/arm['id'];target=Path(arm['target'])
  if arm['id']=='default':assert out.is_dir() and target.is_dir()
  else:out.mkdir();target.mkdir()
  assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
  env=h.env();forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET','CARGO_TARGET_DIR'}
  assert not{k:v for k,v in env.items() if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_') or(k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
  cmd=['cargo','test','--release','--locked','--offline','--target-dir',str(target),'-p','solver','--features','gpu','--lib','--test','postflop_autoresearch','--no-run','--message-format=json','-vv']
  if arm['id']=='default':assert h.read(out/'build-environment.json')['command']==cmd
  else:h.save(out/'build-environment.json',{'at':h.now(),'only_extra_compiler_flags':arm['rustc_flags'],'source_sha256':P['accepted_source_sha256'],'command':cmd})
  try:
   if arm['rustc_flags']:os.environ['CARGO_ENCODED_RUSTFLAGS']='\x1f'.join(arm['rustc_flags'])
   if arm['id']=='default':
    receipt=h.read(out/'cargo.exit.json');assert receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
   else:h.child(cmd,out,'cargo',1800)
  finally:
   if arm['rustc_flags']:os.environ.pop('CARGO_ENCODED_RUSTFLAGS',None)
   h.custody()
   if arm['id']=='default':assert h.read(out/'restoration.json')['source_main_live_PTX_unchanged']
   else:h.save(out/'restoration.json',{'at':h.now(),'source_main_live_PTX_unchanged':True,'process_only_rustflags_removed':not os.environ.get('CARGO_ENCODED_RUSTFLAGS')})
  verify();lines=(out/'cargo.stdout.log').read_text(encoding='utf-8').splitlines();records=[];buildscript_lines=[]
  for line in lines:
   if line.startswith('{'):records.append(json.loads(line))
   else:
    assert __import__('re').match(r'^\[[A-Za-z0-9_.-]+ [^\]]+\] ',line),repr(line);buildscript_lines.append(line)
  h.save(out/'log-format-audit.json',{'structured_records':len(records),'verbose_prefixed_buildscript_lines':len(buildscript_lines),'all_lines_accounted':True,'original_compiler_reused':arm['id']=='default','adapter_protocol_sha256':provided_hash})
  assert any(x.get('reason')=='build-finished' and x.get('success') for x in records)
  stderr=(out/'cargo.stderr.log').read_text(encoding='utf-8');assert ('-C target-cpu=znver3' in stderr)==bool(arm['rustc_flags'])
  artifacts=[x for x in records if x.get('reason')=='compiler-artifact'];dependencies={}
  for record in artifacts:
   for path in record.get('filenames',[])+([record['executable']] if record.get('executable') else []):
    path=Path(path);assert path.resolve().is_relative_to(target.resolve())
    if path.is_file() and path.suffix in ['.rlib','.rmeta','.lib','.dll']:dependencies[str(path)]=h.sha(path)
  tests=[x for x in artifacts if x.get('profile',{}).get('test') and x.get('executable') and x['target']['name'] in arm['outputs']];assert len(tests)==2 and {x['target']['name'] for x in tests}==set(arm['outputs']);pins={}
  for record in tests:
   assert record['fresh'] is False and record['features']==['gpu'];name=record['target']['name'];binary=ROOT/'binaries'/(arm['outputs'][name]+'.exe');data=Path(record['executable']).read_bytes();assert (h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes() in data
   shutil.copyfile(record['executable'],binary);manifest={**h.ar.source_identity(),'candidate':'E098','arm':arm['id'],'measurement_epoch':'RAM20261028','binary_sha256':h.sha(binary),'built_at':h.now(),'build_command':cmd,'rustc_flags':arm['rustc_flags'],'cargo_artifact':record,'dependency_artifact_sha256':dependencies,'build_log_sha256':h.sha(out/'cargo.stdout.log'),'verbose_stderr_sha256':h.sha(out/'cargo.stderr.log'),'build_protocol_sha256':sys.argv[1],'build_script_sha256':h.sha(__file__),'build_adapter_protocol_sha256':provided_hash,'candidate_accepted':False,'hardware_scope':'Ryzen5950X/znver3 local host only; portable default retained; no runtime/global flags changed.'};h.save(binary.with_suffix('.manifest.json'),manifest)
   for p in [binary,binary.with_suffix('.manifest.json')]:pins[str(p)]=h.sha(p)
  h.save(out/'complete.json',{'at':h.now(),'artifact_sha256':pins,'dependency_sha256':dependencies,'source_sha256':P['accepted_source_sha256'],'only_flags':arm['rustc_flags'],'all_compilers_terminal':True,'GPU_kernel_or_solver_runs':0});print(arm['id'],'fresh build terminal; source unchanged.',flush=True)
 h.save(O/'complete.json',{'at':h.now(),'all_compilers_terminal':True,'native_solver_or_GPU_runs':0,'build_protocol_sha256':sys.argv[1],'evidence_sha256':{str(p):h.sha(p) for p in O.rglob('*.json')}})
print('E098 default/znver3 builds complete; no speed claim.',flush=True)
