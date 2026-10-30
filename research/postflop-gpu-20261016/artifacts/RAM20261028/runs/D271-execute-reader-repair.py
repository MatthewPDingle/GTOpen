import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/D271-metadata-engine';h.pin(H/'reader-repair-protocol.json',sys.argv[1]);R=h.read(H/'reader-repair-protocol.json')
for p,d in R['input_sha256'].items():h.pin(p,d)
h.custody();h.ar.refuse_active(h.ar.live_status());O=H/'execution-reader-repair';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.child([sys.executable,str(H/'audit-r2.py'),sys.argv[1]],O,'audit-r2',1800)
    for p,d in R['input_sha256'].items():h.pin(p,d)
    h.custody();h.save(O/'complete.json',{'at':h.now(),'root_report_sha256':h.sha(ROOT/'comparisons/D271-metadata-engine/report.json'),'original_failed_reader_preserved':True,'all42_completed_GPU_cases_not_repeated':True,'all_owned_children_terminal':True,'new_compiler_GPU_CUDA_solver_or_speed_runs':0,'accepted_main_live_protected_PTX_unchanged':True})
print('D271 complete original plus extra GPU raw replay passed, no native repeat.',flush=True)
