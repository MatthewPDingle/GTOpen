import sys,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D174-budget-error-cost';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',1200);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe'),'source_and_inputs_sha256':P['input_sha256'],'native_runs':0})
 h.child([str(H/'probe.exe'),'zero_check_setup_preserves_caller_error_priority_and_joined_cleanup','--nocapture','--test-threads=1'],O,'coordinator-tests',600);verify();assert 'test result: ok. 2 passed; 0 failed;' in(O/'coordinator-tests.stdout.log').read_text(encoding='utf-8')
 h.child([str(H/'probe.exe'),'--exact','d174_budget_failure_costs','--nocapture','--test-threads=1'],O,'budget-cost',1200);verify();h.save(O/'native-complete.json',{'at':h.now(),'all_owned_children_terminal':True,'ordinary_coordinator_tests_passed':2,'actual_error_contract_processes':1,'application_kernel_launches':0})
 h.child([sys.executable,str(ROOT/'runs/D174-assess.py'),sys.argv[1]],O,'assessment',600);verify();h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(ROOT/'comparisons/D174-budget-error-cost/report.json'),'performance_qualification_samples':0,'candidate_accepted':False})
print('D174 all frozen contract/cost work terminal.',flush=True)
