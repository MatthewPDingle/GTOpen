"""Run, assess, replay and publish the frozen fresh16 cohort once."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
assert len(sys.argv)==2;H=R/'runs/E080-confirmation-plan';old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');old.custody();assert not(R/'gpu-run.lock').exists()
for p,h in P['input_sha256'].items():old.pin(p,h)
M=R/'runs/E080-confirmation-manager';assert not M.exists();M.mkdir();print('E080 fresh16 protocol',sys.argv[1],flush=True)
old.child([sys.executable,'-B',str(H/'run.py'),sys.argv[1]],M,'confirmation',old.env(),2400)
qpath=R/'comparisons/E080-fresh16-confirmation/report.json';rpath=R/'comparisons/E080-fresh16-root-check/report.json';q=old.read(qpath);r=old.read(rpath);passed=q['performance']['fresh_confirmation_pass']
assert r['aggregate_gain_pct']==q['performance']['observed_gain_pct']and r['status']==('pass_timing_only'if passed else'pass_rejected')and q['exactness']=={'full_results':96,'convergence_checkpoints':736,'all_exact':True}
assert q['excluded_samples']==[]and q['extension_runs']==0 and q['historical_timing_samples_used']==0
old.custody();assert not(R/'gpu-run.lock').exists();O=R/'runs/E080-confirmation-closure';assert not O.exists();O.mkdir()
reason=f"Fresh16 complete-solve gain {q['performance']['observed_gain_pct']:.6f}%, with {q['performance']['positive_pairs']} improving pairs. All 96 result records and 736 checkpoints are exact. "
if passed:reason+='Fresh timing confirmation passed. Broader compatibility, actual CPU and memory/capacity costs, responsiveness, holdout and fresh-original cumulative qualification remain. Not accepted.'
else:reason+='Rejected by the fixed confirmation gates: '+', '.join(k for k,v in q['gates'].items()if not v)+'. No source, threshold, helper, placement or thread variants, extra samples or rescue runs.'
old.save(O/'decision.json',{'id':'E080-fresh16','at':old.now(),'decision':q['decision'],'performance':q['performance'],'gates':q['gates'],'assessment_sha256':old.sha(qpath),'root_replay_sha256':old.sha(rpath),'source_adopted':False,'accepted_and_live_source':'E051','reason':reason})
published=[]
folders=[H,M,R/'runs/E080-confirmation-wrapper',R/'runs/E080-confirmation-execution',O,qpath.parent,rpath.parent,*[R/'runs'/x for x in P['measurement_order']]]
for folder in folders:
    for p in folder.iterdir():
        if not p.is_file()or p.suffix not in['.py','.json','.log']:continue
        key=folder.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
        published.append({'url':'evidence/'+key,'sha256':old.sha(p)})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080')
    e.update(status='measured'if passed else'rejected',accepted=False,stage='Fresh timing passed; broader qualification pending'if passed else'Closed: fresh confirmation failed',reason=reason,updated_at=old.now(),observed_gain_pct=q['performance']['observed_gain_pct'])
    e['evidence'].extend([{'label':'Fresh16 timing and all gates','url':'evidence/E080-fresh16-confirmation/report.json'},{'label':'Fresh16 raw arithmetic replay','url':'evidence/E080-fresh16-root-check/report.json'},{'label':'Confirmation decision','url':'evidence/E080-confirmation-closure/decision.json'}])
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080'if passed else None,stage='E080 broader qualification preparation'if passed else'Investigating the next GPU optimization',activity=reason+' Accepted and live E051 remain at 12.44% cumulative gain.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.save(O/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':published,'all_owned_children_terminal':True,'accepted_main_live_PTX_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E080 fresh16 confirmation'not in raw
entry=f'''

### E080 fresh16 confirmation

Initial three-pair screen advanced at 2.4834500515% gain, with all 18 result records and 138 checkpoints exact and no fixture guard failure. Initial samples were prerequisites only and not pooled. Separately frozen confirmation protocol {sys.argv[1]} used the same source, binaries, quality, stop rules and three canonical fixtures: exactly B256-B271/E080C01-C16 in balanced BC/CB/CB/BC order across four blocks. No source changes, exclusions, extensions, historical pooling or added rescue runs. Previously passed 86 ordinary units were not reexecuted.

All 32 processes completed successfully. All 96 full non-timing records and 736 convergence checkpoints are exact. Full-cycle fixture medians sum {q['performance']['baseline_full_cycle_ms']} to {q['performance']['candidate_full_cycle_ms']} ms, gain {q['performance']['observed_gain_pct']}%; {q['performance']['positive_pairs']} improving pairs. Pair median {q['performance']['pair_median_gain_pct']}%; block medians {q['performance']['block_median_gains_pct']}; order medians {q['performance']['order_strata_median_gains_pct']}. Fixed gates {json.dumps(q['gates'],separators=(',',':'))}; fixture values {json.dumps([{'id':x['fixture_id'],'gain_pct':x['gain_pct'],'slower_pairs':x['slower_pairs'],'guard_failed':x['fixture_guard_failed']}for x in q['fixtures']],separators=(',',':'))}. Report SHA {old.sha(qpath)}, root replay {r['checks']} checks SHA {old.sha(rpath)}. {reason}

This is registered warm-cache timing and fingerprint/record confirmation, not universal speed or no-tradeoff proof. Broad F32/state/menu/save/resume/continuation, actual CPU/host/GPU peak/capacity/responsiveness, fixed holdout and fresh-original cumulative qualification have not run for E080. Primary whole-arena fingerprints are exact; primary raw arena byte streams were not independently compared. All {len(published)} artifacts were HTTP byte verified. All owned children are terminal, GPU lock released, source/main/live/protected PTX custody exact. Accepted and deployed E051 remains at 12.4372274192% cumulative measured gain; no source adoption. Last primary B271; goal active.
'''
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody()
subprocess.run(['git','commit','--only','-m','research: confirm zero-validation overlap on sixteen fresh pairs','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody();print(json.dumps({'decision':q['decision'],'gain_pct':q['performance']['observed_gain_pct'],'positive_pairs':q['performance']['positive_pairs'],'published_files':len(published),'candidate_adopted':False}),flush=True)
