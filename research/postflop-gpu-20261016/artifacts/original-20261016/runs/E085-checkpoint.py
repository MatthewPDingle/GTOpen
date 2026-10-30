"""Verify terminal handles and preserve the accepted/live research checkpoint."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
folders=['E085-resource-manager','E085-resource-r2/execution','E085-direct-manager',
    'E085-kernel-control/execution','E085-build-manager','E085-final-build/feature',
    'E085-final-build/primary','E085-primary-manager','E085-primary-wrapper','E085-native-execution']
receipts={}
for folder in folders:
    files=list((R/'runs'/folder).glob('*.exit.json'))
    assert files,folder
    for p in files:
        q=old.read(p)
        assert q['returncode']==0 and q['error'] is q['cleanup'] is None,str(p)
        receipts[str(p)]={'sha256':old.sha(p),'returncode':0}
q=old.read(R/'runs/E085-initial-closure/decision.json')
s=old.read(old.ar.STATUS);live=old.ar.live_status();old.ar.refuse_active(live)
assert s['goal_status']=='active' and s['accepted_complete_run']['candidate_id']=='E080'
assert s['accepted_complete_run']['observed_gain_pct']==14.741418835370924
e=next(x for x in s['experiments']if x['id']=='E085')
assert e['status']==('measured' if q['performance']['primary_timing_pass'] else 'rejected')
assert not e['accepted'] and not q['source_adopted']
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as response:
    assert json.load(response)==s
free={p:shutil.disk_usage(p).free for p in ['S:\\','T:\\']}
assert free['T:\\']>=53687091200
O=R/'runs/E085-turn-checkpoint';O.mkdir(exist_ok=False)
report={'at':old.now(),'status':'pass_checkpoint','goal_status':'active',
    'previous_goal_turn':'progress:closedD134/E083andE084withactualcomponent/fullsolveevidence',
    'this_turn':'progress:compiledandnumericallytestednewE085thencompletedfixedprimary',
    'all_owned_native_compiler_processes_terminal':True,'terminal_receipts':receipts,
    'GPU_lock_absent':True,'source_main_live_protected_PTX_custody_pass':True,
    'accepted_live_candidate':'E080','accepted_cumulative_gain_pct':14.741418835370924,
    'E085_decision':q['decision'],'E085_gain_pct':q['performance']['observed_gain_pct'],
    'E085_decision_sha256':old.sha(R/'runs/E085-initial-closure/decision.json'),
    'candidate_adopted':False,'last_primary_baseline':'B283','HTTP_status_matches':True,
    'free_bytes':free,'local_ledger_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip(),
    'no_push':True,'live_status':live}
old.save(O/'report.json',report)
key=O.name+'/report.json';dst=old.ar.DASHBOARD/'evidence'/key
dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(O/'report.json',dst)
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:
    assert response.read()==(O/'report.json').read_bytes()
print(json.dumps({k:report[k]for k in ['status','E085_decision','E085_gain_pct',
    'all_owned_native_compiler_processes_terminal','accepted_live_candidate']}),flush=True)
