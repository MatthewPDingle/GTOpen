import subprocess,sys
from pathlib import Path
root=Path(r'X:\Dev\GTOpen-gpu-research-20261016');bins=Path(r'S:\GTOpen-research\postflop-gpu-20261016\binaries')
for run,kind,candidate in [('E014R2','candidate',True),('B033','baseline',False),('B034','baseline',False),('E014R3','candidate',True)]:
 name=('E014' if candidate else 'E004')+'-postflop_autoresearch'
 cmd=[sys.executable,'tools/postflop_autoresearch.py','--id',run,'--title','Direct-three action repeated pair' if candidate else 'E004 reference repeated pair','--kind',kind,'--binary',str(bins/(name+'.exe')),'--build-manifest',str(bins/(name+'.manifest.json')),'--test','postflop_complete_cycle']
 subprocess.run(cmd,cwd=root,check=True)
