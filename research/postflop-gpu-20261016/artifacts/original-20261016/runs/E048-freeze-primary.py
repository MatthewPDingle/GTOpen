"""Freeze E048's protocol-owned validation ID and six prospective timing processes."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E048-final-source';B=ROOT/'runs/E048-build-plan';F=ROOT/'runs/E048-final-build';C=ROOT/'comparisons/E048-kernel-control/report.json'
assert old.read(F/'terminal.json')['returncode']==0 and old.read(F/'complete.json')['all_compilers_terminal']
control=old.read(C);assert control['status']=='pass_scoped_chance_raw_equivalence' and control['cases']==425 and control['full_raw_files_equal']
HERE=ROOT/'runs/E048-primary-plan';HERE.mkdir();PRIOR=ROOT/'runs/E047-primary-plan-r2'
for n in ['native.py','assess.py','root-check.py']:
 s=(PRIOR/n).read_text(encoding='utf-8').replace('E047','E048').replace('runs/E048-native-execution-r2','runs/E048-native-execution')
 s=s.replace('pass_scoped_up_action_raw_equivalence','pass_scoped_chance_raw_equivalence').replace("control['cases']==819","control['cases']==425")
 s=s.replace("assert P['control_ids']==['V047-unit']","assert len(P['control_ids'])==1 and P['control_ids'][0]==P['ordinary_unit_id']")
 assert 'V047-unit' not in s and 'E047' not in s
 (HERE/n).write_text(s,encoding='utf-8')
p=old.read(PRIOR/'protocol.json')
for k in list(p):
 if k.startswith('prior_'):p.pop(k)
p.update(id='E048-primary',at=old.now(),build_protocol_sha256=old.sha(B/'build-protocol.json'),candidate_owned_sha256={n:x['candidate_sha256'] for n,x in old.read(D/'manifest.json')['owned'].items()},gpu_control_report={'path':str(C),'sha256':old.sha(C)},ordinary_unit_id='V048-unit',control_ids=['V048-unit'],measurement_order=['B143','E048R1','E048R2','B144','B145','E048R3'],pairs=[{'baseline':'B143','candidate':'E048R1'},{'baseline':'B144','candidate':'E048R2'},{'baseline':'B145','candidate':'E048R3'}])
p['source_scope']='Three files: replace two canonical chance mask tests by existing card IDs, update all5 host/test caller bindings, remove2device masks and their exact GPU payload accounting. Public CPU plan/serialization and all float/state/quality/launch/readback behavior unchanged. Compiled resources/raw GPU controls scoped; full-solve behavior pending.'
p['adoption_requirements'][-1]='No material resource/capacity/compatibility/behavior cost. Before adoption verify actual mask-removal metadata/constructor payload, full continuation/F32 and module/lifetime behavior; scoped attributes and lower declared payload do not alone qualify this.'
paths=[HERE/n for n in ['native.py','assess.py','root-check.py']]+[C,D/'manifest.json',D/'source-review.json',B/'build-protocol.json',F/'complete.json',F/'terminal.json',ROOT/'runs/E048-kernel-control/protocol.json',ROOT/'runs/E048-kernel-control/execution/complete.json',ROOT/'runs/E048-kernel-control/audit.py',ROOT/'runs/E048-resource/report.json',ROOT/'comparisons/E048-resource-root-check/report.json',ROOT/'runs/D078-card-membership-source/caller-and-domain-review.json',ar.REPO/'tools/postflop_autoresearch.py',ar.REPO/'tools/postflop_compare.py',ar.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
for n in ['E048-solver','E048-postflop_autoresearch','SG-E020-postflop_autoresearch']:paths.extend([ROOT/'binaries'/(n+'.exe'),ROOT/'binaries'/(n+'.manifest.json')])
p['input_sha256']={str(x):old.sha(x) for x in paths}
status=old.read(ar.STATUS)
for identity in p['control_ids']+p['measurement_order']:assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in status['experiments'])
old.save(HERE/'protocol.json',p)
published={}
for directory in [HERE,D,B,F]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(HERE/'pre-timing-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'performance_measured':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);e=next(x for x in s['experiments'] if x['id']=='E048');e.update(stage='Integrated builds complete; ordinary and fixed primary next',reason='Both builds terminal/restored;425-case directGPU control passed. One84/4ordinary suite then six fixed complete-cycle processes.1% cutoff, strict fixture guard, no extension/adoption.');e['evidence'].append({'label':'E048 fixed primary protocol','url':'evidence/E048-primary-plan/protocol.json'});s.update(state='running',stage='E048 ordinary and fixed primary',activity='Protocol-owned V048-unit before B143/E048R1/E048R2/B144/B145/E048R3; E020 retained.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
print(json.dumps({'protocol_sha256':old.sha(HERE/'protocol.json'),'published_files':len(published)}),flush=True)
