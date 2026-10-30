"""Launch the already-built v2 artifact once; keep failed launch and compiler receipts."""
import json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/D310-interleaved-copy-control'
O=H/'execution-v2'
P=h.read(H/'protocol-v2.json')
C=h.read(H/'launch-continuation.json')
assert len(sys.argv)==2
def verify():
    h.pin(H/'launch-continuation.json',sys.argv[1]);h.custody()
    for table in [P['input_sha256'],C['input_sha256']]:
        for path,digest in table.items():h.pin(path,digest)
verify()
assert h.read(O/'rustc.exit.json')['returncode']==0
assert h.read(O/'native.exit.json')['returncode'] is None
assert not (O/'native-output').exists()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    available=int(subprocess.check_output(['powershell','-NoProfile','-Command','(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory'],text=True).strip())*1024
    assert available>=P['minimum_available_RAM_bytes']
    gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'])
    assert gpu['stdout']==h.read(O/'before.json')['GPU']['stdout']
    h.save(O/'before-launch-continuation.json',{'at':h.now(),'GPU':gpu,'available_RAM_bytes':available,'X_free_bytes':shutil.disk_usage(ROOT).free,'existing_v2_compiler_not_repeated':True})
    h.child([str(H/'probe-v2.exe'),str(O/'native-output')],O,'native-v3',P['maximum_native_seconds'])
    verify()
    lines=(O/'native-v3.stdout.log').read_text(encoding='utf-8').splitlines()
    markers={tag:[json.loads(line.split(' ',1)[1])for line in lines if line.startswith(tag+' ')]for tag in['D310_ABI','D310_COPY','D310_CASE_COMPLETE','D310_COMPLETE']}
    assert [len(markers[k])for k in markers]==[1,9,9,1]
    assert [x['fixture']for x in markers['D310_CASE_COMPLETE']]==[x['fixture']for x in P['cases']]
    end=markers['D310_COMPLETE'][0]
    assert end['CUDA_application_kernels']==end['NVRTC_compiles']==end['CFR_iterations']==0 and end['all_owned_ranges_and_context_dropped']
    h.save(H/'native-report.json',{'at':h.now(),'markers':markers,'stdout_sha256':h.sha(O/'native-v3.stdout.log'),'scope':'Transportonly; noCFRnumerical/solver-speed/capacityadoptionclaim.'})
    h.child([sys.executable,str(H/'reader-v2.py'),C['source_protocol_sha256']],O,'reader',P['maximum_reader_seconds'])
    verify()
print(json.dumps({'native_complete':True,'reader_report_sha256':h.sha(H/'reader-report.json'),'new_solver_candidate':False}),flush=True)
