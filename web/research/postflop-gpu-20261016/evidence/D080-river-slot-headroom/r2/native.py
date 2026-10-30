import json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2;old.pin(HERE/'execution-seal.json',sys.argv[1]);S=old.read(HERE/'execution-seal.json')
for p,h in S['input_sha256'].items():old.pin(p,h)
P=old.read(HERE/'protocol.json')
for k in ['cpu_input_sha256','dependency_artifact_sha256']:
 for p,h in P[k].items():old.pin(p,h)
old.custody();old.ar.refuse_active(old.ar.live_status())
OUT=HERE/'execution';assert not OUT.exists();assert not (HERE/'probe.exe').exists()
with old.ar.exclusive_lock(old.ROOT/'gpu-run.lock'):
 assert shutil.disk_usage(old.ROOT).free>=54*1024**3
 OUT.mkdir();old.child(P['command'],OUT,'rustc',old.env(),600)
 old.custody();old.ar.refuse_active(old.ar.live_status())
 old.save(OUT/'compiled.json',{'at':old.now(),'binary_sha256':old.sha(HERE/'probe.exe'),'protocol_sha256':old.sha(HERE/'protocol.json'),'all_compilers_terminal':True,'solver_executions':0,'production_source_unchanged':True})
 old.child([str(HERE/'probe.exe'),str(HERE.parent/'fixtures.json'),str(OUT/'raw')],OUT,'native',old.env(),240)
 old.custody()
 old.save(OUT/'complete.json',{'at':old.now(),'execution_seal_sha256':sys.argv[1],'binary_sha256':old.sha(HERE/'probe.exe'),'compiler_and_native_returncode':0,'accepted162_main_live_ptx_unchanged':True,'artifact_sha256':{str(x):old.sha(x) for x in OUT.rglob('*') if x.is_file()},'candidate_accepted':False})
print(json.dumps({'status':'D080_terminal_pending_assessment','complete_sha256':old.sha(OUT/'complete.json')}),flush=True)
