import json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'cohort-plan.json',sys.argv[1]);P=old.read(H/'cohort-plan.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();M=ROOT/'runs/D096-manager';assert not M.exists();M.mkdir()
old.child([sys.executable,str(H/'run-cohort.py'),sys.argv[1]],M,'cohort',old.env(),1200)
old.custody();old.child([sys.executable,str(H/'root-and-publish-r2.py')],M,'root',old.env(),300)
q=old.read(H/'cohort-report.json');r=old.read(ROOT/'comparisons/D096-two-tone-root-check/report.json')
old.save(M/'complete.json',{'at':old.now(),'all_owned_children_terminal':True,'cohort_report_sha256':old.sha(H/'cohort-report.json'),'root_report_sha256':old.sha(ROOT/'comparisons/D096-two-tone-root-check/report.json'),'observer_usefulness_pass':q['observer_usefulness_pass'],'source_main_live_ptx_unchanged':True})
old.custody();print(json.dumps({'status':q['status'],'root_checks':r['checks_passed'],'observer_cycle_changes_pct':r['observer_cycle_changes_pct'],'median_phase_intervals':r['median_phase_intervals']}),flush=True)
