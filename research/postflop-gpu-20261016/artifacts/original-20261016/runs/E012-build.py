"""Freeze E012 private SSE4.1 host encoder and its native test artifacts."""
import json,os,sys,subprocess,shutil
from pathlib import Path
ROOT=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(ROOT/'tools'));import postflop_autoresearch as ar
os.chdir(ROOT)
raw=ar.RESEARCH/'runs';log=raw/'E012-build.jsonl';err=raw/'E012-build.stderr.log';assert not log.exists()
before=ar.source_identity();ar.atomic_json(raw/'E012-source-before-build.json',before)
assert before['benchmark_sha256']['crates/solver/tests/postflop_autoresearch.rs']=='f13d79410a22f140c05cb9a822fe9685c2180e5baeda4b625d52ae03feeBD327'.lower()
patch=raw/'E012.patch';assert not patch.exists()
patch.write_bytes(subprocess.check_output(['git','diff','--binary','HEAD','--','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/arena.rs']))
copies=raw/'E012-source';copies.mkdir()
for name in ['mod.rs','arena.rs','host_encode.rs']:shutil.copyfile(ROOT/'crates/solver/src/gpu'/name,copies/name)
env=os.environ.copy();env['CARGO_TARGET_DIR']=str(ar.RESEARCH/'build');env['RAYON_NUM_THREADS']='16'
command=['cargo','test','--release','-p','solver','--features','gpu','--lib','--test','postflop_autoresearch','--no-run','--message-format=json']
print('Building E012 with frozen harness and source',flush=True)
with log.open('wb') as out,err.open('wb') as stderr: result=subprocess.run(command,stdout=out,stderr=stderr,env=env)
if result.returncode:
 print(err.read_text(errors='replace'));raise SystemExit(result.returncode)
after=ar.source_identity();assert before['source_sha256']==after['source_sha256'],'source changed during build'
artifacts=[]
for line in log.read_text(errors='replace').splitlines():
 try:d=json.loads(line)
 except json.JSONDecodeError:continue
 if d.get('reason')=='compiler-artifact' and d.get('profile',{}).get('test') and d.get('executable') and d['target']['name'] in ['solver','postflop_autoresearch']:
  name=d['target']['name'];destination=ar.RESEARCH/'binaries'/f'E012-{name}.exe';assert not destination.exists();shutil.copyfile(d['executable'],destination)
  manifest={'binary_sha256':ar.sha256(destination),'built_at':ar.now(),**before,'build_command':command,'build_log':str(log),'build_log_sha256':ar.sha256(log),'build_stderr_log':str(err),'patch':str(patch),'patch_sha256':ar.sha256(patch),'source_copies':str(copies),'source_matches_prebuild':True,'candidate':'E012','change':'Runtime-gated SSE4.1 for the original encoder only in GPU host readback'}
  ar.atomic_json(destination.with_suffix('.manifest.json'),manifest);artifacts.append(name);print(name,manifest['binary_sha256'],flush=True)
assert set(artifacts)=={'solver','postflop_autoresearch'},artifacts
print('E012 build frozen.',flush=True)
