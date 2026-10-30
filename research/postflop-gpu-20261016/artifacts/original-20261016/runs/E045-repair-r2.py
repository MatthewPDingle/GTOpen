"""Test-only bounded usize-to-u64 constructor correction; preserve failed R1."""
import difflib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
F=ROOT/'runs/E045-final-build'
old.save(F/'terminal.json',{'at':old.now(),'session_id':42814,'returncode':1,'status':'failed_test_code_compile','feature_restoration_sha256':old.sha(F/'feature/restoration.json'),'primary_never_started':True,'native_executions':0,'accepted162_restored':True,'main_live_ptx_unchanged':True})
D=ROOT/'runs/E045-design-r2';D.mkdir();prior=ROOT/'runs/E045-design'
for n in ['base-arena.rs','production-arena.rs','production.patch']:(D/n).write_bytes((prior/n).read_bytes())
candidate=(prior/'candidate-arena.rs').read_text(encoding='utf-8');assert candidate.count('Store::i16(n,2)')==candidate.count('Store::u16(n,2)')==1
candidate=candidate.replace('Store::i16(n,2)','Store::i16(n as u64,2)').replace('Store::u16(n,2)','Store::u16(n as u64,2)')
(D/'candidate-arena.rs').write_text(candidate,encoding='utf-8');(D/'tests.rs').write_text(candidate[candidate.index('\n#[cfg(test)]\nmod e045_zero_proof_control'):],encoding='utf-8')
(D/'candidate.patch').write_text(''.join(difflib.unified_diff((D/'base-arena.rs').read_text(encoding='utf-8').splitlines(keepends=True),candidate.splitlines(keepends=True),fromfile='a/crates/solver/src/gpu/arena.rs',tofile='b/crates/solver/src/gpu/arena.rs')),encoding='utf-8')
assert (D/'production-arena.rs').read_bytes()==(prior/'production-arena.rs').read_bytes()
p=old.read(prior/'manifest.json');p.update(id='E045-source-r2',at=old.now())
for x in p['owned'].values():x.update(base=str(D/'base-arena.rs'),candidate=str(D/'candidate-arena.rs'),candidate_sha256=old.sha(D/'candidate-arena.rs'))
old.save(D/'manifest.json',p)
old.save(D/'amendment.json',{'at':old.now(),'status':'test_only_compile_correction','failed_terminal_sha256':old.sha(F/'terminal.json'),'prior_source_manifest_sha256':old.sha(prior/'manifest.json'),'change':'Two test Store constructors require u64; cast bounded test n (maximum3*2^20+17) from usize. Production bytes unchanged.','production_sha256':old.sha(D/'production-arena.rs'),'native_or_timing_runs':0})
review=old.read(prior/'source-review.json');review.update(id='E045-source-review-r2',at=old.now(),source_manifest_sha256=old.sha(D/'manifest.json'),test_only_amendment_sha256=old.sha(D/'amendment.json'));old.save(D/'source-review.json',review)
B=ROOT/'runs/E045-build-plan-r2';B.mkdir()
s=(ROOT/'runs/E045-build-plan/build.py').read_text(encoding='utf-8').replace("runs/E045-final-build","runs/E045-final-build-r2");(B/'build.py').write_text(s,encoding='utf-8')
bp=old.read(ROOT/'runs/E045-build-plan/build-protocol.json');bp.update(id='E045-final-build-r2',at=old.now(),owned=p['owned'])
for phase in bp['phases']:phase['target']+='-r2'
inputs=[B/'build.py',D/'manifest.json',D/'source-review.json',D/'amendment.json',D/'base-arena.rs',D/'candidate-arena.rs',ROOT/'runs/D075-zero-proof-parallel-source/report.json',F/'terminal.json',ROOT/'runs/small-gain-confirmation-plan/common.py',Path(bp['protected_main']),ar.REPO/'tools/postflop_autoresearch.py']
bp['input_sha256']={str(x):old.sha(x) for x in inputs};old.save(B/'build-protocol.json',bp)
C=ROOT/'runs/E045-control-plan-r2';C.mkdir()
s=(ROOT/'runs/E045-control-plan/execute.py').read_text(encoding='utf-8').replace('runs/E045-final-build','runs/E045-final-build-r2')
(C/'execute.py').write_text(s,encoding='utf-8')
cp=old.read(ROOT/'runs/E045-control-plan/protocol.json');cp.update(id='E045-controls-r2',at=old.now(),source_manifest=str(D/'manifest.json'),build_protocol_sha256=old.sha(B/'build-protocol.json'))
cp['input_sha256']={str(x):old.sha(x) for x in [C/'execute.py',D/'manifest.json',D/'source-review.json',D/'candidate-arena.rs',B/'build-protocol.json',ROOT/'runs/small-gain-confirmation-plan/common.py',ar.REPO/'tools/postflop_autoresearch.py']};old.save(C/'protocol.json',cp)
published={}
for directory in [D,B,C,F]:
 for source in directory.rglob('*'):
  if not source.is_file() or '__pycache__' in source.parts:continue
  key=directory.name+'/'+source.relative_to(directory).as_posix();target=ar.DASHBOARD/'evidence'/key;target.parent.mkdir(parents=True,exist_ok=True);raw=source.read_bytes()
  if target.exists():assert target.read_bytes()==raw
  else:target.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(source)
old.save(B/'publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'native_executions':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 status=old.read(ar.STATUS);e=next(x for x in status['experiments'] if x['id']=='E045');e.update(stage='R1 test compile failure preserved; R2 fresh compile next');e['evidence'].append({'label':'Preserved R1 failure and test-only correction','url':'evidence/E045-design-r2/amendment.json'});status['updated_at']=ar.now();ar.atomic_json(ar.STATUS,status)
print(json.dumps({'candidate_sha256':old.sha(D/'candidate-arena.rs'),'manifest_sha256':old.sha(D/'manifest.json'),'build_protocol_sha256':old.sha(B/'build-protocol.json'),'control_protocol_sha256':old.sha(C/'protocol.json')}))
