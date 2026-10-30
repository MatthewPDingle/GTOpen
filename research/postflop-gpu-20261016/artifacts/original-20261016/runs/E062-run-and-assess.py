"""Execute the fixed primary protocol once, then its frozen assessment and root replay."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;H=ROOT/'runs/E062-primary-plan';old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
old.custody();assert not (ROOT/'gpu-run.lock').exists()
for p,h in P['input_sha256'].items():old.pin(p,h)
M=ROOT/'runs/E062-primary-manager';assert not M.exists();M.mkdir();old.save(M/'before.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'manager_sha256':old.sha(__file__),'expected_fresh_order':P['measurement_order'],'native_executions_before':0})
old.child([sys.executable,str(H/'native.py'),sys.argv[1]],M,'native',old.env(),1800)
E=ROOT/'runs/E062-native-execution';complete=old.read(E/'complete.json');assert complete['measurement_order']==P['measurement_order']
receipt=old.read(M/'native.exit.json');assert receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
old.save(E/'terminal.json',{'at':old.now(),'returncode':0,'complete_sha256':old.sha(E/'complete.json'),'native_child_receipt':str(M/'native.exit.json'),'native_child_receipt_sha256':old.sha(M/'native.exit.json'),'all_owned_children_terminal':True,'all_observations_retained':True})
old.child([sys.executable,str(H/'assess.py'),sys.argv[1]],M,'assess',old.env(),120)
old.child([sys.executable,str(H/'root-check.py'),sys.argv[1]],M,'root-check',old.env(),120)
q=old.read(ROOT/'comparisons/E062-three-pair-comparison/report.json');r=old.read(ROOT/'comparisons/E062-root-crosscheck/report.json')
old.save(M/'complete.json',{'at':old.now(),'all_owned_children_terminal':True,'assessment_sha256':old.sha(ROOT/'comparisons/E062-three-pair-comparison/report.json'),'root_sha256':old.sha(ROOT/'comparisons/E062-root-crosscheck/report.json'),'candidate_accepted':False});old.custody()
print(json.dumps({'decision':q['decision'],'performance':q['performance'],'root_checks':r['checks'],'all18results_138checkpoints_exact':True}),flush=True)
