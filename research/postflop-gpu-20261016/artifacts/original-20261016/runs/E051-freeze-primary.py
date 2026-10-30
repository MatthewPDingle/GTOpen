"""Freeze ordinary units and the untouched fixed1% primary screen for E051."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E051-source';B=ROOT/'runs/E051-build-plan';F=ROOT/'runs/E051-final-build';C=ROOT/'comparisons/E051-kernel-control/report.json'
assert old.read(F/'terminal.json')['returncode']==0 and old.read(F/'complete.json')['all_compilers_terminal']
control=old.read(C);assert control['status']=='pass_scoped_up_action_raw_equivalence' and control['cases']==819 and control['full_raw_files_equal']
H=ROOT/'runs/E051-primary-plan';H.mkdir();prior=ROOT/'runs/E048-primary-plan'
for name in ['native.py','assess.py','root-check.py']:
 s=(prior/name).read_text(encoding='utf-8').replace('E048','E051').replace('pass_scoped_chance_raw_equivalence','pass_scoped_up_action_raw_equivalence').replace("control['cases']==425","control['cases']==819")
 assert 'E048' not in s and 'V048' not in s and '425' not in s
 (H/name).write_text(s,encoding='utf-8')
p=old.read(prior/'protocol.json')
p.update(id='E051-primary',at=old.now(),build_protocol_sha256=old.sha(B/'build-protocol.json'),candidate_owned_sha256={n:v['candidate_sha256'] for n,v in old.read(D/'manifest.json')['owned'].items()},gpu_control_report={'path':str(C),'sha256':old.sha(C)},ordinary_unit_id='V051-unit',control_ids=['V051-unit'],measurement_order=['B149','E051R1','E051R2','B150','B151','E051R3'],pairs=[{'baseline':'B149','candidate':'E051R1'},{'baseline':'B150','candidate':'E051R2'},{'baseline':'B151','candidate':'E051R3'}])
p['source_scope']='One CUDA file/helper: move independent unlocked own-node strategy FMA/store into existing expectation loop; same ordered out accumulation and final regret formulas. No new array/cache/alias qualifier/arity/host/launch/precision/quality change. Supported production buffers independently owned; actual disjoint device extents witnessed in every raw control arm.'
p['adoption_requirements'][-1]='No material resource/capacity/compatibility/behavior cost. After separately frozen16pairs require full F32/state/menu/resume/continuation and fixed holdout/fresh-original cumulative qualification. Lower registers/theoretical occupancy plus direct kernel equivalence do not establish actual solver speed or universal behavior.'
paths=[H/n for n in ['native.py','assess.py','root-check.py']]+[C,D/'manifest.json',D/'source-review.json',B/'build-protocol.json',F/'complete.json',F/'terminal.json',ROOT/'runs/E051-kernel-control/protocol.json',ROOT/'runs/E051-kernel-control/execution/complete.json',ROOT/'runs/E051-kernel-control/execution/terminal.json',ROOT/'runs/E051-kernel-control/audit.py',ROOT/'runs/E051-kernel-control/source-review.json',ROOT/'runs/E051-resource/report.json',ROOT/'comparisons/E051-resource-root-check/report.json',ar.REPO/'tools/postflop_autoresearch.py',ar.REPO/'tools/postflop_compare.py',ar.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
for name in ['E051-solver','E051-postflop_autoresearch','SG-E020-postflop_autoresearch']:paths.extend([ROOT/'binaries'/(name+'.exe'),ROOT/'binaries'/(name+'.manifest.json')])
p['input_sha256']={str(x):old.sha(x) for x in paths}
st=old.read(ar.STATUS)
for identity in p['control_ids']+p['measurement_order']:assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in st['experiments'])
old.save(H/'protocol.json',p)
published={}
for directory in [H,F]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'performance_measured':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(stage='Builds terminal; ordinary and fixed primary next',reason='Fresh feature/primary artifacts restored to accepted source.819direct cases exact including actual disjoint address ranges. One84/4ordinary suite then six fixed complete-cycle processes;1% cutoff and strict fixture guard.');e['evidence'].append({'label':'E051 fixed primary protocol','url':'evidence/E051-primary-plan/protocol.json'});st.update(state='running',stage='E051 ordinary and fixed primary',activity='V051-unit before B149/E051R1/E051R2/B150/B151/E051R3; no adoption.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'published':len(published)}),flush=True)
