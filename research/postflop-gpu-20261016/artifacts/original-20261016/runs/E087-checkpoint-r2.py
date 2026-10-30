import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
receipts={}
for folder in [R/'runs/E087-host-type-check/execution',R/'runs/E087-transfer-control/execution',R/'runs/E087-final-build',R/'runs/E087-primary-wrapper',R/'runs/E087-native-execution']:
 for p in folder.rglob('*.exit.json'):
  x=old.read(p);assert x['returncode']==0 and x['error']is x['cleanup']is None
  receipts[str(p)]={'sha256':old.sha(p),'returncode':0}
assert len(receipts)==17
for p in [R/'runs/E087-host-type-check/execution/complete.json',R/'runs/E087-transfer-control/execution/complete.json',R/'runs/E087-final-build/complete.json',R/'runs/E087-primary-wrapper/complete.json',R/'runs/E087-native-execution/complete.json']:assert p.is_file()
snap=old.ar.live_status();old.ar.refuse_active(snap)
state=old.read(old.ar.STATUS);q=old.read(R/'runs/E087-initial-closure/decision.json')
assert q['decision']=='rejected'and state['accepted_complete_run']['candidate_id']=='E080'
assert state['accepted_complete_run']['observed_gain_pct']==14.741418835370924
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as z:assert z.read()==old.ar.STATUS.read_bytes()
free={n:shutil.disk_usage(n+':\\').free for n in ['S','T']}
assert free['T']>=50*1024**3 and free['S']>=66*1024**3
O=R/'runs/E087-turn-checkpoint';O.mkdir(exist_ok=False)
old.save(O/'report.json',{'at':old.now(),'status':'pass_checkpoint','goal_status':'active','previous_goal_turn':'progress:D138CPUmodel','this_turn':'progress:preparedandtypechecked3hostfiles;realGPUrawtransfersandcompatibilitypassed;twofreshbuildsandfixedcomplete-solvecomparison;rejectedrepeatablefixturetradeoffs','approval_policy':'never','full_access_operational':True,'all_owned_native_compiler_processes_terminal':True,'tool_sessions_completed':[29120,85985,91839],'terminal_receipts':receipts,'GPU_lock_absent':True,'source_main_live_protected_PTX_custody_pass':True,'accepted_live_candidate':'E080','accepted_cumulative_gain_pct':14.741418835370924,'E087_decision':'rejected','E087_gain_pct':q['performance']['observed_gain_pct'],'E087_guard_failures':[x['fixture_id']for x in q['performance']['fixture_regression_guard']if x['failed']],'decision_sha256':old.sha(R/'runs/E087-initial-closure/decision.json'),'tracker_HTTP_current_bytes_exact':True,'live_status':snap,'free_bytes':free,'last_primary_baseline':'B289','source_adopted':False,'pushes':0,'live_restarts':0,'next':'Scout an independent mechanism from accepted E080; exact E087 form and variants remain closed.'})
print(json.dumps({'status':'pass_checkpoint','terminal_receipts':len(receipts),'goal':'active','accepted':'E080','free_bytes':free}),flush=True)
