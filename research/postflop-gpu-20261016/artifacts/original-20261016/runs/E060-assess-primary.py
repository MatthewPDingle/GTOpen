"""Close terminal native receipt and execute the frozen primary assessments."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E060-primary-plan';E=ROOT/'runs/E060-native-execution';P=old.read(H/'protocol.json')
for n,h in P['input_sha256'].items():old.pin(n,h)
q=old.read(E/'complete.json');assert q['measurement_order']==P['measurement_order'] and q['fixture_results']==18 and q['convergence_records']==138
old.save(E/'terminal.json',{'at':old.now(),'session_id':64346,'returncode':0,'complete_sha256':old.sha(E/'complete.json'),'all_owned_children_terminal':True,'all_fixed_samples_retained':True,'accepted162_restored':True})
M=ROOT/'runs/E060-primary-assessment';M.mkdir()
old.child([sys.executable,str(H/'assess.py'),old.sha(H/'protocol.json')],M,'assess',old.env(),120)
old.child([sys.executable,str(H/'root-check.py'),old.sha(H/'protocol.json')],M,'root-check',old.env(),120)
q=old.read(ROOT/'comparisons/E060-three-pair-comparison/report.json');r=old.read(ROOT/'comparisons/E060-root-crosscheck/report.json')
old.save(M/'complete.json',{'at':old.now(),'assessment_sha256':old.sha(ROOT/'comparisons/E060-three-pair-comparison/report.json'),'root_sha256':old.sha(ROOT/'comparisons/E060-root-crosscheck/report.json'),'all_children_terminal':True,'candidate_accepted':False});old.custody()
print(json.dumps({'decision':q['decision'],'performance':q['performance'],'root_checks':r['checks'],'exact_results':r['exact_fixture_results'],'exact_checkpoints':r['exact_checkpoints']}),flush=True)
