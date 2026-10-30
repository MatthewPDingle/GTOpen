"""Only after successful controls, freeze and publish six new E045 processes."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
C=ROOT/'runs/E045-control-execution/complete.json';c=old.read(C)
assert c['status']=='pass_scoped_parallel_zero_proof' and c['integer_or_checks']==3516 and c['full_predicate_cases']==576 and c['unit_passed']==86
D=ROOT/'runs/E045-design-r2';B=ROOT/'runs/E045-build-plan-r2';F=ROOT/'runs/E045-final-build-r2'
HERE=ROOT/'runs/E045-primary-plan';HERE.mkdir()
current="assert control['status']=='pass_scoped_parallel_zero_proof' and control['integer_or_checks']==3516 and control['full_predicate_cases']==576 and control['unit_passed']==86"
for n in ['native.py','assess.py']:
 s=(ROOT/'runs/E041-primary-plan'/n).read_text(encoding='utf-8').replace('E041','E045').replace('runs/E045-final-build','runs/E045-final-build-r2').replace('gpu_control_report','numerical_control_report')
 # Replace only the declared historical numerical-control assertion.
 source_line=next(line for line in s.splitlines() if 'assert control[' in line)
 assert "control['raw_pairs']==68" in source_line and "control['raw_files']==160" in source_line
 prefix=source_line[:source_line.index('assert control[')]
 s=s.replace(source_line,prefix+current)
 (HERE/n).write_text(s,encoding='utf-8')
s=(ROOT/'runs/E042-primary-plan/root-check.py').read_text(encoding='utf-8').replace('E042','E045');(HERE/'root-check.py').write_text(s,encoding='utf-8')
p=old.read(ROOT/'runs/E041-primary-plan/protocol.json')
p.pop('gpu_control_report')
p.update(id='E045-primary',at=old.now(),build_protocol_sha256=old.sha(B/'build-protocol.json'),candidate_owned_sha256={n:x['candidate_sha256'] for n,x in old.read(D/'manifest.json')['owned'].items()},numerical_control_report={'path':str(C),'sha256':old.sha(C)},control_complete_path=str(C),control_ids=[],measurement_order=['B137','E045R1','E045R2','B138','B139','E045R3'],pairs=[{'baseline':'B137','candidate':'E045R1'},{'baseline':'B138','candidate':'E045R2'},{'baseline':'B139','candidate':'E045R3'}])
p['source_scope']='Only gpu/arena.rs. Exact complete signed/unsigned integer OR proof uses existing Rayon pool for >=2Miwords, fixed1Miword chunks. Scale-first, F32 and snapshot/inactive guards, all GPU/upload/readback arithmetic and allocation unchanged. Test-only copied original and fixed controls compile out of performance library.'
p['adoption_requirements'][-1]='No material resource/capacity/compatibility/behavior cost. Before adoption separately freeze matched whole-process CPU-time/peak-memory and responsiveness qualification; positive median CPU-time increase with strict majority paired increases disqualifies. Existing Rayon concurrency is a potential cost, not an assumed free speedup.'
paths=[HERE/n for n in ['native.py','assess.py','root-check.py']]+[C,D/'manifest.json',D/'source-review.json',D/'amendment.json',D/'production.patch',B/'build-protocol.json',F/'complete.json',F/'terminal.json',ROOT/'runs/E045-control-plan-r2/protocol.json',ROOT/'runs/V045-unit/report.json',ar.REPO/'tools/postflop_autoresearch.py',ar.REPO/'tools/postflop_compare.py',ar.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
for n in ['E045-solver','E045-postflop_autoresearch','SG-E020-postflop_autoresearch']:paths.extend([ROOT/'binaries'/(n+'.exe'),ROOT/'binaries'/(n+'.manifest.json')])
p['input_sha256']={str(x):old.sha(x) for x in paths}
status=old.read(ar.STATUS)
for identity in p['measurement_order']:assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in status['experiments'])
old.save(HERE/'protocol.json',p)
published={}
for directory in [HERE,D,B,F,ROOT/'runs/E045-control-plan-r2',C.parent,ROOT/'runs/V045-unit']:
 for source in directory.rglob('*'):
  if not source.is_file() or '__pycache__' in source.parts:continue
  key=directory.name+'/'+source.relative_to(directory).as_posix();target=ar.DASHBOARD/'evidence'/key;target.parent.mkdir(parents=True,exist_ok=True);raw=source.read_bytes()
  if target.exists():assert target.read_bytes()==raw
  else:target.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(source)
old.save(HERE/'pre-timing-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'performance_measured':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 status=old.read(ar.STATUS);e=next(x for x in status['experiments'] if x['id']=='E045');e.update(status='preparing',correctness='pass',stage='Controls passed; fixed primary screen next',reason='86 ordinary tests/4ignored,3516 exact raw integer comparisons across1/2/16-worker pools and576 full accepted-reference predicates passed. Input bits unchanged. Fixed3pair timing and later CPU/resource qualification remain pending.')
 e['evidence'].extend([{'label':'E045 native integer controls','url':'evidence/E045-control-execution/complete.json'},{'label':'E045 fixed primary protocol','url':'evidence/E045-primary-plan/protocol.json'}]);status.update(stage='E045 fixed primary screen',activity='Six frozen complete-cycle processes next;1% cutoff, strict fixture guard and no sample extensions.',updated_at=ar.now(),state='running');ar.atomic_json(ar.STATUS,status)
print(json.dumps({'protocol_sha256':old.sha(HERE/'protocol.json'),'http_verified_files':len(published)}),flush=True)
