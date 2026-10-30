"""Publish local commits and verify live dashboard/source state after both diagnostics."""
import json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
assert not subprocess.check_output(['git','diff','--name-only','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,text=True).strip()
items=[('D099','D099-plan-posting-scratch','research: close exact river-posting allocation headroom screen'),('D100','D100-show-cache-configuration','research: reject showdown L1 preference on occupancy costs')]
links={}
for identity,folder,subject in items:
 commits=subprocess.check_output(['git','log','-1','--format=%H','--fixed-strings','--grep='+subject],cwd=old.REPO,text=True).splitlines();assert len(commits)==1
 p=ROOT/'runs'/folder/'commit.json';old.save(p,{'at':old.now(),'commit':commits[0],'committed_paths':['research/postflop-gpu-20261016/experiments.md'],'accepted_source':'E051','all_owned_children_terminal':True,'no_new_optimization_accepted':True,'source_main_live_ptx_unchanged':True,'goal_active':True})
 key='evidence/'+folder+'/commit.json';dst=old.ar.DASHBOARD/key;assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
 links[identity]=key
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert s['state']=='running' and s['active_experiment'] is None and s['accepted_complete_run']['candidate_id']=='E051'
 for identity,key in links.items():
  e=next(e for e in s['experiments'] if e['id']==identity);assert e['accepted'] is False;e['evidence'].append({'label':'Local ledger commit','url':key})
 s['updated_at']=old.now();old.ar.atomic_json(old.ar.STATUS,s)
old.pin(old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md','2b4f173b98863272279c39302017608aa8a0976074a709fe09e61af5a4b0735f')
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/',timeout=15) as response:assert response.status==200
old.custody();print(json.dumps({'status':'both_diagnostics_published','effective_cutoff_pct':1,'all_owned_children_terminal':True,'goal_active':True,'source_main_live_ptx_unchanged':True,'new_performance_gain_adopted':False,'previous_goal_turn':'progress','current_goal_turn':'progress'}),flush=True)
