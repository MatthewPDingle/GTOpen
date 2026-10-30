import importlib.util,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D280-pinned-registration-lifecycle';P=h.read(H/'protocol.json');O=H/'execution';assert len(sys.argv)==2
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O.mkdir(exist_ok=False)
for p in[H/'protocol.json',H/'fixtures.json',H/'probe.rs']:
    dest=h.ar.DASHBOARD/'evidence'/H.name/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='D280'for x in status['experiments']);status['experiments'].append({'id':'D280','title':'Pinned-staging registration allocation lifecycle','kind':'diagnostic','status':'running','accepted':False,'stage':'Fixed native DMA/lifecycle and process-cost component screen','reason':'OrdinaryWindowspages+CUDAregistrationonly>=64MiB,originaltinyfallback. Exactoriginal3staging sizes,2wholewordDMA/CPUcycles/fulloutputs/cleanup andmatchedCPU/memory/lifetimegates. Componenteffort>=100.521554msonly,nofullsolvegain/sourceadmission.','evidence':[{'label':'Frozen original sizes/protocol','url':'evidence/'+H.name+'/protocol.json'}]});status.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='D280',stage='Pinned-staging allocation lifecycle test',activity='Onefixedmodel,8freshnativeprocessesincluding2warmups;wholebitDMA+cleanupandmatchedcosts. No production source or shader change; E080 remainslive.');h.ar.atomic_json(h.ar.STATUS,status)
spec=importlib.util.spec_from_file_location('d280_sampler',H/'sampler.py');sampler=importlib.util.module_from_spec(spec);spec.loader.exec_module(sampler)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    verify();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',900);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
    nvml=sampler.Nvml()
    try:
        for row in P['sequence']:
            verify();h.ar.refuse_active(h.ar.live_status());assert sampler.system_memory()['available_physical_bytes']>=P['available_RAM_before_and_during_bytes']and shutil.disk_usage(ROOT).free>=64*1024**3
            out=H/row['id'];assert not out.exists();sampler.run([str(H/'probe.exe'),row['arm'],str(out),row['role']],O,row['id'],h,nvml,900);verify();assert sum(p.stat().st_size for s in P['sequence']for p in(H/s['id']).glob('*.bin'))<=P['raw_reservation_bytes']
    finally:nvml.close()
    h.child([sys.executable,str(ROOT/'runs/D280-read-pinned-lifecycle.py'),sys.argv[1]],O,'reader',900);verify();h.save(O/'complete.json',{'at':h.now(),'root_report_sha256':h.sha(H/'report.json'),'all_owned_compiler_native_sampler_reader_children_terminal':True,'new_CUDA_applicationkernels_NVRTC_CFR_solver_or_speed_samples':0,'accepted_main_live_protected_PTX_unchanged':True})
print('D280 fixed component cohort and full raw reader terminal.',flush=True)
