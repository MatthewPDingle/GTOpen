import os,subprocess,sys
from pathlib import Path
root=Path(r'X:\Dev\GTOpen-gpu-research-20261016');bins=Path(r'S:\GTOpen-research\postflop-gpu-20261016\binaries')
controls=[('V015-state','E015-postflop_state_perf','postflop_states',False,None),('V015-menu','E015-postflop_action_menus','postflop_action_menus',False,None),('V015-resume','E015-postflop_resume_state','postflop_resume_state',False,None),('V015-gpu','E015-gpu','*',True,None),('V015-f32-reference','E004-postflop_autoresearch','postflop_complete_cycle',False,'f32'),('V015-f32-candidate','E015-postflop_autoresearch','postflop_complete_cycle',False,'f32')]
for identity,name,test,ordinary,storage in controls:
 env=os.environ.copy()
 for key in ['POSTFLOP_AUTORESEARCH_PROFILE','POSTFLOP_AUTORESEARCH_FIXTURE','POSTFLOP_AUTORESEARCH_STORAGE']:env.pop(key,None)
 if storage:env['POSTFLOP_AUTORESEARCH_STORAGE']=storage
 cmd=[sys.executable,'tools/postflop_autoresearch.py','--id',identity,'--title','E015 broader correctness qualification','--kind','validation','--binary',str(bins/(name+'.exe')),'--build-manifest',str(bins/(name+'.manifest.json')),'--test',test]
 if ordinary:cmd.append('--not-ignored')
 subprocess.run(cmd,cwd=root,env=env,check=True)
