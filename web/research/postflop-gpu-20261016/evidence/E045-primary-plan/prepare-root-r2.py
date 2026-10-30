"""Preserve accumulation-order observer failure; use accurate fsum, no native rerun."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
out=old.ROOT/'comparisons/E045-root-crosscheck'
old.save(out/'failure.json',{'at':old.now(),'returncode':1,'status':'failed_observer_float_accumulation_assumption','script_sha256':old.sha(HERE/'root-check.py'),'error':'AssertionError: aggregate arithmetic','cause':'Root used sequential bs+=median; the Python3.12 sum used by the registered assessment is compensated. Same exact three medians give9719.810300000001 versus9719.8103ms, changing gain by1.84e-14 percentage points. R2 independently uses math.fsum over the retained medians. No rounding of source samples, policy change or native rerun.','timing_decision_unchanged':'rejected: river strict fixture guard failed','new_native_runs':0})
s=(HERE/'root-check.py').read_text(encoding='utf-8')
s=s.replace('import datetime,json,statistics,sys','import datetime,json,math,statistics,sys')
s=s.replace("comparisons/E045-root-crosscheck'","comparisons/E045-root-crosscheck-r2'")
needle='gain=100*(bs-cs)/bs;passed='
assert s.count(needle)==1
s=s.replace(needle,"bs=math.fsum(f['baseline_median_ms'] for f in fixture);cs=math.fsum(f['candidate_median_ms'] for f in fixture)\ngain=100*(bs-cs)/bs;passed=")
s=s.replace("'id':'E045-root-crosscheck'","'id':'E045-root-crosscheck-r2'")
s=s.replace("'root_cross_check_only':True","'root_cross_check_only':True,'prior_observer_failure_sha256':old.sha(old.ROOT/'comparisons/E045-root-crosscheck/failure.json'),'new_native_runs':0,'aggregation_repair':'math.fsum of same three retained fixture medians'")
q=HERE/'root-check-r2.py';assert not q.exists();q.write_text(s,encoding='utf-8');print(old.sha(q))
