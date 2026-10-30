"""Freeze unexecuted original observations; never rerun or relax the failed test."""
from pathlib import Path
import ast,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());H=R/'runs/E080-broader-controls-plan';P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
failure=R/'runs/E080-broader-controls-execution/failure.json';f=old.read(failure);assert len(f['completed_rows'])==14
br=old.read(R/'runs/V080-symmetry-baseline/report.json');assert br['status']=='invalid'and br['returncode']==101
receipt=old.read(R/'runs/E080-broader-controls-manager/native.exit.json');assert receipt['returncode']==1 and receipt['error']is receipt['cleanup']is None
doc=old.REPO/'research/preflop-evolution/symmetric-bridge-20260919/DIAGNOSTICS.md';text=doc.read_text(encoding='utf-8');assert '0.022339 bb two-tone and 0.016563 bb monotone' in text and 'Preserve that failed' in text
rows=[x for x in P['rows']if x['id']in['V080-symmetry-candidate','V080-stored-baseline','V080-stored-candidate']];assert len(rows)==3
for row in rows:assert not(R/'runs'/row['id']).exists()
assert not(R/'runs/E080-broader-warm-execution').exists();ast.parse((H/'continue-observations.py').read_text(encoding='utf-8'))
paths=[Path(__file__),H/'continue-observations.py',H/'protocol.json',doc,failure,R/'runs/E080-broader-controls-manager/native.exit.json',R/'runs/V080-symmetry-baseline/report.json',R/'runs/V080-symmetry-baseline/stdout.log']
for row in f['completed_rows']:paths.extend([R/'runs'/row['id']/'report.json',R/'runs'/row['id']/'stdout.log'])
extra={'id':'E080-remaining-original-broader-observations','at':old.now(),'original_protocol_sha256':old.sha(H/'protocol.json'),'remaining_rows':rows,'historical_failure_document':str(doc),'input_sha256':P['input_sha256']|{str(p):old.sha(p)for p in paths},'scope':'Continue only the unexecuted candidate symmetry and two stored rows plus the originally frozen large warm controls. All original test cases, seeds, flags, binaries, source and thresholds are unchanged. The accepted-baseline failed test is not reexecuted, removed or turned green. A matching failed candidate outcome is recorded as failure parity only, never as research-equivalence approval or automatic adoption. Source/material/scope audit still required.'}
old.save(H/'continuation-protocol.json',extra)
for p in[Path(__file__),H/'continue-observations.py',H/'continuation-protocol.json']:
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'continuation-pre-native-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'continuation-protocol.json'),'new_solver_observations':0,'original_failed_test_reexecution':False,'HTTP_byte_verified':True})
print('E080 continuation observation protocol',old.sha(H/'continuation-protocol.json'),flush=True)
M=R/'runs/E080-broader-observation-parent';assert not M.exists();M.mkdir();old.child([sys.executable,'-B',str(H/'continue-observations.py'),old.sha(H/'continuation-protocol.json')],M,'remaining',old.env(),3900);old.custody();print('E080 original remaining observations terminal.',flush=True)
