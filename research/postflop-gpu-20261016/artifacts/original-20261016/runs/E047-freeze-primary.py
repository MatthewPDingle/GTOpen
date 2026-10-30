"""Freeze E047 ordinary84/4 and fixed three paired complete-cycle observations."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E047-final-source';B=ROOT/'runs/E047-build-plan';F=ROOT/'runs/E047-final-build';C=ROOT/'comparisons/E047-kernel-control-r2/report.json'
assert old.read(F/'terminal.json')['returncode']==0 and old.read(F/'complete.json')['all_compilers_terminal']
assert old.read(C)['cases']==819 and old.read(C)['status']=='pass_scoped_up_action_raw_equivalence'
HERE=ROOT/'runs/E047-primary-plan';HERE.mkdir()
for n in ['native.py','assess.py']:
 s=(ROOT/'runs/E042-primary-plan'/n).read_text(encoding='utf-8').replace('E042','E047').replace("control['cases']==717","control['cases']==819");(HERE/n).write_text(s,encoding='utf-8')
s=(ROOT/'runs/E042-primary-plan/root-check.py').read_text(encoding='utf-8').replace('E042','E047').replace('import datetime,json,statistics,sys','import datetime,json,math,statistics,sys')
needle='gain=100*(bs-cs)/bs;passed=';assert s.count(needle)==1
s=s.replace(needle,"bs=math.fsum(f['baseline_median_ms'] for f in fixture);cs=math.fsum(f['candidate_median_ms'] for f in fixture)\ngain=100*(bs-cs)/bs;passed=")
(HERE/'root-check.py').write_text(s,encoding='utf-8')
p=old.read(ROOT/'runs/E042-primary-plan/protocol.json');p.update(id='E047-primary',at=old.now(),build_protocol_sha256=old.sha(B/'build-protocol.json'),candidate_owned_sha256={n:x['candidate_sha256'] for n,x in old.read(D/'manifest.json')['owned'].items()},gpu_control_report={'path':str(C),'sha256':old.sha(C)},control_ids=['V047-unit'],measurement_order=['B140','E047R1','E047R2','B141','B142','E047R3'],pairs=[{'baseline':'B140','candidate':'E047R1'},{'baseline':'B141','candidate':'E047R2'},{'baseline':'B142','candidate':'E047R3'}])
p['source_scope']='Only kernels.cu: one-action dispatch to unchanged helper<1> in existing up_action. No other helper/body/host/plan/field/entry/launch/allocation change. Same queried resources and other8 entries/ABI; additional code/dispatch and compile/module costs must be measured.'
p['adoption_requirements'][-1]='No material memory/capacity/compatibility/behavior costs, including compiled module/graph resources and dispatch/initialization overhead. Probe equality is scoped and never alone qualifies adoption.'
paths=[HERE/n for n in ['native.py','assess.py','root-check.py']]+[C,D/'manifest.json',D/'source-review.json',D/'candidate.patch',B/'build-protocol.json',F/'complete.json',F/'terminal.json',ROOT/'runs/E047-kernel-control/protocol.json',ROOT/'runs/E047-kernel-control/execution/complete-r2.json',ROOT/'runs/E047-kernel-control/execution/wrapper-failure.json',ROOT/'runs/E047-kernel-control/audit-r2.py',ROOT/'runs/E047-resource/report.json',ROOT/'comparisons/E047-resource-root-check/report.json',ar.REPO/'tools/postflop_autoresearch.py',ar.REPO/'tools/postflop_compare.py',ar.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
for n in ['E047-solver','E047-postflop_autoresearch','SG-E020-postflop_autoresearch']:paths.extend([ROOT/'binaries'/(n+'.exe'),ROOT/'binaries'/(n+'.manifest.json')])
p['input_sha256']={str(x):old.sha(x) for x in paths}
s=old.read(ar.STATUS)
for identity in p['control_ids']+p['measurement_order']:assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in s['experiments'])
old.save(HERE/'protocol.json',p)
published={}
for directory in [HERE,D,B,F]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);raw=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==raw
  else:dst.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(src)
old.save(HERE/'pre-timing-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'performance_measured':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 status=old.read(ar.STATUS);e=next(x for x in status['experiments'] if x['id']=='E047');e.update(stage='Fresh builds complete; ordinary and fixed primary next',reason='Resource and819-case raw controls passed. Both builds terminal/restored. One ordinary84/4 suite then fixed3pairs;1% aggregate and strict fixture guards, no extensions/adoption.');e['evidence'].append({'label':'E047 frozen primary protocol','url':'evidence/E047-primary-plan/protocol.json'});status.update(state='running',stage='E047 ordinary and fixed primary',activity='One ordinary suite then six frozen complete-cycle processes; accepted E020 retained.',updated_at=ar.now());ar.atomic_json(ar.STATUS,status)
print(json.dumps({'protocol_sha256':old.sha(HERE/'protocol.json'),'published_files':len(published)}),flush=True)
