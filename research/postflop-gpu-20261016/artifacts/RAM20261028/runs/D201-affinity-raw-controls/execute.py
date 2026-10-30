import sys,shutil,importlib.util,urllib.request,json
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('bounded',H/'bounded_child.py');bounded=importlib.util.module_from_spec(spec);spec.loader.exec_module(bounded)
assert bounded.affinity.query()=={'process_mask':P['masks']['baseline'],'system_mask':P['masks']['baseline']}
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['limits']['required_free_bytes']
 for arm in P['sequence']:
  verify();h.ar.refuse_active(h.ar.live_status());out=H/(arm+'-output');out.mkdir(exist_ok=False)
  bounded.run([P['binary'],'--exact','d168_worker_controls','--ignored','--nocapture','--test-threads=1'],O,arm,h,P['limits'],H,out,16,P['masks'][arm]);verify()
 h.child([sys.executable,str(H/'audit.py')],O,'audit',1800);verify()
 D=ROOT/'comparisons/D201-affinity-raw-controls';h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(D/'report.json'),'source_main_live_PTX_unchanged':True,'performance_samples':0,'new_gain_accepted':False})
print('D201 raw affinity controls complete; all children terminal, no speed score.',flush=True)
