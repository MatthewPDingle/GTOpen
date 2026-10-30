import json,sys,subprocess,os,shutil
from pathlib import Path
root=Path(r'X:\Dev\GTOpen-gpu-research-20261016');sys.path.insert(0,str(root/'tools'));import postflop_autoresearch as ar
before=ar.source_identity();frozen=json.loads((ar.RESEARCH/'binaries/E015-postflop_autoresearch.manifest.json').read_text());assert before['source_sha256']==frozen['source_sha256']
log=ar.RESEARCH/'runs/E015-controls-build.jsonl';err=ar.RESEARCH/'runs/E015-controls-build.stderr.log';assert not log.exists()
targets=['postflop_state_perf','postflop_action_menus','postflop_resume_state','gpu']
cmd=['cargo','test','--release','-p','solver','--features','gpu']
for t in targets:cmd.extend(['--test',t])
cmd+=['--no-run','--message-format=json'];env=os.environ.copy();env['CARGO_TARGET_DIR']=str(ar.RESEARCH/'build');env['RAYON_NUM_THREADS']='16'
print('Building E015 broader controls from unchanged candidate source',flush=True)
with log.open('wb') as out,err.open('wb') as error:r=subprocess.run(cmd,cwd=root,env=env,stdout=out,stderr=error)
if r.returncode:print(err.read_text());raise SystemExit(r.returncode)
assert ar.source_identity()['source_sha256']==before['source_sha256']
found=[]
for line in log.read_text().splitlines():
 try:d=json.loads(line)
 except json.JSONDecodeError:continue
 if d.get('reason')=='compiler-artifact' and d.get('profile',{}).get('test') and d.get('executable') and d['target']['name'] in targets:
  name=d['target']['name'];dest=ar.RESEARCH/'binaries'/f'E015-{name}.exe';assert not dest.exists();shutil.copyfile(d['executable'],dest)
  ar.atomic_json(dest.with_suffix('.manifest.json'),{**before,'binary_sha256':ar.sha256(dest),'built_at':ar.now(),'build_command':cmd,'build_log':str(log),'build_log_sha256':ar.sha256(log),'build_stderr_log':str(err),'candidate':'E015','source_matches_primary_binary':True,'primary_manifest':str(ar.RESEARCH/'binaries/E015-postflop_autoresearch.manifest.json'),'source_matches_prebuild':True})
  found.append(name);print(name,ar.sha256(dest),flush=True)
assert set(found)==set(targets)
