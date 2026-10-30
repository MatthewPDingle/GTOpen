"""Confirm source custody, terminal receipts, ledger commit and actual served status."""
import json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip()
assert subprocess.check_output(['git','log','-1','--format=%s'],cwd=old.REPO,text=True).strip()=='research: verify profiler configuration compatibility without collection'
assert not subprocess.check_output(['git','diff','--name-only','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,text=True).strip()
old.pin(old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md','2b4f173b98863272279c39302017608aa8a0976074a709fe09e61af5a4b0735f')
for ident in ['E062','E063']:
 assert old.read(ROOT/f'runs/{ident}-primary-manager/complete.json')['all_owned_children_terminal']
 assert old.read(ROOT/f'runs/{ident}-closure/decision.json')['candidate_accepted'] is False
for label in ['cl','probe']:assert old.read(ROOT/f'runs/D103-profiler-support/execution/{label}.exit.json')['returncode']==0
H=ROOT/'runs/D103-profiler-support';p=H/'commit.json';old.save(p,{'at':old.now(),'commit':commit,'committed_paths':['research/postflop-gpu-20261016/experiments.md'],'all_owned_children_terminal':True,'source_restored_E051':True,'main_live_ptx_unchanged':True,'new_speedups_accepted':False,'compatibility_query_only':True,'counter_access_unverified':True,'last_primary_baseline':'B197','goal_active':True,'wording_correction':'Uncommitted ledger draft normalized unowned to owned child scope before commit; original executed closure script retained. No audit of unrelated processes claimed.'})
key='evidence/D103-profiler-support/commit.json';dst=old.ar.DASHBOARD/key;assert not dst.exists();dst.write_bytes(p.read_bytes())
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='D103');assert e['status']=='completed' and e['correctness']=='pass';e['evidence'].append({'label':'Local diagnostic ledger commit','url':key});s['updated_at']=old.now();old.ar.atomic_json(old.ar.STATUS,s)
assert old.ar.STATUS.is_relative_to(old.ar.DASHBOARD)
url=old.ar.LIVE+'/research/postflop-gpu-20261016/'+old.ar.STATUS.relative_to(old.ar.DASHBOARD).as_posix()
with urllib.request.urlopen(url,timeout=15) as response:served=json.loads(response.read())
for ident in ['D102','D103','E062','E063']:assert next(e for e in served['experiments'] if e['id']==ident)==next(e for e in s['experiments'] if e['id']==ident)
assert served['accepted_complete_run']==s['accepted_complete_run'] and served['accepted_complete_run']['candidate_id']=='E051' and served['active_experiment'] is None
old.custody();print(json.dumps({'status':'served_status_and_all_custody_verified','commit':commit,'accepted':{k:v for k,v in s['accepted_complete_run'].items() if k not in ['evidence','fixtures','requirements']},'next':'separately frozen counter-availability query','all_owned_children_terminal':True,'goal_active':True}),flush=True)
