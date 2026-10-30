"""Freeze E014 direct-three action kernel and its native test artifacts."""
import json,os,sys,subprocess,shutil
from pathlib import Path
ROOT=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(ROOT/'tools'));import postflop_autoresearch as ar
os.chdir(ROOT)
raw=ar.RESEARCH/'runs';log=raw/'E014-build.jsonl';err=raw/'E014-build.stderr.log';assert not log.exists()
before=ar.source_identity();ar.atomic_json(raw/'E014-source-before-build.json',before)
assert before['benchmark_sha256']['crates/solver/tests/postflop_autoresearch.rs']=='f13d79410a22f140c05cb9a822fe9685c2180e5baeda4b625d52ae03feeBD327'.lower()
patch=raw/'E014.patch';assert not patch.exists()
patch.write_bytes(subprocess.check_output(['git','diff','--binary','HEAD','--','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/plan.rs','crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/continuation_capacity.rs']))
copies=raw/'E014-source';copies.mkdir()
for name in ['mod.rs','plan.rs','kernels.cu','continuation_capacity.rs']:shutil.copyfile(ROOT/'crates/solver/src/gpu'/name,copies/name)
env=os.environ.copy();env['CARGO_TARGET_DIR']=str(ar.RESEARCH/'build');env['RAYON_NUM_THREADS']='16'
command=['cargo','test','--release','-p','solver','--features','gpu','--lib','--test','postflop_autoresearch','--no-run','--message-format=json']
print('Building E014 with frozen harness and source',flush=True)
with log.open('wb') as out,err.open('wb') as stderr: result=subprocess.run(command,stdout=out,stderr=stderr,env=env)
if result.returncode:
 print(err.read_text(errors='replace'));raise SystemExit(result.returncode)
after=ar.source_identity();assert before['source_sha256']==after['source_sha256'],'source changed during build'
artifacts=[]
for line in log.read_text(errors='replace').splitlines():
 try:d=json.loads(line)
 except json.JSONDecodeError:continue
 if d.get('reason')=='compiler-artifact' and d.get('profile',{}).get('test') and d.get('executable') and d['target']['name'] in ['solver','postflop_autoresearch']:
  name=d['target']['name'];destination=ar.RESEARCH/'binaries'/f'E014-{name}.exe';assert not destination.exists();shutil.copyfile(d['executable'],destination)
  manifest={'binary_sha256':ar.sha256(destination),'built_at':ar.now(),**before,'build_command':command,'build_log':str(log),'build_log_sha256':ar.sha256(log),'build_stderr_log':str(err),'patch':str(patch),'patch_sha256':ar.sha256(patch),'source_copies':str(copies),'source_matches_prebuild':True,'candidate':'E014','change':'Stable same-level direct-three action partition and unchanged arithmetic in dedicated kernel'}
  ar.atomic_json(destination.with_suffix('.manifest.json'),manifest);artifacts.append(name);print(name,manifest['binary_sha256'],flush=True)
assert set(artifacts)=={'solver','postflop_autoresearch'},artifacts
print('E014 build frozen.',flush=True)
