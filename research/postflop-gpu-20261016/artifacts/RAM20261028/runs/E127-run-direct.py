"""One frozen compiler/first-application-kernel process/complete raw reader."""
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E127-direct';P=h.read(H/'protocol.json');O=H/'execution'
assert len(sys.argv)==2
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
verify();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'])
    assert gpu['stdout']==h.read(ROOT/'runs/E127-resource/execution/before.json')['GPU']['stdout']
    h.save(O/'before.json',{'at':h.now(),'GPU':gpu,'X_free_bytes':shutil.disk_usage(ROOT).free})
    h.child(P['rustc_command'],O,'rustc',300);verify()
    h.child([str(H/'probe.exe'),str(O/'raw')],O,'native',1200);verify()
    assert sum(p.stat().st_size for p in(O/'raw').iterdir())==P['expected_raw_bytes']
    h.child([sys.executable,str(ROOT/'runs/E127-read-direct.py'),sys.argv[1]],O,'reader',1200);verify()
print(json.dumps({'report_sha256':h.sha(H/'report.json'),'solver_speed_samples':0}),flush=True)
