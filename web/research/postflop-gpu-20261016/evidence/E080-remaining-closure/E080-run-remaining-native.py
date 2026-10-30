"""Run and publish the fixed capacity/holdout/cumulative package once."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
assert len(sys.argv)==2;H=R/'runs/E080-remaining-native-plan';old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');old.custody();assert not(R/'gpu-run.lock').exists();M=R/'runs/E080-remaining-native-manager';assert not M.exists();M.mkdir();print('E080 remaining protocol',sys.argv[1],flush=True)
old.child([sys.executable,'-B',str(H/'native.py'),sys.argv[1]],M,'native',old.env(),2400)
old.child([sys.executable,'-B',str(H/'root-check.py'),sys.argv[1]],M,'root-replay',old.env(),180)
O=R/'comparisons/E080-remaining-native';X=R/'comparisons/E080-remaining-root-check/report.json';root=old.read(X);hold=old.read(O/'holdout.json');passed=root['status']=='pass_remaining_timing_and_capacity_only';old.custody();assert not(R/'gpu-run.lock').exists();D=R/'runs/E080-remaining-closure';assert not D.exists();D.mkdir()
if passed:reason=f"Actual owned capacity matches in all six cases per arm. Fixed wide-turn holdout passed ({hold['observed_gain_pct']:.6f}% gain) with six exact raw files and 36 checkpoints. Fresh original comparison measured {root['cumulative_gain_pct']:.6f}% cumulative gain. Actual resource costs, responsiveness and final scope audit remain; not accepted."
else:reason=('Rejected by the repeatable wide-turn holdout slowdown guard.'if root['holdout_guard_failed']else'Rejected by the fresh-original cumulative gate.')+' All fixed observations are retained. No extra samples, source, threshold, helper, thread, placement or eligibility variants or rescue runs. Accepted and live E051 are unchanged.'
old.save(D/'decision.json',{'id':'E080-remaining','at':old.now(),'status':'passed_remaining_pending_resource_audit'if passed else'rejected','reason':reason,'root_report_sha256':old.sha(X),'holdout_gain_pct':hold['observed_gain_pct'],'cumulative_gain_pct':root['cumulative_gain_pct'],'source_adopted':False,'research_equivalence_cleared':False})
pub=[]
def publish(p,key):
    dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
    else:shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
    pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
for folder in[H,M,R/'runs/E080-remaining-build-plan',R/'runs/E080-remaining-build-manager',D,O,X.parent]:
    for p in folder.iterdir():
        if p.is_file()and p.suffix in['.json','.py','.rs','.log']:publish(p,folder.name+'/'+p.name)
for folder in[R/'runs/E080-remaining-native-execution',R/'runs/E080-remaining-build']:
    for p in folder.rglob('*'):
        if p.is_file()and p.suffix in['.json','.log']:publish(p,folder.name+'/'+p.relative_to(folder).as_posix())
for identity in P['cumulative_order']:
    folder=R/'runs'/identity
    if folder.exists():
        for p in folder.iterdir():
            if p.is_file()and p.suffix in['.json','.log']:publish(p,identity+'/'+p.name)
for stem in['E080-capacity-candidate','E080-holdout-candidate']:publish(R/'binaries'/(stem+'.manifest.json'),'E080-remaining-binary-manifests/'+stem+'.manifest.json')
publish(Path(__file__),D.name+'/'+Path(__file__).name)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080');e.update(status='measured'if passed else'rejected',accepted=False,stage='Capacity, holdout and cumulative gates passed; resource audit next'if passed else'Closed: holdout or cumulative gate failed',reason=reason,updated_at=old.now());e['evidence'].extend([{'label':'Actual owned capacity','url':'evidence/E080-remaining-native/capacity.json'},{'label':'Fixed holdout and complete raw states','url':'evidence/E080-remaining-native/holdout.json'},{'label':'Remaining gates root replay','url':'evidence/E080-remaining-root-check/report.json'},{'label':'Qualification decision','url':'evidence/E080-remaining-closure/decision.json'}])
    if root['cumulative_gain_pct']is not None:e['cumulative_timing_gain_pct']=root['cumulative_gain_pct'];e['evidence'].append({'label':'Fresh original-to-candidate comparison','url':'evidence/E080-remaining-native/cumulative.json'})
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080'if passed else None,stage='E080 actual resource qualification preparation'if passed else'Investigating the next GPU optimization',activity=reason+' Deployed accepted E051 cumulative gain remains 12.44%.');old.ar.atomic_json(old.ar.STATUS,s)
old.save(D/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'bulk_raw_physically_S':True,'all_owned_children_terminal':True,'source_main_live_PTX_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E080 actual capacity, fixed holdout and fresh original comparison'not in raw
entry=f'''

### E080 actual capacity, fixed holdout and fresh original comparison

Prior turn completed 18 broad rows, including preserved deliberate experimental changing-range symmetry failure in both baseline/candidate with all 65 scientific/allocation lines identical. No test gate was relabeled green and that research path remains uncleared. State/menu/resume 160 snapshots per arm, ordinary GPU/preflop/F32/paging/stored controls and six complete raw large warm snapshots per arm match; 16,692,856,704 raw bytes retained physically S. E080 source and timing cohorts remain unchanged, initial 2.4834500515% and separate fresh16 1.7148158134% with all16pairs improving. No adoption.

Build only missing candidate capacity and holdout evaluators from exact existing source/fixture and pinned feature/primary libraries; reuse verified accepted E051 baseline evaluators. Two compilers terminal zero, no source activation. Freeze native protocol {sys.argv[1]} before observations. Explicit absolute artifact root, original capacity marker and the established r3 real outer-clock >= component-sum observer behavior retained before native; no outcome-driven repairs.

Both actual capacity probes run once across six fixed cases per arm, all retained metadata/canonical-state/workspace/public-wrapper sizes exact. Device-wide free-memory observations remain unscored; zero solver iterations, no forced spill or whole-memory proof. Fixed H080B1/H080C1,H080C2/H080B2,H080B3/H080C3 unchanged full169 turn, target0.3%/check20/max400; all six full non-timing payloads, 36 checkpoints and entire raw q/scale files exact to accepted historical anchor. Holdout gain {hold['observed_gain_pct']}%, paired slowdown {hold['paired_slowdown_pct']}, strict guard failed {hold['strict_guard_failed']}. {'Cumulative was not executed after holdout rejection.'if root['holdout_guard_failed']else'Fresh original B272/E080O1,E080O2/B273,B274/E080O3 complete cycles then ran, with all18records/138checkpoints exact; observed cumulative gain '+str(root['cumulative_gain_pct'])+'% and guards '+json.dumps(root['cumulative_guards'],separators=(',',':'))+'.'} Root {root['checks_passed']} checks; report {old.sha(X)}. {reason}

All observations retained; no timing pooling, exclusions, extra samples or source variants. All {len(pub)} published artifacts HTTP byte verified; bulk raw physically S. All owned children terminal, GPU lock released, source/main/live/protected PTX exact. Actual CPU/host/GPU peak, responsiveness and final source/scope audit remain if performance gates pass. Experimental research failure stays failed and is not cleared. Accepted/deployed E051 cumulative 12.4372274192% unchanged; last primary {'B271'if root['holdout_guard_failed']else'B274'}; goal active; no source adoption.
'''
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: qualify zero-validation overlap capacity and heldout performance','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':'remaining_pass_pending_resource_audit'if passed else'rejected','holdout_gain_pct':hold['observed_gain_pct'],'cumulative_gain_pct':root['cumulative_gain_pct'],'published_files':len(pub),'candidate_adopted':False}),flush=True)
