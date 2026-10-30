import json, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/D195-parent-chance-controls';h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json');O=H/'execution'
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    for category in ['original','fanout']:
        folder=Path(P['folders'][category]);out=folder/'execution';out.mkdir(exist_ok=False)
        h.child(P['rustc_commands'][category],out,'rustc',600);verify()
        binary=folder/'probe.exe';data=binary.read_bytes()
        for arm in ['baseline','candidate']:assert (folder/(arm+'.ptx')).read_bytes() in data
        h.save(out/'build-complete.json',{'at':h.now(),'binary_sha256':h.sha(binary),'source_and_embedded_PTX_verified':True,'native_executions':0})
        h.ar.refuse_active(h.ar.live_status());h.child([str(binary),str(folder/'output')],out,'probe',1800);verify()
        lines=(out/'probe.stdout.log').read_text(encoding='utf-8').splitlines();rows=[json.loads(s.split(P['markers'][category],1)[1]) for s in lines if P['markers'][category] in s]
        assert rows[0]['stage']=='binding' and rows[-1]['stage']=='complete'
        assert len([x for x in rows if x['stage']=='case'])==P['expected_cases'][category]
        end=rows[-1];assert end['cases']==P['expected_cases'][category] and end['kernel_launches']==2*end['cases']
        assert end['full_outputs_exact'] and end['actual_immutable_inputs_exact'] and not end['performance_measured']
        raw={str(p):h.sha(p) for p in (folder/'output').iterdir() if p.is_file()};assert len(raw)==3
        h.save(out/'complete.json',{'at':h.now(),'raw_marker_summary':end,'raw_file_sha256':raw,'stdout_sha256':h.sha(out/'probe.stdout.log'),'all_children_terminal':True,'candidate_accepted':False})
h.child([sys.executable,str(ROOT/'runs/D195-audit.py')],O,'audit',1800);verify()
report=ROOT/'comparisons/D195-parent-chance-controls/report.json';q=h.read(report);assert q['status']=='pass_scoped_full_raw_parent_fanout_equivalence' and q['cases']==8345 and q['kernel_launches']==16690
h.save(O/'complete.json',{'at':h.now(),'all_owned_compilers_native_readers_terminal':True,'report_sha256':h.sha(report),'application_kernel_launches':16690,'GPU_solver_or_speed_samples':0,'accepted_source_main_live_protected_PTX_unchanged':True})
print(json.dumps({'status':q['status'],'cases':q['cases'],'kernel_launches':q['kernel_launches'],'checks':q['checks'],'all_owned_children':'terminal','solver_speed_samples':0}),flush=True)
