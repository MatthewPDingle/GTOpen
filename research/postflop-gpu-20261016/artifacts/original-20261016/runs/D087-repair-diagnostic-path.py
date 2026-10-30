"""Preserve a precompile stale-path failure; no native rerun or source change."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();H=ROOT/'runs/D087-cupti-driver-profile'
assert not (ROOT/'gpu-run.lock').exists() and not (H/'diagnostic-build-plan.json').exists() and not (H/'diagnostic-build').exists()
D=H/'diagnostic-draft-r1';D.mkdir()
for name in ['prepare-diagnostic-build.py','evaluator.rs','evaluator.patch']:
 p=H/name;target=D/name;assert p.resolve().is_relative_to(H.resolve()) and target.resolve().is_relative_to(H.resolve());p.rename(target)
old.save(D/'failure.json',{'at':old.now(),'outer_exec_chunk_id':'01b05b','returncode':1,'failure':'FileNotFoundError at protocol hashing: stale build-r3/D087Collector.dll string. Collector built in build/.','all_compiler_and_native_work_prevented':True,'evaluator_or_solver_behavior_change':False,'old_script_sha256':old.sha(D/'prepare-diagnostic-build.py'),'evaluator_sha256':old.sha(D/'evaluator.rs')})
s=(D/'prepare-diagnostic-build.py').read_text(encoding='utf-8').replace("H/'build-r3/","H/'build/")
needle="},'candidate_accepted':False,'performance_qualification':False};old.save(H/'diagnostic-build-plan.json',P)"
assert s.count(needle)==1
s=s.replace(needle,"},'candidate_accepted':False,'performance_qualification':False};P['input_sha256'].update({str(x):old.sha(x) for x in [H/'prepare-diagnostic-build-r2.py',H/'diagnostic-draft-r1/failure.json',H/'diagnostic-draft-r1/prepare-diagnostic-build.py',H/'build-diagnostic.py']});old.save(H/'diagnostic-build-plan.json',P)")
assert 'build-r3' not in s
(H/'prepare-diagnostic-build-r2.py').write_text(s,encoding='utf-8',newline='\n')
print('Stale path failure preserved; corrected preparation script ready.',flush=True)
