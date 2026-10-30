import subprocess,sys
from pathlib import Path
root=Path(r'X:\Dev\GTOpen-gpu-research-20261016');bins=Path(r'S:\GTOpen-research\postflop-gpu-20261016\binaries')
for run,kind,candidate in [('B035','baseline',False),('E015','candidate',True),('E015R2','candidate',True),('B036','baseline',False),('B037','baseline',False),('E015R3','candidate',True)]:
 name=('E015' if candidate else 'E004')+'-postflop_autoresearch'
 cmd=[sys.executable,'tools/postflop_autoresearch.py','--id',run,'--title','Paired player reach reuse' if candidate else 'E004 reference for paired reach reuse','--kind',kind,'--binary',str(bins/(name+'.exe')),'--build-manifest',str(bins/(name+'.manifest.json')),'--test','postflop_complete_cycle']
 subprocess.run(cmd,cwd=root,check=True)
