import sys,shutil,os
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
    for arm in P['sequence']:h.child(P['rustc_commands'][arm],O,'rustc-'+arm,1200);verify()
    previous=os.environ.get('D156_OUTPUT')
    try:
        for arm in P['sequence']:
            verify();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
            output=H/(arm+'-output');output.mkdir(exist_ok=False);os.environ['D156_OUTPUT']=str(output)
            h.child([str(H/(arm+'.exe')),'--exact','postflop_complete_cycle','--ignored','--nocapture','--test-threads=1'],O,arm,1800);verify()
    finally:
        if previous is None:os.environ.pop('D156_OUTPUT',None)
        else:os.environ['D156_OUTPUT']=previous
    h.child([sys.executable,str(H/'audit.py')],O,'audit',1800);verify()
    h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(ROOT/'comparisons/D156-primary-lifecycle-control/report.json'),'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'performance_qualification_samples':0,'candidate_accepted':False})
print('D156 complete primary raw state and lifecycle controls passed.',flush=True)
