"""Freeze production-only E047 source after full raw GPU replay; no source activation here."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
CONTROL=ROOT/'comparisons/E047-kernel-control-r2/report.json';c=old.read(CONTROL)
assert c['status']=='pass_scoped_up_action_raw_equivalence' and c['cases']==819 and c['kernel_launches']==1638 and c['full_raw_files_equal']
K=ROOT/'runs/E047-kernel-control';D=ROOT/'runs/E047-final-source';D.mkdir();src=ROOT/'runs/E047-design'
for n,name in [('baseline.cu','base-kernels.cu'),('candidate.cu','candidate-kernels.cu'),('candidate.patch','candidate.patch')]:(D/name).write_bytes((src/n).read_bytes())
owned={'crates/solver/src/gpu/kernels.cu':{'base':str(D/'base-kernels.cu'),'base_sha256':old.sha(D/'base-kernels.cu'),'candidate':str(D/'candidate-kernels.cu'),'candidate_sha256':old.sha(D/'candidate-kernels.cu')}}
old.save(D/'manifest.json',{'id':'E047-final-source','at':old.now(),'accepted_source_sha256':old.BASE,'owned':owned,'raw_control_report_sha256':old.sha(CONTROL),'raw_control_protocol_sha256':old.sha(K/'protocol.json'),'raw_decoder_sha256':old.sha(K/'audit-r2.py'),'control_reporting_failure_sha256':old.sha(K/'execution/wrapper-failure.json'),'source_review_sha256':old.sha(ROOT/'runs/D077-one-action-source/report.json'),'candidate_accepted':False})
old.save(D/'source-review.json',{'id':'E047-final-source-review','at':old.now(),'status':'pass_to_fresh_compile_units_and_fixed_primary','root_review_only':True,'source_scope':'One existing training entry gains na==1 routing to unchanged helper<1>;2/3/4/generic code, all bodies/host/plan/stores/launches/buffers and other8 PTX entries unchanged.','compiled_resource_scope':'Same66registers/64local bytes,896 max threads and14/7/3 theoretical blocks at64/128/256. Same exact ABI. Module/code size and full-cycle behavior still need qualification.','raw_gpu_control':{'cases':819,'changed_path_cases':138,'kernel_launches':1638,'root_checks':56527,'raw_output_words':12375858,'actual_device_immutable_words':5199114,'guard_words':10240828,'all_raw_exact':True,'raw_files_retained':5},'reporting_failure':'Native comparator and all per-case assertions passed once, but final marker retained old717/1434 constants; wrapper rejected it. Original source/raw marker/failure retained. Root independently decoded all819 full records and exact EOF; only assessment totals corrected. No numerical mismatch, native rerun or corpus exclusion.','resource_root_check_sha256':old.sha(ROOT/'comparisons/E047-resource-root-check/report.json'),'control_report_sha256':old.sha(CONTROL),'ordinary_expected_passed':84,'ordinary_expected_ignored':4,'pending':['fresh feature/primary builds','ordinary84/4','fixed3pair1%/strict fixture screen','conditional fresh16pair/broader/holdout/cumulative/resource qualification'],'candidate_accepted':False})
HERE=ROOT/'runs/E047-build-plan';HERE.mkdir();oldbuild=ROOT/'runs/E044-build-plan'
(HERE/'build.py').write_text((oldbuild/'build.py').read_text(encoding='utf-8').replace('E044','E047'),encoding='utf-8')
p=old.read(oldbuild/'build-protocol.json');p.update(id='E047-final-build',at=old.now(),owned=owned)
for phase in p['phases']:phase['target']=phase['target'].replace('e044','e047');phase['outputs']={k:v.replace('E044','E047') for k,v in phase['outputs'].items()}
refs=[HERE/'build.py',D/'manifest.json',D/'source-review.json',D/'base-kernels.cu',D/'candidate-kernels.cu',CONTROL,K/'protocol.json',K/'execution/complete-r2.json',K/'execution/wrapper-failure.json',K/'audit-r2.py',ROOT/'runs/E047-resource/report.json',ROOT/'comparisons/E047-resource-root-check/report.json',Path(p['protected_main']),ROOT/'runs/small-gain-confirmation-plan/common.py',ar.REPO/'tools/postflop_autoresearch.py']
p['input_sha256']={str(x):old.sha(x) for x in refs};old.save(HERE/'build-protocol.json',p)
published={}
for directory in [D,HERE,K,CONTROL.parent]:
 for source in directory.rglob('*'):
  if not source.is_file() or '__pycache__' in source.parts:continue
  key=directory.name+'/'+source.relative_to(directory).as_posix();target=ar.DASHBOARD/'evidence'/key;target.parent.mkdir(parents=True,exist_ok=True);raw=source.read_bytes()
  if target.exists():assert target.read_bytes()==raw
  else:target.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(source)
old.save(HERE/'pre-compile-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'solver_executions':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);e=next(x for x in s['experiments'] if x['id']=='E047');e.update(stage='Raw GPU control passed; fresh feature/primary builds next',correctness='pass',reason='819 directGPU cases/1638launches exact, including138 changed-path cases. Root decoded all5 raw files/56527checks. Stale final summary counts corrected in assessment only; reporting failure retained. No speed measured.');e['evidence'].extend([{'label':'E047 full raw GPU control','url':'evidence/E047-kernel-control-r2/report.json'},{'label':'Preserved summary-count reporting failure','url':'evidence/E047-kernel-control/execution/wrapper-failure.json'},{'label':'E047 production source review','url':'evidence/E047-final-source/source-review.json'}]);s.update(state='running',stage='E047 fresh isolated builds',activity='Numerical control passed; feature/primary compilation precedes ordinary and complete-cycle tests.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
print(json.dumps({'source_manifest_sha256':old.sha(D/'manifest.json'),'build_protocol_sha256':old.sha(HERE/'build-protocol.json'),'published_files':len(published)}),flush=True)
