"""Pre-native caller-ID correction, preserving frozen R1 and its refused invocation."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
PRIOR=ROOT/'runs/E047-primary-plan';FAILED=ROOT/'runs/E047-native-execution';e=old.read(FAILED/'V042-unit.exit.json')
assert e['returncode']==1 and e['error'] is None and e['cleanup'] is None
assert 'Refused: Experiment ID already appears in dashboard: V042-unit' in (FAILED/'V042-unit.stderr.log').read_text(encoding='utf-8')
oldroot=old.read(ROOT/'comparisons/E042-root-crosscheck/report.json')
pins={p:h for p,h in oldroot['preserved_sha256'].items() if '/V042-unit/' in p.replace('\\','/')}
assert len(pins)>=2
for p,h in pins.items():old.pin(p,h)
status=old.read(ar.STATUS);P=old.read(PRIOR/'protocol.json')
for identity in P['control_ids']+P['measurement_order']:assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in status['experiments'])
old.save(FAILED/'admission-failure.json',{'at':old.now(),'status':'caller_used_stale_validation_id','wrapper_returncode':1,'planned_unit':'V047-unit','actual_refused_unit':'V042-unit','cause':'Replacing E042 did not replace V042 in two caller literals. ar rejected the already-recorded validation ID before native launch; planned IDs were unused.','old_V042_artifacts_still_exact':pins,'protocol_sha256':old.sha(PRIOR/'protocol.json'),'native_script_sha256':old.sha(PRIOR/'native.py'),'new_unit_or_benchmark_executions':0,'source_binary_controls_unchanged':True,'repair':'Read the sole control ID from protocol data, use a new output directory and re-freeze before any test. Same candidate/binaries and six still-unused measurement IDs.'})
HERE=ROOT/'runs/E047-primary-plan-r2';HERE.mkdir()
for n in ['native.py','assess.py','root-check.py']:
 s=(PRIOR/n).read_text(encoding='utf-8').replace('runs/E047-native-execution','runs/E047-native-execution-r2')
 if n=='native.py':
  assert s.count("'V042-unit'")==2
  s=s.replace("'V042-unit'","P['control_ids'][0]")
  s=s.replace("r,raw=run_one(P['control_ids'][0]", "assert P['control_ids']==['V047-unit']\nr,raw=run_one(P['control_ids'][0]")
 assert 'V042-unit' not in s
 (HERE/n).write_text(s,encoding='utf-8')
P.update(id='E047-primary-r2',at=old.now(),prior_pre_native_failure_sha256=old.sha(FAILED/'admission-failure.json'))
P['input_sha256']={p:h for p,h in P['input_sha256'].items() if not Path(p).is_relative_to(PRIOR)}
P['input_sha256']|={str(p):old.sha(p) for p in [HERE/'native.py',HERE/'assess.py',HERE/'root-check.py',FAILED/'admission-failure.json',PRIOR/'protocol.json',PRIOR/'native.py']}
old.save(HERE/'protocol.json',P)
published={}
for directory in [HERE,FAILED]:
 for src in directory.rglob('*'):
  if not src.is_file():continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);raw=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==raw
  else:dst.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(src)
old.save(HERE/'pre-timing-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'native_unit_or_benchmark_executions':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);row=next(x for x in s['experiments'] if x['id']=='E047');row.update(stage='R1 caller-ID refusal preserved; R2 fixed primary ready',reason='Stale validation ID was refused before any native test. R2 reads V047-unit from frozen protocol. Candidate/binaries/control evidence unchanged; six measurement IDs remain unused.');row['evidence'].extend([{'label':'Preserved pre-native caller-ID refusal','url':'evidence/E047-native-execution/admission-failure.json'},{'label':'E047 corrected frozen primary','url':'evidence/E047-primary-plan-r2/protocol.json'}]);s.update(state='running',stage='E047 ordinary and fixed primary R2',activity='Pre-native caller corrected; no test/benchmark sample yet.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
print(json.dumps({'protocol_sha256':old.sha(HERE/'protocol.json'),'failed_attempt_sha256':old.sha(FAILED/'admission-failure.json'),'old_validation_artifacts_verified':len(pins)}),flush=True)
