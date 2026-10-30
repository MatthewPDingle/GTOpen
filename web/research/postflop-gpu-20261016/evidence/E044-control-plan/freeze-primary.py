"""Freeze E044's fixed primary screen after controls; publish byte-exact evidence."""
import json,sys,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
ROOT=old.ROOT;ar=old.ar;old.custody()
C=ROOT/'comparisons/E044-discount-control-r2/report.json'
c=old.read(C);assert c['status']=='pass_scoped_discount_gpu_lifecycle' and c['raw_pairs']==308 and c['raw_files']==630
D=ROOT/'runs/E044-design';B=ROOT/'runs/E044-build-plan';F=ROOT/'runs/E044-final-build'
PTH=ROOT/'runs/E044-primary-plan';assert not PTH.exists();PTH.mkdir()
for n in ['native.py','assess.py']:
 s=(ROOT/'runs/E041-primary-plan'/n).read_text(encoding='utf-8').replace('E041','E044')
 s=s.replace('pass_scoped_zero_restore_gpu_lifecycle','pass_scoped_discount_gpu_lifecycle')
 s=s.replace("['raw_pairs']==68","['raw_pairs']==308").replace("['raw_files']==160","['raw_files']==630")
 s=s.replace("['ordinary_tests_passed']==86","['ordinary_tests_passed']==84").replace("['unit_passed']==86","['unit_passed']==84")
 (PTH/n).write_text(s,encoding='utf-8')
s=(ROOT/'runs/E042-primary-plan/root-check.py').read_text(encoding='utf-8').replace('E042','E044')
(PTH/'root-check.py').write_text(s,encoding='utf-8')
p=old.read(ROOT/'runs/E041-primary-plan/protocol.json')
p.update(id='E044-primary',at=old.now(),build_protocol_sha256=old.sha(B/'build-protocol.json'),candidate_owned_sha256={n:x['candidate_sha256'] for n,x in old.read(D/'manifest.json')['owned'].items()},gpu_control_report={'path':str(C),'sha256':old.sha(C)},control_complete_path=str(ROOT/'runs/E044-control-execution/complete.json'),control_ids=[],measurement_order=['B134','E044R1','E044R2','B135','B136','E044R3'],pairs=[{'baseline':'B134','candidate':'E044R1'},{'baseline':'B135','candidate':'E044R2'},{'baseline':'B136','candidate':'E044R3'}])
p['source_scope']='Only gpu/mod.rs: two disjoint three-float windows of existing pinned staging, fixed reuse synchronization and first-field lifetime guard. Original CPU discounts/CUDA/plan/storage/graph shape unchanged. Tiny fallback remains pageable. Test-only controls compile out of performance library. No new pinned/device/event/stream/graph allocation; measured host object +16 bytes.'
p['adoption_requirements'][-1]='No material memory/capacity/compatibility/behavior costs. In addition to broader/holdout/cumulative checks, measure stop/drop responsiveness and full-process wall time because this mechanism changes queuing and first-field drain ownership.'
paths=[PTH/n for n in ['native.py','assess.py','root-check.py']]+[C,D/'manifest.json',D/'source-review.json',D/'production.patch',B/'build-protocol.json',F/'complete.json',F/'terminal.json',HERE/'protocol.json',HERE/'audit.py',HERE/'audit-r2.py',ROOT/'comparisons/E044-discount-control/failure.json',ROOT/'runs/E044-control-execution/complete.json',ROOT/'runs/V044-unit/report.json',ROOT/'runs/V044-discount-staging/report.json',ROOT/'runs/E044-control-raw/evidence.json',ar.REPO/'tools/postflop_autoresearch.py',ar.REPO/'tools/postflop_compare.py',ar.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
for name in ['E044-solver','E044-postflop_autoresearch','SG-E020-postflop_autoresearch']:
 paths.extend([ROOT/'binaries'/(name+'.exe'),ROOT/'binaries'/(name+'.manifest.json')])
p['input_sha256']={str(x):old.sha(x) for x in paths}
status=old.read(ar.STATUS)
for identity in p['measurement_order']:
 assert not (ROOT/'runs'/identity).exists() and not any(e['id']==identity for e in status['experiments'])
old.save(PTH/'protocol.json',p)
assert old.read(ROOT/'binaries/E044-postflop_autoresearch.manifest.json')['build_protocol_sha256']==p['build_protocol_sha256']
files={}
for directory in [PTH,D,B,F,HERE,ROOT/'runs/E044-control-execution',ROOT/'runs/V044-unit',ROOT/'runs/V044-discount-staging',ROOT/'runs/E044-control-raw',C.parent,ROOT/'comparisons/E044-discount-control']:
 for source in directory.rglob('*'):
  if not source.is_file() or '__pycache__' in source.parts:continue
  # Freeze/publication script is included, but its future receipt is not recursive.
  rel=source.relative_to(directory)
  key=directory.name+'/'+rel.as_posix();files[key]=source
published={}
for key,source in files.items():
 target=ar.DASHBOARD/'evidence'/key;target.parent.mkdir(parents=True,exist_ok=True)
 raw=source.read_bytes()
 if target.exists():assert target.read_bytes()==raw
 else:target.write_bytes(raw)
 url='http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key
 with urllib.request.urlopen(url,timeout=15) as response:assert response.read()==raw
 published[key]=old.sha(source)
old.save(PTH/'pre-timing-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'performance_measured':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);row=next(e for e in s['experiments'] if e['id']=='E044')
 row.update(status='preparing',correctness='pass',stage='Controls passed; fixed primary timing frozen',reason='84 ordinary tests;14 lifecycle cases/630 retained files/308 raw pairs; error/unwind/drop controls passed. Root observer epoch assertion repaired against unchanged raw data; failure preserved. Host object +16 bytes; no new GPU/pinned allocation. Timing and broader/resource qualification remain pending.')
 row['evidence']=[{'label':'E044 lifecycle raw cross-check','url':'evidence/E044-discount-control-r2/report.json'},{'label':'Preserved observer epoch failure','url':'evidence/E044-discount-control/failure.json'},{'label':'E044 frozen primary protocol','url':'evidence/E044-primary-plan/protocol.json'},{'label':'E044 source review','url':'evidence/E044-design/source-review.json'}]
 s.update(state='running',stage='E044 fixed primary screen',activity='Three paired full-cycle measurements next;1% cutoff and strict fixture guard; E020 retained.',updated_at=ar.now())
 ar.atomic_json(ar.STATUS,s)
print(json.dumps({'protocol_sha256':old.sha(PTH/'protocol.json'),'publication_sha256':old.sha(PTH/'pre-timing-publication.json'),'http_verified_files':len(published)}),flush=True)
