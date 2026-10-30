"""Preserve the failed observer, correct its epoch, never rerun native controls."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
p=HERE/'audit.py'
old.save(old.ROOT/'comparisons/E044-discount-control/failure.json',{
 'at':old.now(),'status':'failed_observer_epoch_assumption',
 'script_sha256':old.sha(p),'returncode':1,
 'error':'AssertionError: strategy-only preserves complete previous raw regrets',
 'cause':'The observer compared strategy-only readback with pre-materialization CPU arenas. The native sequence calls ensure_symmetric before that readback; it can fill sibling regrets. lock_node changes separate lock tables only. The retained materialized snapshot is the correct preceding regret state.',
 'source_evidence':['crates/solver/src/cfr.rs:780','crates/solver/src/query.rs:837','E044-design/control-body.rs'],
 'native_reexecuted':False,'performance_measured':False})
s=p.read_text(encoding='utf-8')
assert s.count("comparisons/E044-discount-control'")==1
s=s.replace("comparisons/E044-discount-control'","comparisons/E044-discount-control-r2'")
s=s.replace("first=host((d/'first.host.candidate.bin').read_bytes())","first=host((d/'materialized.host.candidate.bin').read_bytes())")
s=s.replace('previous raw regrets','previous materialized raw regrets')
s=s.replace("'id':'E044-discount-control'","'id':'E044-discount-control-r2'")
s=s.replace("'root_cross_check_only':True", "'root_cross_check_only':True,'prior_observer_failure_sha256':old.sha(old.ROOT/'comparisons/E044-discount-control/failure.json'),'native_reexecuted':False")
q=HERE/'audit-r2.py';assert not q.exists();q.write_text(s,encoding='utf-8')
print(old.sha(q))
