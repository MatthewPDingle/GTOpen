"""Seal fresh feature and primary E051 builds after terminal raw controls."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E051-source';C=ROOT/'comparisons/E051-kernel-control/report.json';control=old.read(C)
assert control['status']=='pass_scoped_up_action_raw_equivalence' and control['cases']==819 and control['full_raw_files_equal']
T=ROOT/'runs/E051-kernel-control/execution/terminal.json';assert old.read(T)['returncode']==0
H=ROOT/'runs/E051-build-plan';H.mkdir();prior=ROOT/'runs/E048-build-plan'
(H/'build.py').write_text((prior/'build.py').read_text(encoding='utf-8').replace('E048','E051'),encoding='utf-8')
p=old.read(prior/'build-protocol.json');p.update(id='E051-final-build',at=old.now(),owned=old.read(D/'manifest.json')['owned'])
p['phases']=[{**x,'target':x['target'].replace('e048','e051'),'outputs':{k:v.replace('E048','E051') for k,v in x['outputs'].items()}} for x in p['phases']]
paths=[H/'build.py',D/'manifest.json',D/'source-review.json',C,T,ROOT/'runs/E051-resource/report.json',ROOT/'comparisons/E051-resource-root-check/report.json',ROOT/'runs/E051-kernel-control/protocol.json',ROOT/'runs/E051-kernel-control/execution/complete.json',ROOT/'runs/E051-kernel-control/audit.py',ROOT/'runs/E051-kernel-control/source-review.json',Path(p['protected_main']),ROOT/'runs/small-gain-confirmation-plan/common.py',ar.REPO/'tools/postflop_autoresearch.py']
for v in p['owned'].values():paths.extend([Path(v['base']),Path(v['candidate'])])
p['input_sha256']={str(x):old.sha(x) for x in paths};old.save(H/'build-protocol.json',p)
published={}
for directory in [H,ROOT/'runs/E051-kernel-control',C.parent]:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.pdb'] or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-build-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'performance_measured':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(stage='Raw controls passed; fresh feature and primary builds next',reason='819cases/1638launches,12375858output words/5199114actual immutable words/10240828guards exact; all actual mutable regions disjoint. Compiled register/occupancy prerequisite passed. Full solver timings pending.');e['evidence'].extend([{'label':'E051 complete raw GPU comparison','url':'evidence/E051-kernel-control/report.json'},{'label':'E051 final build protocol','url':'evidence/E051-build-plan/build-protocol.json'}]);st.update(state='running',stage='E051 fresh integrated builds',activity='Build feature and GPU-only test binaries; restore accepted E020 after each phase.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
print(json.dumps({'build_protocol_sha256':old.sha(H/'build-protocol.json'),'published':len(published)}),flush=True)
