"""Record a pre-observation identity collision, then use a fresh unit label."""
from pathlib import Path
import ast
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
old.custody()
assert not(R/'gpu-run.lock').exists()
original=R/'runs/E084-freeze-primary.py'
failed_plan=R/'runs/E084-primary-plan'
assert failed_plan.exists() and not(failed_plan/'protocol.json').exists()
ids=['V084-unit','B278','E084R1','E084R2','B279','B280','E084R3']
assert all(not(R/'runs'/x).exists()for x in ids)
assert not(R/'runs/E084-native-execution').exists()
O=R/'runs/E084-primary-preparation-repair'
O.mkdir(exist_ok=False)
old.save(O/'report.json',{
    'at':old.now(),'original_preparer_sha256':old.sha(original),
    'original_error':'AssertionError at line23: planned ordinary unit label V082-unit already exists from E082. Primary protocol was not written and no unit/solve process started.',
    'cause':'Adaptation changed candidate E082 strings but left the separate V082 unit label unchanged.',
    'repair':'Fresh V084-unit identity; new primary-plan-r2 folder preserves all four original generated scripts. Candidate source, binaries, workload, order, quality, clocks and gates unchanged.',
    'new_native_unit_or_solve_processes':0,'new_samples':0,
    'source_and_timing_gates_changed':False,'original_plan_script_sha256':{str(p):old.sha(p)for p in failed_plan.iterdir()if p.is_file()}})
t=original.read_text()
assert t.count('V082-unit')==2
t=t.replace('V082-unit','V084-unit').replace('E084-primary-plan','E084-primary-plan-r2')
ast.parse(t)
target=R/'runs/E084-freeze-primary-r2.py'
assert not target.exists()
target.write_text(t,encoding='utf-8',newline='\n')
old.save(O/'new-preparer.json',{'path':str(target),'sha256':old.sha(target),'original':str(original),'source_activated':False,'new_samples':0})
print(target,flush=True)
