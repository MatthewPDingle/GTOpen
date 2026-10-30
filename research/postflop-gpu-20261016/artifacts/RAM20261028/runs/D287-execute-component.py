import importlib.util,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D287-terminal-component';P=h.read(H/'protocol.json');O=H/'execution';assert len(sys.argv)==2
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();assert not O.exists();O.mkdir()
spec=importlib.util.spec_from_file_location('bounded',H/'bounded_child.py');bounded=importlib.util.module_from_spec(spec);spec.loader.exec_module(bounded)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());initial=bounded.memory();assert initial['available_physical']>=P['limits']['available_RAM_before_bytes']and shutil.disk_usage(ROOT).free>=P['limits']['required_free_bytes'];h.save(O/'admission.json',{'at':h.now(),'memory':initial,'free_X_bytes':shutil.disk_usage(ROOT).free});h.child(P['rustc_command'],O,'rustc',1200);verify();binary=H/'probe.exe';assert(H/'baseline.ptx').read_bytes()in binary.read_bytes();h.save(O/'binary.json',{'sha256':h.sha(binary),'accepted_exact_PTX_embedded':True});out=H/'component-output';out.mkdir()
 bounded.run([str(binary),'--exact','postflop_complete_cycle','--ignored','--nocapture','--test-threads=1'],O,'probe',h,P['limits'],H,out);verify();h.child([sys.executable,str(H/'audit.py')],O,'reader',1800);verify();q=h.read(H/'report.json');h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(H/'report.json'),'component_pass':q['status']=='pass_component_effort_cost_and_bits_only','no_extra_samples':True,'optimizer_source_created_or_adopted':False})
print(q['status'],q['component_saving_ms'],q['failed_gates'],flush=True)
