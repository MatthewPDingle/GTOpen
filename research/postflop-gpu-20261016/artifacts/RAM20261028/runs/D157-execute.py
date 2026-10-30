import sys,shutil,importlib.util
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('d157_sampler',H/'sampler.py');sampler=importlib.util.module_from_spec(spec);spec.loader.exec_module(sampler)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    for arm,cmd in P['rustc_commands'].items():h.child(cmd,O,'rustc-'+arm,1200);verify()
    h.save(O/'binaries.json',{'at':h.now(),'binary_sha256':{a:h.sha(H/(a+'.exe')) for a in P['rustc_commands']}})
    nvml=sampler.Nvml()
    try:
        assert nvml.versions()==P['NVML_versions']
        for row in P['sequence']:
            verify();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
            sampler.run([str(H/(row['arm']+'.exe')),'--exact','postflop_complete_cycle','--ignored','--nocapture','--test-threads=1'],O,row['id'],h,nvml,1200)
            verify()
    finally:nvml.close()
    h.child([sys.executable,str(H/'assess.py')],O,'assessment',1200);verify()
    h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(ROOT/'comparisons/D157-actual-resources/report.json'),'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'performance_qualification_samples':0,'candidate_accepted':False})
print('D157 fixed actual resource cohort and assessment complete.',flush=True)
