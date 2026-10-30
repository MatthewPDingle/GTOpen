"""Freeze E049 three-pair screen after terminal ordinary/provenance controls."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E049-final-source';B=ROOT/'runs/E049-build-plan';F=ROOT/'runs/E049-final-build';C=ROOT/'runs/E049-controls-execution/complete.json'
control=old.read(C);assert control['status']=='pass_provenance_controls' and control['predicate_comparisons']==5600
assert control['cpu_only_ordinary_passed'] and control['gpu_ordinary_passed']
assert old.read(C.parent/'terminal.json')['returncode']==0 and old.read(F/'terminal.json')['returncode']==0
HERE=ROOT/'runs/E049-primary-plan';HERE.mkdir();PRIOR=ROOT/'runs/E048-primary-plan'
for n in ['native.py','assess.py','root-check.py']:
 s=(PRIOR/n).read_text(encoding='utf-8').replace('E048','E049').replace('gpu_control_report','controls_report')
 s=s.replace("control['status']=='pass_scoped_chance_raw_equivalence' and control['cases']==425 and control['full_raw_files_equal']","control['status']=='pass_provenance_controls' and control['predicate_comparisons']==5600 and control['cpu_only_ordinary_passed'] and control['gpu_ordinary_passed']")
 if n=='native.py':
  start=s.index("assert len(P['control_ids'])==1")
  end=s.index("baseline=P['baseline_binary']",start)
  s=s[:start]+"assert P['control_ids']==[]\nsave(OUT/'controls-complete.json',{'at':now(),'previously_terminal_controls_sha256':sha(Path(P['controls_report']['path'])),'all_passed':True,'no_reexecution':True})\n"+s[end:]
  s=s.replace('E049 ordinary units then one fixed3-pair','E049 previously terminal controls then one fixed3-pair')
 assert 'V048' not in s and 'E048' not in s and 'pass_scoped_chance' not in s
 (HERE/n).write_text(s,encoding='utf-8')
p=old.read(PRIOR/'protocol.json')
for k in ['gpu_control_report','ordinary_unit_id']:p.pop(k,None)
p.update(id='E049-primary',at=old.now(),build_protocol_sha256=old.sha(B/'build-protocol.json'),candidate_owned_sha256={n:x['candidate_sha256'] for n,x in old.read(D/'manifest.json')['owned'].items()},controls_report={'path':str(C),'sha256':old.sha(C)},control_ids=[],previously_terminal_control_ids=['V049-cpu','V049-unit'],measurement_order=['B146','E049R1','E049R2','B147','B148','E049R3'],pairs=[{'baseline':'B146','candidate':'E049R1'},{'baseline':'B147','candidate':'E049R2'},{'baseline':'B148','candidate':'E049R3'}])
p['source_scope']='Two files: GPU-only ArenaBuf provenance metadata, conservative invalidation before every borrowed/mutable exposure, and i16/u16 zero-upload OR-scan shortcut for unexposed default owners. Existing scale bits, snapshots, fallback, CPU arithmetic, GPU kernels and evaluator unchanged.'
p['adoption_requirements'][-1]='No material resource/capacity/compatibility/behavior cost. Require matched compressed CPU solve/encoding and warm constructor measurements, actual metadata and final-artifact F32/CPU-only code, full process wall including teardown/first-touch, saves/load/resume/continuation. Repeatable CPU slowdown disqualifies. Initial timing cannot adopt.'
paths=[HERE/n for n in ['native.py','assess.py','root-check.py']]+[C,C.parent/'terminal.json',ROOT/'runs/E049-control-plan/protocol.json',D/'manifest.json',D/'source-review.json',B/'build-protocol.json',F/'complete.json',F/'terminal.json',ROOT/'runs/D079-initial-zero-provenance/report.json',ar.REPO/'tools/postflop_autoresearch.py',ar.REPO/'tools/postflop_compare.py',ar.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
for n in ['E049-solver','E049-postflop_autoresearch','SG-E020-postflop_autoresearch']:paths.extend([ROOT/'binaries'/(n+'.exe'),ROOT/'binaries'/(n+'.manifest.json')])
for identity in p['previously_terminal_control_ids']:
 paths.extend([ROOT/'runs'/identity/'report.json',ROOT/'runs'/identity/'stdout.log'])
p['input_sha256']={str(x):old.sha(x) for x in paths}
status=old.read(ar.STATUS)
for identity in p['measurement_order']:assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in status['experiments'])
old.save(HERE/'protocol.json',p)
published={}
for directory in [HERE,C.parent]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(HERE/'pre-timing-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'performance_measured':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E049');e.update(stage='Controls passed; fixed primary next',reason='CPU-only and GPU ordinary suites terminal; 5600 predicate comparisons and no-scan witnesses passed. One fixed3-pair complete-cycle screen, 1% and strict fixture guard, no adoption.');e['evidence'].append({'label':'E049 fixed primary protocol','url':'evidence/E049-primary-plan/protocol.json'});st.update(state='running',stage='E049 fixed primary',activity='B146/E049R1/E049R2/B147/B148/E049R3 once; E020 retained.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(HERE/'protocol.json'),'published':len(published)}),flush=True)
