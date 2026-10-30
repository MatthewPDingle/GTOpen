import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
receipts={}
folders=[R/'runs/E089-resource/execution',R/'runs/E089-kernel-control/execution',R/'runs/E089-direct-audit',R/'runs/E089-final-build',R/'runs/E089-primary-wrapper',R/'runs/E089-native-execution']
for folder in folders:
 for p in folder.rglob('*.exit.json'):
  x=old.read(p);assert x['returncode']==0 and x['error']is x['cleanup']is None
  receipts[str(p)]={'sha256':old.sha(p),'returncode':0}
assert len(receipts)==17
for p in [R/'runs/E089-resource/execution/complete.json',R/'runs/E089-kernel-control/execution/complete.json',R/'runs/E089-final-build/complete.json',R/'runs/E089-primary-wrapper/complete.json',R/'runs/E089-native-execution/complete.json']:assert p.is_file()
snap=old.ar.live_status();old.ar.refuse_active(snap);state=old.read(old.ar.STATUS)
q=old.read(R/'runs/E089-initial-closure/decision.json')
assert q['decision']=='rejected'and state['accepted_complete_run']['candidate_id']=='E080'
assert state['accepted_complete_run']['observed_gain_pct']==14.741418835370924
assert old.read(R/'runs/E088-duplicate-closure/report.json')['compiler_invocations']==0
free={n:shutil.disk_usage(n+':\\').free for n in ['S','T']}
assert free['S']>=66*1024**3 and free['T']>=50*1024**3
O=R/'runs/E089-turn-checkpoint';O.mkdir(exist_ok=False)
old.save(O/'report.json',{'at':old.now(),'status':'pass_checkpoint','goal_status':'active','previous_goal_turn':'progress: completed E087 correctness/build/primary and rejected fixture tradeoffs','this_turn':'progress: declined duplicate E088 before execution, then compiled and numerically tested new E089, completed fresh full builds and fixed whole-solve comparison, rejected below 1%','all_owned_native_compiler_processes_terminal':True,'tool_sessions_completed':[9669,74978,55803],'terminal_receipts':receipts,'GPU_lock_absent':True,'source_main_live_protected_PTX_custody_pass':True,'accepted_live_candidate':'E080','accepted_cumulative_gain_pct':14.741418835370924,'E088_decision':'duplicate; no compiler or GPU execution','E089_decision':'rejected','E089_gain_pct':q['performance']['observed_gain_pct'],'E089_guard_failures':[],'decision_sha256':old.sha(R/'runs/E089-initial-closure/decision.json'),'live_status':snap,'free_bytes':free,'last_primary_baseline':'B292','source_adopted':False,'pushes':0,'live_restarts':0,'next':'Scout an independent bottleneck from accepted E080. E089 exact form and variants remain closed.'})
pub=[]
for p in [O/'report.json',R/'runs/E089-primary-freezer-review.json',R/'runs/E089-primary-freezer-before-review.py',R/'runs/E089-prepare-primary-freezer.py']:
 key=('E089-turn-checkpoint/'if p.parent==O else'E089-primary-preparation/')+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E089')
 x['evidence'].append({'label':'Terminal process and custody checkpoint','url':'evidence/E089-turn-checkpoint/report.json'})
 s['updated_at']=old.now();old.ar.atomic_json(old.ar.STATUS,s)
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as z:assert z.read()==old.ar.STATUS.read_bytes()
old.save(O/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'tracker_current_bytes_exact':True})
print(json.dumps({'status':'pass_checkpoint','terminal_receipts':len(receipts),'accepted':'E080','goal':'active','free_bytes':free}),flush=True)
