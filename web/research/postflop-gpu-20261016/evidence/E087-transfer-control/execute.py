import sys,json,shutil,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 old.custody();old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
verify();O=H/'execution';O.mkdir(exist_ok=False)
assert not(H/'probe.exe').exists() and not(H/'output').exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status())
 assert shutil.disk_usage('S:\\').free>=98*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
 uuid=subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip()
 assert uuid=='GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee'
 old.child(P['rustc_command'],O,'rustc',old.env(),1200);verify()
 old.save(O/'binary.json',{'sha256':old.sha(H/'probe.exe'),'at':old.now()})
 old.child([str(H/'probe.exe'),str(H/'output')],O,'probe',old.env(),1800);verify()
 old.child([sys.executable,str(H/'audit.py')],O,'audit',old.env(),900);verify()
 old.save(O/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'binary_sha256':old.sha(H/'probe.exe'),'GPU_raw_control_audit_sha256':old.sha(R/'comparisons/E087-transfer-control/report.json'),'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'performance_measurement':False,'candidate_accepted':False})
 print('E087 raw GPU transfer controls completed and independently read',flush=True)
