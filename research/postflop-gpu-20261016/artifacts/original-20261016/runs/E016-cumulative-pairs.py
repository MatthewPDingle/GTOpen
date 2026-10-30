import subprocess,sys
from pathlib import Path
root=Path(r'X:\Dev\GTOpen-gpu-research-20261016');bins=Path(r'S:\GTOpen-research\postflop-gpu-20261016\binaries')
for run,kind,candidate in [('B044','baseline',False),('E016C1','candidate',True),('E016C2','candidate',True),('B045','baseline',False),('B046','baseline',False),('E016C3','candidate',True)]:
 name='E016-postflop_autoresearch' if candidate else 'baseline-complete'
 cmd=[sys.executable,'tools/postflop_autoresearch.py','--id',run,'--title','E016 cumulative comparison' if candidate else 'Original implementation fresh cumulative reference','--kind',kind,'--binary',str(bins/(name+'.exe')),'--build-manifest',str(bins/(name+'.manifest.json')),'--test','postflop_complete_cycle']
 subprocess.run(cmd,cwd=root,check=True)
