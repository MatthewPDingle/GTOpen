"""Root-only policy-pinned entry to the unchanged E037 measurement runner."""
import datetime,runpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import policy_guard as gate
assert len(sys.argv)==2,'Provide separate policy authorization SHA256'
expected=sys.argv[1];policy,auth=gate.verify(expected)
assert not (gate.ROOT/'gpu-run.lock').exists()
assert gate.read(gate.ROOT/'runs/E037-build/exit.json')['returncode']==0
for identity in policy['order']:assert not (gate.ROOT/'runs'/identity).exists(),identity
for name in ['runs/E037-primary-execution','runs/E037-assessment','comparisons/E037-three-pair-comparison','runs/E037R1.patch']:
    assert not (gate.ROOT/name).exists(),name
gate.EXECUTION.mkdir(exist_ok=False)
gate.create_json(gate.EXECUTION/'pre-primary.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policy_sha256':gate.sha(gate.HERE/'policy.json'),'policy_manifest_sha256':gate.sha(gate.HERE/'scripts-manifest.json'),'policy_authorization_sha256':expected,'original_authorization_sha256':gate.sha(gate.OLD/'authorization.json'),'all_seven_run_directories_absent':True,'order':policy['order'],'original_primary_sha256':gate.sha(gate.OLD/'primary.py'),'wrapper_sha256':gate.sha(__file__)})
error=None;returncode=1
try:
    sys.argv=[str(gate.OLD/'primary.py')]
    runpy.run_path(str(gate.OLD/'primary.py'),run_name='__main__')
    returncode=0
except BaseException as fault:
    error=repr(fault);raise
finally:
    gate.create_json(gate.EXECUTION/'exit.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':returncode,'error':error})
