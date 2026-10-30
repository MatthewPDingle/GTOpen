"""Verify final process/source/dashboard custody for this research checkpoint."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
old.custody()
assert not(R/'gpu-run.lock').exists()
receipts={}
for folder in ['D134-manager-r2','E084-resource-manager','E084-direct-manager',
               'E084-build-manager','E084-primary-manager','E084-primary-wrapper']:
    for p in (R/'runs'/folder).glob('*.exit.json'):
        q=old.read(p)
        assert q['returncode']==0 and q['error']is q['cleanup']is None,str(p)
        receipts[str(p)]={'sha256':old.sha(p),'returncode':q['returncode']}
for folder in ['E084-resource/execution','E084-kernel-control/execution',
               'E084-native-execution','E084-final-build/feature','E084-final-build/primary']:
    for p in (R/'runs'/folder).glob('*.exit.json'):
        q=old.read(p)
        assert q['returncode']==0 and q['error']is q['cleanup']is None,str(p)
        receipts[str(p)]={'sha256':old.sha(p),'returncode':q['returncode']}
live=old.ar.live_status()
old.ar.refuse_active(live)
s=old.read(old.ar.STATUS)
assert s['goal_status']=='active'
assert s['accepted_complete_run']['candidate_id']=='E080'
assert s['accepted_complete_run']['observed_gain_pct']==14.741418835370924
assert s['deployment']['live_binary_sha256']=='c3c88449297574df6eeb9cb3badf4a99b0802dc740fea0f9d8fee401c1c22a62'
assert s['execution_permissions']['approval_policy']=='never' and s['execution_permissions']['full_access']
assert all(next(x for x in s['experiments']if x['id']==ident)['status']=='rejected'for ident in ['D134','E083','E084'])
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as response:
    assert json.load(response)==s
free={p:shutil.disk_usage(p).free for p in ['S:\\','T:\\']}
assert free['T:\\']>=53687091200
out=R/'runs/D134-E084-turn-closure'
out.mkdir(exist_ok=False)
report={'at':old.now(),'status':'pass_checkpoint','goal_status':'active',
    'full_access':True,'approval_policy':'never','approval_prompts_requested':0,
    'receipt_inventory':receipts,'all_owned_native_compiler_processes_terminal':True,
    'GPU_lock_absent':True,'accepted_source_main_live_protected_PTX_custody_pass':True,
    'accepted_live_candidate':'E080','accepted_cumulative_observed_gain_pct':14.741418835370924,
    'D134_E083_decision_sha256':old.sha(R/'comparisons/D134-component-closure/report.json'),
    'E084_decision_sha256':old.sha(R/'runs/E084-initial-closure/decision.json'),
    'E084_initial_gain_pct':-2.2031737913124756,
    'E084_full_results_exact':18,'E084_checkpoints_exact':138,
    'last_primary_baseline':'B280','status_HTTP_matches_file':True,
    'free_bytes':free,'local_ledger_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip(),
    'no_push':True,'live_status':live}
old.save(out/'report.json',report)
key=out.name+'/report.json'
dst=old.ar.DASHBOARD/'evidence'/key
dst.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(out/'report.json',dst)
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:
    assert response.read()==(out/'report.json').read_bytes()
print(json.dumps({k:report[k]for k in ['status','all_owned_native_compiler_processes_terminal',
    'accepted_live_candidate','accepted_cumulative_observed_gain_pct','last_primary_baseline']}),flush=True)
