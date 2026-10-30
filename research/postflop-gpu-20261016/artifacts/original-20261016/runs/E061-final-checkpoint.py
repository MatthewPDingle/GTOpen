"""Confirm final source custody and served dashboard result before next docket form."""
import json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
assert subprocess.check_output(['git','log','-1','--format=%s'],cwd=old.REPO,text=True).strip()=='research: reject first fresh async-staging qualification'
assert not subprocess.check_output(['git','diff','--name-only','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,text=True).strip()
H=ROOT/'runs/E061-closure';p=H/'commit.json';commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip()
old.save(p,{'at':old.now(),'commit':commit,'committed_paths':['research/postflop-gpu-20261016/experiments.md'],'original_source_form':'E050','new_qualification':'E061','all_owned_children_terminal':True,'source_restored_to_E051':True,'main_live_ptx_unchanged':True,'new_gain_accepted':False,'next_docket_form':'E057asE062','goal_active':True})
key='evidence/E061-closure/commit.json';dst=old.ar.DASHBOARD/key;assert not dst.exists();dst.write_bytes(p.read_bytes())
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='E061');assert e['status']=='rejected' and e['correctness']=='pass';e['evidence'].append({'label':'Local ledger commit','url':key});s['updated_at']=old.now();old.ar.atomic_json(old.ar.STATUS,s)
assert old.ar.STATUS.is_relative_to(old.ar.DASHBOARD)
rel=old.ar.STATUS.relative_to(old.ar.DASHBOARD).as_posix()
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+rel,timeout=15) as response:served=json.loads(response.read())
served_e=next(e for e in served['experiments'] if e['id']=='E061');assert served_e==e and served['accepted_complete_run']==s['accepted_complete_run']
old.pin(old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md','2b4f173b98863272279c39302017608aa8a0976074a709fe09e61af5a4b0735f')
old.custody();print(json.dumps({'status':'closed_source_form_and_live_dashboard_verified','commit':commit,'gain_pct':served_e['observed_gain_pct'],'accepted_source':s['accepted_complete_run']['candidate_id'],'next':'E062original prefix mapping','all_owned_children_terminal':True,'goal_active':True}),flush=True)
