"""Publish fixed broader controls and observed workspace payload without adoption."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E051-broader-controls-plan';P=old.read(H/'protocol.json');E=ROOT/'runs/E051-broader-controls-execution';O=ROOT/'comparisons/E051-broader-controls';R=ROOT/'comparisons/E051-broader-root-check';q=old.read(O/'report.json');r=old.read(R/'report.json')
assert q['status']=='pass_broader_exact_controls_only' and r['status']=='pass_broader_only'
T=old.read(E/'terminal.json');assert T['returncode']==0 and T['complete_sha256']==old.sha(E/'complete.json')
workspace={}
for arm in ['baseline','candidate']:
 path=ROOT/'runs'/('V051-stored-'+arm)/'stdout.log';text=path.read_text(encoding='utf-8');rows=[json.loads(x.split('GPU_STORED_SUMMARY ',1)[1]) for x in text.splitlines() if 'GPU_STORED_SUMMARY ' in x];assert len(rows)==1
 workspace[arm]={'workspace_bytes':rows[0]['workspace_bytes'],'source_stdout_sha256':old.sha(path)}
assert workspace['baseline']['workspace_bytes']==workspace['candidate']['workspace_bytes']
old.save(O/'workspace-payload-observation.json',{'at':old.now(),'actual_mutable_workspace_bytes':workspace,'equal':True,'scope':'Actual StoredWorkspace CUDA slice payload after fixed720pass control. Excludes immutable metadata,module/context/driver allocations,pinned memory,allocator bookkeeping and peak temporaries; not complete capacity qualification.'})
published={}
directories=[H,E,O,R]+[ROOT/'runs'/row['id'] for row in P['rows']]
for directory in directories:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==data
  published[key]=old.sha(src)
for arm,files in q['latest_complete_save_files'].items():
 for name,meta in files.items():
  src=Path(meta['path']);old.pin(src,meta['sha256']);key='E051-broader-save-files/'+arm+'/'+name;dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==src.read_bytes()
  published[key]=old.sha(src)
old.save(O/'publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'candidate_accepted':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(status='preparing',stage='Broader controls passed; capacity/holdout/cumulative remain',reason='160ordered snapshots each,all3F32fixtures,sixGPUtests each,paging160sweeps and720stored passes each match. Latest3complete saves byte-exact; actual mutable workspace payload equal. Complete material-capacity/holdout/fresh-original cumulative gates pending; no adoption.');e['evidence'].extend([{'label':'E051 complete broader result','url':'evidence/E051-broader-controls/report.json'},{'label':'E051 broader root replay','url':'evidence/E051-broader-root-check/report.json'},{'label':'E051 actual mutable workspace payload','url':'evidence/E051-broader-controls/workspace-payload-observation.json'}]);st.update(state='running',stage='E051 material-capacity and holdout preparation',activity='Broad exactness passed. Preserve2.1751731507% fresh16 timing result; adoption awaits remaining gates.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
text=f'''

### E051 broader correctness controls

Build protocol {old.sha(ROOT/'runs/E051-broader-build-plan/protocol.json')} linked8fresh standalone correctness binaries from exact tracked state/menu/resume/GPU test sources and pinned accepted/candidate primary solver rlibs. Only compile-time CARGO_MANIFEST_DIR is relocated to separate S: save roots; no harness text changed. Own CUDA source must be embedded and opposite source absent. Two fresh candidate continuation integration binaries came from a separate Cargo feature target; every artifact was newly compiled and candidate CUDA embedded. Build session81305 returned0; accepted162 restored before any native. Existing feature-unit reference source map matches acceptedE020 exactly; candidate unit differs only in the intended CUDA helper.

Broader protocol {old.sha(H/'protocol.json')} froze16before/after invocations. Session4535 completed once:24state,24menu and112resume snapshots perarm exactly match eachother and historical acceptedE020 controls; allthree F32full non-timing fixtures/23checkpoints perarm match the acceptedF32anchor. Both six-test GPU/CPU tolerance suites pass, distinct from the exact original/candidate comparisons. Paging160alternating sweeps, invalid-input rejection and720unique stored full-device/restored/value bitwise passes succeed in eacharm. Full latest state/menu/resume save bytes are compared and retained onS/public evidence. Actual final mutable workspace payload is {workspace['baseline']['workspace_bytes']}bytes in botharms; this excludes metadata/context/module/pinned/allocator/peak costs and is not complete capacity evidence.

Broader report {old.sha(O/'report.json')} and58check root log/payload/save-byte replay {old.sha(R/'report.json')} preserve the results. Root replay is not external independent review. All artifacts are served and HTTP byte-verified; checkoutoutputs remain only the two preexisting protected PTX files. No broad-control timing is used as a speed result and no forced SSD spill is claimed. Material capacity, fixed wide-turn holdout and fresh-original cumulative qualification remain pending before source adoption. Accepted E020/main/HEAD/live/PTX remain unchanged; goal active.
'''
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';data=ledger.read_bytes();assert b'### E051 broader correctness controls' not in data;nl=b'\r\n' if b'\r\n' in data else b'\n';ledger.write_bytes(data+text.encode('utf-8').replace(b'\n',nl))
print(json.dumps({'status':'pass_broader_only','workspace_bytes_each':workspace['baseline']['workspace_bytes'],'published':len(published),'publication_sha256':old.sha(O/'publication.json')}),flush=True)
