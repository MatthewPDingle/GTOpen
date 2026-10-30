import subprocess,sys
from pathlib import Path
root=Path(r'X:\Dev\GTOpen-gpu-research-20261016');bins=Path(r'S:\GTOpen-research\postflop-gpu-20261016\binaries')
for run,kind,candidate in [('B041','baseline',False),('E016','candidate',True),('E016R2','candidate',True),('B042','baseline',False),('B043','baseline',False),('E016R3','candidate',True)]:
 name=('E016' if candidate else 'E015')+'-postflop_autoresearch'
 cmd=[sys.executable,'tools/postflop_autoresearch.py','--id',run,'--title','Cross-iteration player-0 reach reuse' if candidate else 'E015 reference for cross-iteration reach reuse','--kind',kind,'--binary',str(bins/(name+'.exe')),'--build-manifest',str(bins/(name+'.manifest.json')),'--test','postflop_complete_cycle']
 subprocess.run(cmd,cwd=root,check=True)
