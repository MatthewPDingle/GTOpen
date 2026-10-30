import sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();H=ROOT/'runs/E052-kernel-control';src=(H/'probe.rs').read_text();assert '&&c["profile"]!="all_zero" {assert!(nz>0' in src
src=src.replace('&&c["profile"]!="all_zero" {assert!(nz>0','&&c["profile"]!="all_zero"&&c["profile"]!="stress_signed_zero" {assert!(nz>0')
(H/'probe-r2.rs').write_text(src,encoding='utf-8',newline='\n')
old.save(H/'prelaunch-host-check-repair.json',{'at':old.now(),'native_executions':0,'reason':'All-signed-zero stress deliberately has zero payoffs; inherited finite-nonzero anti-vacuity condition must exempt its explicit profile. Every328case and all exact output/input/guard tests retained. Original first probe source preserved.','old_probe_sha256':old.sha(H/'probe.rs'),'new_probe_sha256':old.sha(H/'probe-r2.rs')})
resource=old.read(ROOT/'runs/E052-resource/protocol.json');cmd=list(resource['rustc_command']);cmd[1]=str(H/'probe-r2.rs');cmd[-1]=str(H/'probe.exe')
runner=ROOT/'runs/E052-execute-controls.py';data={'id':'E052-kernel-control-execution','at':old.now(),'status':'FROZEN_BEFORE_ANY_LAUNCH','rustc_command':cmd,'protocol_sha256':old.sha(H/'protocol.json'),'input_sha256':{str(p):old.sha(p) for p in H.iterdir() if p.is_file()}|{str(runner):old.sha(runner)}|{p:h for p,h in resource['input_sha256'].items() if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']},'cases':328,'same128threads_each':True,'same_float_order':True,'performance_measured':False,'candidate_accepted':False};old.save(H/'execution-plan.json',data)
for p in [H/'probe-r2.rs',H/'prelaunch-host-check-repair.json',H/'execution-plan.json',runner]:
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
print(old.sha(H/'execution-plan.json'),flush=True)
