import sys,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    h.child(P['rustc_command'],O,'rustc',600);verify()
    h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
    for ident in P['native_sequence']:
        h.child([str(H/'probe.exe'),str(O/(ident+'.ptx'))],O,ident,600);verify()
    h.child([sys.executable,str(H/'assess.py')],O,'assessment',600);verify()
    h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(ROOT/'comparisons/D158-cold-main-acquisition/report.json'),'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'solver_or_explicit_GPU_context_kernel_calls':0,'candidate_accepted':False})
print('D158 three fresh cold main PTX acquisitions and assessment complete.',flush=True)
