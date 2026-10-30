import subprocess,sys,os
from pathlib import Path
root=Path(r'X:\Dev\GTOpen-gpu-research-20261016');bulk=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
env=os.environ.copy()
for key in list(env):
 if key.startswith('POSTFLOP_AUTORESEARCH_'):env.pop(key)
env['POSTFLOP_AUTORESEARCH_PROFILE']='1'
for rid in ['D020','D020R2','D020R3']:
 subprocess.run([sys.executable,'tools/postflop_autoresearch.py','--id',rid,'--title','E004 diagnostic kernel profile after exact scoring','--kind','diagnostic','--binary',str(bulk/'binaries/E004-postflop_autoresearch.exe'),'--build-manifest',str(bulk/'binaries/E004-postflop_autoresearch.manifest.json'),'--test','postflop_complete_cycle'],cwd=root,env=env,check=True)
