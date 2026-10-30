import shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D267b-node-order-model';P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child([sys.executable,str(ROOT/'runs/D267b-node-order-model.py'),sys.argv[1]],O,'model',1800);verify();assert sum(p.stat().st_size for p in(H/'output').iterdir())<=P['raw_output_reservation_bytes'];h.child([sys.executable,str(ROOT/'runs/D267b-node-order-audit.py'),sys.argv[1]],O,'audit',1800);verify();h.save(O/'complete.json',{'at':h.now(),'all_owned_readers_terminal':True,'model_sha256':h.sha(H/'model-report.json'),'root_sha256':h.sha(H/'root-report.json'),'compiler_CUDA_kernel_solver_speed_runs':0,'accepted_main_live_protected_PTX_unchanged':True})
print('D267 reversible CPU metadata model and full inverse replay passed.',flush=True)
