"""Refresh accepted E015 diagnostic profiles; no qualifying timings."""
import subprocess,sys,os
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
binary=ar.RESEARCH/'binaries/E015-postflop_autoresearch.exe'
assert ar.sha256(binary)=='37e09be0b3d2ec66db6b49e13e09aa468a487218bd0215306f025bf7ca226eda'
out=ar.RESEARCH/'runs/D029-profile-plan';out.mkdir(exist_ok=False)
ar.atomic_json(out/'protocol.json',{'at':ar.now(),'runs':['D029','D029R2','D029R3'],
 'binary':str(binary),'binary_sha256':ar.sha256(binary),'purpose':'Refresh source-hypothesis priorities after E015 paired reach reuse; separate from E017 qualification.',
 'limits':'Extra iteration after scoring/fingerprint. Synchronized eager host spans, not ordinary graph device-time shares. All diagnostic complete-cycle times excluded from acceptance; E017 source may be under editing, but preserved E015 build manifest identifies executed code.'})
env=os.environ.copy()
for key in list(env):
 if key.startswith('POSTFLOP_AUTORESEARCH_'):env.pop(key)
env['POSTFLOP_AUTORESEARCH_PROFILE']='1'
for identity in ['D029','D029R2','D029R3']:
 subprocess.run([sys.executable,'tools/postflop_autoresearch.py','--id',identity,'--title','Accepted E015 diagnostic profile after scoring','--kind','diagnostic',
  '--binary',str(binary),'--build-manifest',str(binary.with_suffix('.manifest.json')),'--test','postflop_complete_cycle'],cwd=repo,env=env,check=True)
ar.atomic_json(out/'completed.json',{'at':ar.now(),'runs':3,'scope':'Diagnostic only; no candidate or gain accepted'})
print('D029 profiles completed.',flush=True)
