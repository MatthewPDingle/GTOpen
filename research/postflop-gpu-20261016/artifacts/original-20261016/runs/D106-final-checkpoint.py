"""Seal this turn's progress and verify the actual served research status."""
import hashlib,json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D106-subtree-replication';S=ROOT/'runs/E065-source';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip()
assert subprocess.check_output(['git','log','-1','--format=%s'],cwd=old.REPO,text=True).strip()=='research: reject narrowed indices and stage exact betting-subtree replication'
assert not subprocess.check_output(['git','diff','--name-only','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,text=True).strip()
old.pin(S/'baseline-tree.rs',old.BASE['crates/solver/src/tree.rs']);manifest=old.read(S/'manifest.json');assert manifest['status']=='STAGED_NOT_FROZEN_FOR_NATIVE' and manifest['native_executions']==0
old.pin(S/'candidate-tree.rs',manifest['candidate_owned_sha256']['crates/solver/src/tree.rs'])
assert not (H/'execution').exists() and not list((ROOT/'binaries').glob('E065-*.exe')) and not list(ROOT.glob('build-e065-*'))
assert old.read(ROOT/'runs/E064-resource/execution/complete.json')['all_children_terminal']
for n in ['cl','probe']:assert old.read(ROOT/f'runs/D104-counter-availability/execution/{n}.exit.json')['returncode']==0
old.pin(old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md','2b4f173b98863272279c39302017608aa8a0976074a709fe09e61af5a4b0735f')
# Preserve the exact mutable-ledger bytes cited by the source audit. It was
# taken after E064 closure and before appending the D106 staging entry.
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();wanted=old.read(H/'source-audit.json')['source_sha256'][str(ledger)]
end=raw.index(b'### D106 repeated betting-subtree');snapshot=None
for trim in range(0,16):
 part=raw[:end-trim]
 if hashlib.sha256(part).hexdigest()==wanted:snapshot=part;break
assert snapshot is not None
snap=H/'ledger-source-audit-snapshot.md';assert not snap.exists();snap.write_bytes(snapshot);old.pin(snap,wanted)
old.save(H/'ledger-snapshot-provenance.json',{'at':old.now(),'snapshot_sha256':wanted,'snapshot_path':str(snap),'original_path':str(ledger),'current_ledger_commit':head,'method':'Exact hash-matching byte prefix before current D106append; no rewording/normalization of historical evidence.'})
old.save(H/'checkpoint.json',{'at':old.now(),'goal_turn_classification':'progress','actual_progress':['D104one availability size/fill attempt: HardwareBusy26at fill, cleanup and no retry','D10555,427,463integer addresses proven, no GPU floating values','E064allocated-resource/occupancy/maxthreads rejection before application kernels','D106source finding and E065exact-layout subtree-replication code staged off-tree; no native execution yet'],'goal_active':True,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'last_primary_baseline':'B197','all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'next_required_action':'Implement/review/freeze/run CPU TreeBuilder original/candidate controls from E065staged files and D106next-native-design.json. Full raw typed tree/capacity/error equality and fixed component admission first. No native command is currently pending; no execution protocol exists yet. Do not rerun unavailable counter route or closed source families.','staged_source_sha256':manifest['candidate_owned_sha256'],'native_execution_for_staged_E065':0,'no_new_speedup_accepted':True})
old.save(H/'commit.json',{'at':old.now(),'commit':head,'committed_paths':['research/postflop-gpu-20261016/experiments.md'],'closed_candidate':'E064','staged_candidate':'E065','staged_candidate_native_executions':0,'all_owned_children_terminal':True,'new_speedup_accepted':False,'goal_active':True})
published={}
for name in ['ledger-source-audit-snapshot.md','ledger-snapshot-provenance.json','checkpoint.json','commit.json']:
 p=H/name;key='evidence/D106-subtree-replication/'+name;dst=old.ar.DASHBOARD/key;assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'final-publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='E065');assert e['status']=='preparing' and e['correctness']=='pending' and not e['accepted'];e['evidence'].extend([{'label':'Exact source-audit ledger snapshot','url':'evidence/D106-subtree-replication/ledger-source-audit-snapshot.md'},{'label':'Turn checkpoint and next native controls','url':'evidence/D106-subtree-replication/checkpoint.json'},{'label':'Local research ledger commit','url':'evidence/D106-subtree-replication/commit.json'}]);s['updated_at']=old.now();old.ar.atomic_json(old.ar.STATUS,s)
url=old.ar.LIVE+'/research/postflop-gpu-20261016/'+old.ar.STATUS.relative_to(old.ar.DASHBOARD).as_posix()
with urllib.request.urlopen(url,timeout=15) as response:served=json.loads(response.read())
for ident in ['D104','D105','D106','E064','E065']:assert next(e for e in served['experiments'] if e['id']==ident)==next(e for e in s['experiments'] if e['id']==ident)
assert served['accepted_complete_run']==s['accepted_complete_run'] and served['accepted_complete_run']['candidate_id']=='E051' and served['accepted_complete_run']['observed_gain_pct']==12.4372274192464 and served['active_experiment']=='E065'
old.custody();print(json.dumps({'status':'turn_progress_sealed_and_actual_served_status_verified','commit':head,'accepted_gain_pct':served['accepted_complete_run']['observed_gain_pct'],'staged_candidate':'E065','staged_native_executions':0,'all_owned_children_terminal':True,'goal_active':True}),flush=True)
