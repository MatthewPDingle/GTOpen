import sys,json,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',1200);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe')],O,'layout',120);verify()
rows=[json.loads(x.split('D208_LAYOUT ',1)[1]) for x in (O/'layout.stdout.log').read_text().splitlines() if 'D208_LAYOUT ' in x];assert len(rows)==1;r=rows[0]
h.save(H/'report.json',{'id':'D208','at':h.now(),'status':'pass_complete_host_compile_role_bindings_and_prospective_layout','protocol_sha256':sys.argv[1],'layout':r,'role_review_sha256':h.sha(H/'role-review.json'),'baseline_host_source_sha256':h.sha(ROOT/'runs/E104-source/baseline-mod-r2.rs'),'candidate_host_source_sha256':h.sha(ROOT/'runs/E104-source/candidate-mod-r2.rs'),'all_owned_compiler_layout_children_terminal':True,'actual_constructor_CUDA_kernel_or_solver_calls':0,'performance_samples':0,'candidate_accepted':False,'scope':'FullcandidateRusthosttypechecked/codegeneratedofftreeandactualtypedhost/framecostlayout. Alloriginalkernel/playerargumentrolesandrootcopy staticallymatch. NoGPUconstructor/resource requery/rawCFR/dereference/numeric/lifecycle/fullsolver/speed/adoptionproof. Actualwrapperdelta wasprospectivelybounded<=32,alloriginalnumeric/device/state fieldsstillmustexact.'});h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(H/'report.json'),'application_kernel_or_solver_runs':0});verify();print(json.dumps({'status':'host_compile_layout_pass','layout':r,'new_CFR_GPU_calls':0}),flush=True)
