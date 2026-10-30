"""Own one frozen compatibility batch; publish its complete evidence without adoption."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
assert len(sys.argv)==2;H=R/'runs/E080-broader-controls-plan';old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');old.custody();assert not(R/'gpu-run.lock').exists();M=R/'runs/E080-broader-controls-manager';assert not M.exists();M.mkdir()
print('E080 broader protocol',sys.argv[1],flush=True)
old.child([sys.executable,'-B',str(H/'native.py'),sys.argv[1]],M,'native',old.env(),2400)
E=R/'runs/E080-broader-controls-execution';receipt=old.read(M/'native.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
old.save(E/'terminal.json',{'at':old.now(),'returncode':0,'complete_sha256':old.sha(E/'complete.json'),'wrapper_receipt_sha256':old.sha(M/'native.exit.json')})
old.child([sys.executable,'-B',str(H/'root-check.py'),sys.argv[1]],M,'root-replay',old.env(),180)
old.child([sys.executable,'-B',str(H/'warm.py'),sys.argv[1]],M,'large-warm',old.env(),2100)
qpath=R/'comparisons/E080-broader-controls/report.json';rootpath=R/'comparisons/E080-broader-root-check/report.json';warmpath=R/'comparisons/E080-large-warm-controls/report.json';q=old.read(qpath);root=old.read(rootpath);warm=old.read(warmpath)
assert q['status']=='pass_broader_exact_controls_only'and root['status']=='pass_broader_only'and warm['status']=='pass_six_full_raw_large_warm_states_each'
old.custody();assert not(R/'gpu-run.lock').exists();O=R/'runs/E080-broader-closure';assert not O.exists();O.mkdir();reason='Broader controls passed: 160 state/menu/resume snapshots per arm, exact F32 records, postflop/preflop GPU suites, continuation checks and 720 stored-state passes per arm. Six full raw large warm compressed snapshots and complete saves per arm also match. Actual resource/material costs, holdout and fresh-original cumulative qualification remain. Not accepted.'
old.save(O/'decision.json',{'id':'E080-broader','at':old.now(),'status':'pass_broader_only','compatibility_report_sha256':old.sha(qpath),'root_report_sha256':old.sha(rootpath),'large_warm_report_sha256':old.sha(warmpath),'candidate_adopted':False,'reason':reason})
published=[]
folders=[H,M,E,R/'runs/E080-broader-build-plan',R/'runs/E080-broader-build-manager',R/'runs/E080-broader-build-manager-r2',R/'runs/E080-broader-warm-execution',O,qpath.parent,rootpath.parent,warmpath.parent,*[R/'runs'/x['id']for x in P['rows']]]
for folder in folders:
    for p in folder.iterdir():
        if not p.is_file()or p.suffix not in['.json','.log','.py','.rs']:continue
        key=folder.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
        published.append({'url':'evidence/'+key,'sha256':old.sha(p)})
for arm in['baseline','candidate']:
    p=R/'runs/E080-broader-warm-execution'/arm/'parsed.json';key='E080-large-warm-'+arm+'/parsed.json';dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
    published.append({'url':'evidence/'+key,'sha256':old.sha(p)})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080');e.update(status='measured',correctness='Broad controls and six full raw large warm states per arm pass',accepted=False,stage='Broader controls passed; material qualification next',reason=reason,updated_at=old.now());e['evidence'].extend([{'label':'Broad compatibility and exact saves','url':'evidence/E080-broader-controls/report.json'},{'label':'Broader raw-log replay','url':'evidence/E080-broader-root-check/report.json'},{'label':'Full raw large warm compressed states','url':'evidence/E080-large-warm-controls/report.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080',stage='E080 material qualification preparation',activity=reason+' Accepted and live E051 remain at 12.44% cumulative gain.');old.ar.atomic_json(old.ar.STATUS,s)
old.save(O/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':published,'bulk_raw_physically_S':True,'all_owned_children_terminal':True,'source_main_live_PTX_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E080 broader compatibility and large warm state'not in raw
entry=f'''

### E080 broader compatibility and large warm state

Previous turn completed frozen D131 component and exact E080 integration: 86 ordinary units, initial 2.4834500515% gain, then separate fresh16 1.7148158134% gain with 16/16 improving pairs and all 96 records/736 checkpoints exact. No adoption. Current source/main/live/protected PTX and idle state reverified. Broad preparation first formed a wrong manifest.exe path before any compiler; preserve original preparation and exact uncompiled sources, correct bookkeeping only. Five baseline compilers then succeeded, but a reused observer incorrectly required postflop CUDA text in the preflop-only test binary. Preserve failed verifier and all five terminal compiler outputs. Observer repair {old.sha(R/'runs/E080-broader-build-plan/protocol-r2.json')} requires actual preflop CUDA for that harness and original postflop CUDA elsewhere; no recompilation of completed work, no subject/flags/fixtures/source change. Seven remaining standalone compilers and one fresh continuation build completed; accepted source restored in finally.

Native protocol {sys.argv[1]} frozen and HTTP published before all broader observations. Eighteen fixed rows, baseline and candidate each: state/menu/resume controls, six postflop GPU and fifteen preflop GPU tests, three complete F32 fixtures, 160 alternating continuation sweeps, all three continuation symmetry tests, 720 stored full-state passes. All pass, 160 state/menu/resume snapshots per arm and latest three complete save files exact; broad report SHA {old.sha(qpath)}, root {root['checks']} checks SHA {old.sha(rootpath)}. Tolerance suites are distinct from the exact state/save comparisons. No primary or confirmation timing samples added.

Added one fixed canonical large two-tone compressed control per arm with {warm['verified_q_bytes']} q bytes, above the unchanged 64 MiB worker eligibility. Actual full-plan GPU warmup, iso compaction reconstruction, tight-budget rejection, query materialization and resync, complete save/load and resume. Each arm has three successful GPU constructors, one budget rejection, seven iterations and six complete raw q/scale snapshots. All six raw files and complete save bytes stream-compared, all root-query and non-path records exact; {warm['raw_bytes_retained']} raw bytes physically S and {warm['encoded_elements_per_arm']} encoded elements per arm. Report SHA {old.sha(warmpath)}. Eligibility is verified from actual byte lengths and pinned source; no independent worker-thread trace claimed. This establishes scoped actual warm-state parity, not whole-memory/capacity/responsiveness or performance proof.

All {len(published)} published artifacts HTTP byte verified; bulk stays S. All owned children terminal, GPU lock released, accepted source/main/live/protected PTX exact. E080 source/binaries unchanged, fresh16 and initial timing evidence preserved. No adoption or universal/no-tradeoff claim. Actual CPU/host/GPU peak, capacity/responsiveness, fixed holdout and fresh-original cumulative qualification remain. E051 accepted/live cumulative 12.4372274192% unchanged; last primary B271; goal active.
'''
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: qualify zero-validation overlap state and continuation behavior','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':'pass_broader_only','large_warm_raw_bytes':warm['raw_bytes_retained'],'published_files':len(published),'candidate_adopted':False}),flush=True)
