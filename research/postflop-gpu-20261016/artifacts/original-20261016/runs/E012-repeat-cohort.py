"""Finish the alternating E004/E012 cohort using already frozen executables."""
import subprocess,sys,os
from pathlib import Path
root=Path(r'X:\Dev\GTOpen-gpu-research-20261016');bulk=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
env=os.environ.copy()
for k in list(env):
 if k.startswith('POSTFLOP_AUTORESEARCH_'):env.pop(k)
for rid,binid,kind in [('E012R2','E012','candidate'),('B027','E004','baseline'),('B028','E004','baseline'),('E012R3','E012','candidate')]:
 command=[sys.executable,'tools/postflop_autoresearch.py','--id',rid,'--title',f'{binid} SSE4.1 readback cohort {rid}','--kind',kind,'--binary',str(bulk/'binaries'/f'{binid}-postflop_autoresearch.exe'),'--build-manifest',str(bulk/'binaries'/f'{binid}-postflop_autoresearch.manifest.json'),'--test','postflop_complete_cycle']
 subprocess.run(command,cwd=root,env=env,check=True)
