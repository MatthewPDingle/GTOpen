import os,sys,subprocess
from pathlib import Path
root=Path('S:/GTOpen-research/postflop-gpu-20261016')
runner=Path('tools/postflop_autoresearch.py').resolve()
env=os.environ.copy()
for key in ['POSTFLOP_AUTORESEARCH_CONSTRUCTOR_PROFILE','POSTFLOP_AUTORESEARCH_QUANTIZED_INIT_PROFILE','POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE']:
 env.pop(key,None)
for fixture,short in [('two-tone','T'),('river','R')]:
 for rep in [1,2,3]:
  for kind in (['B','C'] if rep!=2 else ['C','B']):
   binary='E004' if kind=='B' else 'E010'
   identity=f'D013-{short}{kind}{rep}'
   args=[sys.executable,str(runner),'--id',identity,'--title',f'Isolated {fixture}, {binary}, repetition {rep}','--kind','diagnostic','--binary',str(root/f'binaries/{binary}-postflop_autoresearch.exe'),'--build-manifest',str(root/f'binaries/{binary}-postflop_autoresearch.manifest.json'),'--test','postflop_complete_cycle','--fixture',fixture]
   result=subprocess.run(args,env=env)
   if result.returncode:sys.exit(result.returncode)
