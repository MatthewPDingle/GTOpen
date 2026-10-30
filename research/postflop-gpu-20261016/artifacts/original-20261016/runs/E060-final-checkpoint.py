"""Publish local ledger commit and confirm the live dashboard/current policy."""
import json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
assert not subprocess.check_output(['git','diff','--name-only','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,text=True).strip()
assert subprocess.check_output(['git','log','-1','--format=%s'],cwd=old.REPO,text=True).strip()=='research: reject above-cutoff E060 on river regression'
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip()
H=ROOT/'runs/E060-closure';p=H/'commit.json'
old.save(p,{'at':old.now(),'commit':commit,'committed_paths':['research/postflop-gpu-20261016/experiments.md'],'accepted_source':'E051','all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'no_new_optimization_accepted':True,'goal_active':True})
key='evidence/E060-closure/commit.json';dst=old.ar.DASHBOARD/key;assert not dst.exists();dst.write_bytes(p.read_bytes())
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='E060');assert e['status']=='rejected' and e['correctness']=='pass' and e['observed_gain_pct']==1.2170441078096297
 assert s['state']=='running' and s['active_experiment'] is None and s['accepted_complete_run']['candidate_id']=='E051'
 e['evidence'].append({'label':'Local ledger commit','url':key});s['updated_at']=old.now();old.ar.atomic_json(old.ar.STATUS,s)
policy=old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md';old.pin(policy,'2b4f173b98863272279c39302017608aa8a0976074a709fe09e61af5a4b0735f')
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/',timeout=15) as response:assert response.status==200
old.custody();print(json.dumps({'status':'published_and_source_verified','commit':commit,'effective_cutoff_pct':1,'E060_rejected_on_tradeoff':True,'goal_active':True,'all_owned_children_terminal':True}),flush=True)
