"""Exactly one frozen compiler/native/complete-reader sequence, holding GPU lock."""
import json, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/D310-interleaved-copy-control'
P=h.read(H/'protocol-v2.json')
assert len(sys.argv)==2
def verify():
    h.pin(H/'protocol-v2.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def available():
    return int(subprocess.check_output(['powershell','-NoProfile','-Command','(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory'],text=True).strip())*1024
verify()
O=H/'execution-v2';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'] and available()>=P['minimum_available_RAM_bytes']
    gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'])
    ref=h.read(ROOT/'runs/D308-packed-arithmetic/execution/before.json')['gpu']
    assert gpu['stdout']==ref['stdout'] and 'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee' in gpu['stdout']
    h.save(O/'before.json',{'at':h.now(),'GPU':gpu,'X_free_bytes':shutil.disk_usage(ROOT).free,'available_RAM_bytes':available(),'solver_speed_samples':0})
    h.child(P['rustc_command'],O,'rustc',300)
    verify();h.ar.refuse_active(h.ar.live_status())
    h.child([str(H/'probe.exe'),str(O/'native-output')],O,'native',P['maximum_native_seconds'])
    verify()
    lines=(O/'native.stdout.log').read_text(encoding='utf-8').splitlines()
    markers={tag:[json.loads(line.split(' ',1)[1])for line in lines if line.startswith(tag+' ')]for tag in['D310_ABI','D310_COPY','D310_CASE_COMPLETE','D310_COMPLETE']}
    assert [len(markers[k])for k in markers]==[1,9,9,1]
    assert [x['fixture']for x in markers['D310_CASE_COMPLETE']]==[x['fixture']for x in P['cases']]
    assert markers['D310_COMPLETE'][0]['CUDA_application_kernels']==markers['D310_COMPLETE'][0]['NVRTC_compiles']==markers['D310_COMPLETE'][0]['CFR_iterations']==0
    assert markers['D310_COMPLETE'][0]['all_owned_ranges_and_context_dropped']
    h.save(H/'native-report.json',{'at':h.now(),'markers':markers,'stdout_sha256':h.sha(O/'native.stdout.log'),'scope':'Transportonly; no numerical/CFR/speed/capacityadoptionclaim.'})
    assert available()>=P['minimum_available_RAM_bytes']
    h.child([sys.executable,str(H/'reader-v2.py'),sys.argv[1]],O,'reader',P['maximum_reader_seconds'])
    verify()
print(json.dumps({'native_complete':True,'reader_report_sha256':h.sha(H/'reader-report.json'),'new_solver_candidate':False}),flush=True)
