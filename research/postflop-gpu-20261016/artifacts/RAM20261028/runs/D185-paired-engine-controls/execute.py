import sys, shutil
from pathlib import Path
H = Path(__file__).resolve().parent
ROOT = H.parent.parent
sys.path.insert(0, str(ROOT/'epoch'))
import common as h
assert len(sys.argv) == 2
h.pin(H/'protocol.json', sys.argv[1])
P = h.read(H/'protocol.json')
def verify():
    h.custody()
    h.pin(H/'protocol.json', sys.argv[1])
    for p, digest in P['input_sha256'].items(): h.pin(p, digest)
verify()
O = H/'execution'
O.mkdir(exist_ok=False)
assert not (H/'probe.exe').exists() and not (H/'output').exists()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    assert shutil.disk_usage(ROOT).free >= P['required_free_bytes']
    gpu = h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'])
    assert gpu['returncode'] == 0 and 'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee' in gpu['stdout']
    h.save(O/'before.json', {'at':h.now(), 'GPU':gpu, 'performance_measurement':False})
    h.child(P['rustc_command'], O, 'rustc', 1200)
    verify()
    h.save(O/'binary.json', {'at':h.now(), 'sha256':h.sha(H/'probe.exe')})
    h.child([str(H/'probe.exe'), str(H/'output')], O, 'probe', 1800)
    verify()
    h.child([sys.executable, str(H/'audit.py')], O, 'audit', 1800)
    verify()
    h.save(O/'complete.json', {'at':h.now(), 'protocol_sha256':sys.argv[1], 'all_owned_children_terminal':True, 'source_main_live_PTX_custody_pass':True, 'report_sha256':h.sha(ROOT/'comparisons/D185-paired-engine-controls/report.json'), 'performance_measurement':False, 'packing_implementation_created':False})
print('D185 paired-action engine controls and raw reader passed.', flush=True)
