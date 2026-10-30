import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/D270-actual-metadata-CPU';h.pin(H/'reader-repair-protocol.json',sys.argv[1]);R=h.read(H/'reader-repair-protocol.json')
for p,d in R['input_sha256'].items():h.pin(p,d)
h.custody();h.ar.refuse_active(h.ar.live_status());O=H/'execution-reader-repair';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.child([sys.executable,str(ROOT/'runs/D270-root-replay-r2.py'),R['original_protocol_sha256'],sys.argv[1]],O,'reader-r2',1800)
    for p,d in R['input_sha256'].items():h.pin(p,d)
    h.custody();h.save(O/'complete.json',{'at':h.now(),'root_report_sha256':h.sha(H/'root-report-r2.json'),'all_owned_children_terminal':True,'all18completed_native_cases_not_repeated':True,'original_failed_reader_preserved':True,'new_compiler_native_CUDA_GPU_solver_speed_runs':0,'accepted_main_live_protected_PTX_unchanged':True})
print('D270 read-only corrected complete replay finished; original forecast failure retained.',flush=True)
