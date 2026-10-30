import sys,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();P=old.read(H/'build-plan.json');B=H/'build-r2'
old.save(H/'build/terminal.json',{'at':old.now(),'returncode':1,'failure':'Popen list quoting preserved literal backslash quotes in cmd /c argument; vcvars did not start, no compiler or native execution.','native_executions':0})
script=(H/'build.py').read_text().replace("'build-plan.json'","'build-plan-r2.json'").replace("child(['cmd.exe','/d','/c',cmd],'collector',180)","child('cmd.exe /d /s /c \"'+cmd+'\"','collector',180)")
dest=H/'build-r2.py';dest.write_text(script,encoding='utf-8',newline='\n');oldB=P['build_dir'];P.update(id='D085-build-r2',at=old.now(),build_dir=str(B),private_dll_dirs=[str(B),P['private_dll_dirs'][1]],repair='Pass cmd.exe command as raw Windows command line so nested vcvars/cl quotes follow CMD parsing, not C argv escaping. No source/native change.')
for k in ['collector_command','ability_command']:P[k]=[s.replace(oldB,str(B)) for s in P[k]]
P['input_sha256']|={str(p):old.sha(p) for p in [dest,H/'build.py',H/'build-plan.json',*list((H/'build').glob('*'))] if p.is_file()};old.save(H/'build-plan-r2.json',P)
for p in [dest,H/'build-plan-r2.json',H/'build/terminal.json']:
 key=H.name+'/'+p.relative_to(H).as_posix();d=old.ar.DASHBOARD/'evidence'/key;d.parent.mkdir(parents=True,exist_ok=True);assert not d.exists();d.write_bytes(p.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
print(old.sha(H/'build-plan-r2.json'),flush=True)
