import sys,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E091-raw-control';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();assert not(H/'probe.exe').exists()and not(H/'output').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid']in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'performance_measurement':False})
 h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
 h.child([str(H/'probe.exe'),str(H/'output')],O,'probe',1200);verify()
 markers=[json.loads(x.split('E091_RAW ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E091_RAW 'in x];assert len(markers)==P['cases']+1 and markers[-1]['stage']=='complete';assert[m['case']for m in markers[:-1]]==h.read(H/'corpus.json');assert markers[-1]['cases']==P['cases']
 files={str(p):h.sha(p)for p in(H/'output').iterdir()};assert len(files)==5 and sum(p.stat().st_size for p in(H/'output').iterdir())<=P['raw_reservation_bytes']
 h.save(O/'native-complete.json',{'at':h.now(),'all_native_children_terminal':True,'last_marker':markers[-1],'raw_sha256':files,'protocol_sha256':sys.argv[1]})
h.child([sys.executable,str(ROOT/'runs/E091-raw-audit.py')],O,'audit',600);verify();h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(ROOT/'comparisons/E091-raw-control/report.json'),'source_main_live_PTX_custody_pass':True,'performance_measurement':False});print('E091 finite raw controls and reader passed.',flush=True)
